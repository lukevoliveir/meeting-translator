import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from conftest import FRONTEND_URL, navigate_to_call


class TestLanguageSelector:
    """Language selection screen."""

    def test_page_loads(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        title = browser.find_element(By.CLASS_NAME, "ls-title")
        assert "Meeting Translator" in title.text

    def test_language_list_displays(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        items = browser.find_elements(By.CLASS_NAME, "ls-item")
        assert len(items) >= 3, f"Expected at least 3 language items, got {len(items)}"

    def test_select_language(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        first_item = browser.find_elements(By.CLASS_NAME, "ls-item")[0]
        first_item.click()
        time.sleep(0.5)
        assert "ls-item--selected" in first_item.get_attribute("class")

    def test_next_button_enabled(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        next_btn = browser.find_element(By.CLASS_NAME, "ls-btn-primary")
        assert next_btn.is_enabled()

    def test_language_items_have_flag_and_name(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        flags = browser.find_elements(By.CLASS_NAME, "ls-flag")
        names = browser.find_elements(By.CLASS_NAME, "ls-name")
        assert len(flags) >= 3
        assert len(names) >= 3


class TestSpeakerProfile:
    """Speaker profile setup screen."""

    def test_navigate_to_profile_screen(self, browser, frontend_service, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-page")))
        title = browser.find_element(By.CLASS_NAME, "sp-title")
        assert "Perfil" in title.text

    def test_profile_form_displays(self, browser, frontend_service, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-page")))
        assert browser.find_element(By.CLASS_NAME, "sp-input")
        assert browser.find_element(By.CLASS_NAME, "sp-url-input")
        assert browser.find_element(By.CLASS_NAME, "sp-btn-skip")

    def test_skip_button_navigates_to_call(self, browser, frontend_service, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-btn-skip")))
        browser.find_element(By.CLASS_NAME, "sp-btn-skip").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))

    def test_add_url_button_exists(self, browser, frontend_service, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-btn-add")))
        add_btn = browser.find_element(By.CLASS_NAME, "sp-btn-add")
        assert add_btn.is_displayed()

    def test_name_input_accepts_text(self, browser, frontend_service, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-input")))
        name_input = browser.find_element(By.CLASS_NAME, "sp-input")
        name_input.send_keys("Test Speaker")
        assert name_input.get_attribute("value") == "Test Speaker"

    def test_url_input_accepts_url(self, browser, frontend_service, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-url-input")))
        url_input = browser.find_element(By.CLASS_NAME, "sp-url-input")
        url_input.send_keys("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert "youtube" in url_input.get_attribute("value")


class TestCallOverlay:
    """Live call overlay screen."""

    def test_navigate_to_call_screen(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))

    def test_connection_dot_exists(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))
        dot = browser.find_element(By.CLASS_NAME, "co-dot")
        assert dot.is_displayed()

    def test_caption_area_exists(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))
        caption = browser.find_element(By.CLASS_NAME, "co-caption")
        assert caption.is_displayed()

    def test_exit_button_exists(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))
        exit_btn = browser.find_element(By.CLASS_NAME, "co-exit-btn")
        assert exit_btn.is_displayed()
        assert exit_btn.is_enabled()

    def test_exit_modal_appears(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        browser.find_element(By.CLASS_NAME, "co-exit-btn").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-modal")))
        modal = browser.find_element(By.CLASS_NAME, "co-modal")
        assert modal.is_displayed()
        end_btn = browser.find_element(By.CLASS_NAME, "co-modal-end")
        assert "Encerrar" in end_btn.text

    def test_exit_modal_cancel(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        browser.find_element(By.CLASS_NAME, "co-exit-btn").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-modal-continue")))
        browser.find_element(By.CLASS_NAME, "co-modal-continue").click()
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "co-modal")))
        # Overlay bar should still be visible after cancelling
        assert browser.find_element(By.CLASS_NAME, "co-bar").is_displayed()


class TestSessionSummary:
    """Session summary screen."""

    def _go_to_summary(self, browser, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        browser.find_element(By.CLASS_NAME, "co-exit-btn").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-modal-end")))
        browser.find_element(By.CLASS_NAME, "co-modal-end").click()

    def test_session_summary_after_end(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-page")))
        title = browser.find_element(By.CLASS_NAME, "ss-title")
        assert "Resumo" in title.text

    def test_summary_has_stats(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-page")))
        stat_values = browser.find_elements(By.CLASS_NAME, "ss-stat-value")
        assert len(stat_values) >= 3, f"Expected at least 3 stat values, got {len(stat_values)}"

    def test_summary_has_new_session_button(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-page")))
        new_session_btn = browser.find_element(By.CLASS_NAME, "ss-btn-primary")
        assert new_session_btn.is_displayed()
        assert new_session_btn.is_enabled()

    def test_new_session_restarts_to_language_selector(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-btn-primary")))
        browser.find_element(By.CLASS_NAME, "ss-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ls-page")))
        assert browser.find_element(By.CLASS_NAME, "ls-title").is_displayed()

    def test_summary_phrases_section_conditional(self, browser, frontend_service, wait):
        # ss-phrases is only rendered when recent_phrases.length > 0 (no audio in tests)
        self._go_to_summary(browser, wait)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-page")))
        sections = browser.find_elements(By.CLASS_NAME, "ss-phrases")
        if sections:
            assert sections[0].is_displayed()
        # Absence is also valid — no audio was captured during the test session


class TestFullUserJourney:
    """Complete user journey integration tests."""

    def test_journey_language_to_call(self, browser, frontend_service, wait):
        # Step 1: App loads on language selector
        browser.get(FRONTEND_URL)
        time.sleep(2)
        assert "Meeting Translator" in browser.find_element(By.CLASS_NAME, "ls-title").text

        # Step 2: Select first available language
        items = browser.find_elements(By.CLASS_NAME, "ls-item")
        items[0].click()
        assert "ls-item--selected" in items[0].get_attribute("class")

        # Step 3: Navigate to profile screen
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-page")))

        # Step 4: Skip profile → call overlay
        browser.find_element(By.CLASS_NAME, "sp-btn-skip").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))
        assert browser.find_element(By.CLASS_NAME, "co-bar").is_displayed()
        print("✓ Language → Profile → Call journey passed")

    def test_full_journey_to_summary_and_restart(self, browser, frontend_service, wait):
        # Language selector
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()

        # Skip profile
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-btn-skip")))
        browser.find_element(By.CLASS_NAME, "sp-btn-skip").click()

        # Exit call
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        browser.find_element(By.CLASS_NAME, "co-exit-btn").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-modal-end")))
        browser.find_element(By.CLASS_NAME, "co-modal-end").click()

        # Session summary
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-page")))
        assert "Resumo" in browser.find_element(By.CLASS_NAME, "ss-title").text

        # Restart
        browser.find_element(By.CLASS_NAME, "ss-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ls-page")))
        assert browser.find_element(By.CLASS_NAME, "ls-title").is_displayed()
        print("✓ Full journey language → call → summary → restart passed")
