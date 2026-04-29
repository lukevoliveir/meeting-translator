"""Build script for creating standalone executables for Windows and macOS."""

import platform
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd: list) -> bool:
    """
    Execute a shell command.

    Args:
        cmd: Command as list of strings

    Returns:
        True if successful, False otherwise
    """
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Comando não encontrado: {e}")
        return False


def build_windows() -> bool:
    """
    Build Windows executable using PyInstaller.

    Returns:
        True if build successful
    """
    print("\n" + "=" * 60)
    print("🔨 Compilando para Windows (.exe)")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("⚠️  PyInstaller não encontrado. Instalando...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Run PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico",
        "--name=MeetingTranslator",
        "--add-data=assets:assets",
        "main.py"
    ]

    print(f"\n📦 Executando: {' '.join(cmd)}")
    if run_command(cmd):
        exe_path = Path("dist/MeetingTranslator.exe")
        if exe_path.exists():
            print(f"\n✅ Build concluído com sucesso!")
            print(f"📍 Executável: {exe_path.absolute()}")
            print(f"📊 Tamanho: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            print("\n💡 Nota: O modelo Whisper (~1.5 GB) será baixado na primeira execução.")
            return True
    return False


def build_macos() -> bool:
    """
    Build macOS app bundle using py2app.

    Returns:
        True if build successful
    """
    print("\n" + "=" * 60)
    print("🔨 Compilando para macOS (.dmg)")
    print("=" * 60)

    # Check if py2app is installed
    try:
        import py2app
    except ImportError:
        print("⚠️  py2app não encontrado. Instalando...")
        run_command([sys.executable, "-m", "pip", "install", "py2app"])

    # Create setup.py for py2app
    setup_content = """
from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyInstaller', 'pystray', 'PIL', 'pynput', 'librosa', 'numpy', 'torch', 'whisper'],
    'resources': ['assets'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
"""

    with open("setup.py", "w") as f:
        f.write(setup_content)

    # Run py2app
    print(f"\n📦 Executando: python setup.py py2app")
    if run_command([sys.executable, "setup.py", "py2app"]):
        app_path = Path("dist/MeetingTranslator.app")

        if app_path.exists():
            print(f"\n✅ App bundle criado com sucesso!")
            print(f"📍 App: {app_path.absolute()}")

            # Create DMG
            print(f"\n📦 Criando DMG...")
            dmg_cmd = [
                "hdiutil",
                "create",
                "-volname", "MeetingTranslator",
                "-srcfolder", str(app_path.parent),
                "-ov",
                "-format", "UDZO",
                "dist/MeetingTranslator.dmg"
            ]

            if run_command(dmg_cmd):
                dmg_path = Path("dist/MeetingTranslator.dmg")
                if dmg_path.exists():
                    print(f"✅ DMG criado com sucesso!")
                    print(f"📍 DMG: {dmg_path.absolute()}")
                    print(f"📊 Tamanho: {dmg_path.stat().st_size / 1024 / 1024:.1f} MB")
                    print("\n💡 Nota: O modelo Whisper (~1.5 GB) será baixado na primeira execução.")
                    return True

    return False


def build_linux() -> None:
    """Build for Linux (use run.sh instead)."""
    print("\n" + "=" * 60)
    print("🐧 Linux - Use run.sh")
    print("=" * 60)
    print("\nPara usar no Linux:")
    print("  ./install.sh    # Instala dependências")
    print("  ./run.sh        # Executa a aplicação")


def main() -> None:
    """Main build orchestrator."""
    print("\n🎬 Meeting Translator - Build Script\n")

    system = platform.system()

    if system == "Windows":
        success = build_windows()
    elif system == "Darwin":  # macOS
        success = build_macos()
    elif system == "Linux":
        build_linux()
        success = True
    else:
        print(f"❌ Sistema operacional não suportado: {system}")
        success = False

    if success:
        print("\n" + "=" * 60)
        print("🎉 Build finalizado com sucesso!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Build falhou")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
