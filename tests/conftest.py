import pytest
import time
import subprocess
import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import socket

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@pytest.fixture(scope="session")
def backend_service():
    print("\n🚀 Starting backend service...")

    if port_in_use(BACKEND_PORT):
        print(f"⚠️  Port {BACKEND_PORT} already in use, assuming backend is running")
        yield
        return

    backend_dir = PROJECT_ROOT / "backend"
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    for _ in range(10):
        if port_in_use(BACKEND_PORT):
            print("✓ Backend is running")
            break
        time.sleep(1)
    else:
        process.kill()
        raise RuntimeError("Backend service failed to start within 10 seconds")

    yield

    print("\n🛑 Stopping backend service...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="session")
def frontend_service():
    print("\n🎨 Starting frontend service...")

    if port_in_use(FRONTEND_PORT):
        print(f"⚠️  Port {FRONTEND_PORT} already in use, assuming frontend is running")
        yield
        return

    frontend_dir = PROJECT_ROOT / "frontend"

    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)

    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Vite takes a few seconds to compile on first run
    for _ in range(15):
        if port_in_use(FRONTEND_PORT):
            print("✓ Frontend is running")
            break
        time.sleep(1)
    else:
        process.kill()
        raise RuntimeError("Frontend service failed to start within 15 seconds")

    yield

    print("\n🛑 Stopping frontend service...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture
def browser():
    print("\n🌐 Starting browser...")

    options = Options()
    # options.add_argument("--headless")  # Uncomment for headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Selenium 4.6+ has selenium-manager built in — no webdriver_manager needed
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    yield driver

    print("\n🔒 Closing browser...")
    driver.quit()


@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 10)


def screenshot_on_failure(driver, test_name):
    reports_dir = PROJECT_ROOT / "tests" / "reports" / "screenshots"
    reports_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = reports_dir / f"{test_name}_failure.png"
    driver.save_screenshot(str(screenshot_path))
    print(f"\n📸 Screenshot saved: {screenshot_path}")


@pytest.fixture(autouse=True)
def test_failure_handler(request):
    yield
    failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    if failed:
        try:
            driver = request.getfixturevalue("browser")
            screenshot_on_failure(driver, request.node.name)
        except pytest.FixtureLookupError:
            pass  # test didn't use a browser fixture


def navigate_to_call(driver):
    """Helper: language selector → skip profile → call overlay."""
    driver.get(FRONTEND_URL)
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, "ls-btn-primary").click()
    time.sleep(1)
    driver.find_element(By.CLASS_NAME, "sp-btn-skip").click()
    time.sleep(1)
