"""Janela de overlay flutuante com ícone na bandeja do sistema."""

import platform
import threading
import tkinter as tk
from typing import Optional, Callable
from datetime import datetime

from PIL import Image, ImageDraw

_IS_MACOS = platform.system() == "Darwin"

# pynput e pystray usam AppKit no macOS, o que causa crash quando rodado
# junto com Tkinter (conflito de thread TIS/TSM). Importar apenas em
# plataformas que não são macOS.
if not _IS_MACOS:
    from pynput import keyboard
    from pystray import Icon, Menu, MenuItem


# Mapeamento de bandeira por código de idioma
LANGUAGE_FLAGS = {
    "pt": "🇧🇷",
    "en": "🇺🇸",
    "es": "🇪🇸",
    "fr": "🇫🇷",
    "de": "🇩🇪",
    "it": "🇮🇹",
    "ja": "🇯🇵",
    "ko": "🇰🇷",
    "zh": "🇨🇳",
    "ru": "🇷🇺",
    "ar": "🇸🇦",
    "hi": "🇮🇳",
}


class OverlayWindow:
    """Janela de overlay flutuante para exibir legendas traduzidas."""

    def __init__(self, on_close: Optional[Callable] = None):
        """
        Inicializa a janela de overlay.

        Args:
            on_close: Callback chamado quando o usuário clica no botão ✕
        """
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.85)
        self.root.attributes("-topmost", True)

        # Dimensões da tela
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.root.configure(bg="#000000")

        # Frame principal
        self.frame = tk.Frame(self.root, bg="#000000")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Label de texto (lado esquerdo)
        self.label = tk.Label(
            self.frame,
            text="Aguardando áudio...",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#000000",
            wraplength=720,
            justify=tk.CENTER,
            padx=20,
            pady=20,
        )
        self.label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Botão fechar (lado direito)
        self.on_close_callback = on_close
        self.close_btn = tk.Button(
            self.frame,
            text="✕",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#000000",
            highlightbackground="#000000",
            activebackground="#333333",
            bd=0,
            padx=5,
            pady=5,
            cursor="hand2",
            command=self._on_close_click,
        )
        self.close_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Posiciona na parte inferior central
        self._position_window()

        # Bind para arrastar
        self.label.bind("<Button-1>", self._start_drag)
        self.label.bind("<B1-Motion>", self._drag)
        self.frame.bind("<Button-1>", self._start_drag)
        self.frame.bind("<B1-Motion>", self._drag)

        self.is_visible = True
        self._hidden = False

        # Estado do texto atual
        self.current_text = ""
        self.current_lang = ""

        # Rastreamento de sessão
        self.session_start_time = datetime.now()
        self.phrase_count = 0
        self.speaker_profile_active = False

        # Listener de teclado (desativado no macOS)
        self.listener = None

        # Ícone na bandeja (desativado no macOS — AppKit exige thread principal)
        self.tray_icon = None
        if not _IS_MACOS:
            self._setup_tray()

    def _position_window(self) -> None:
        """Posiciona a janela na parte inferior central da tela."""
        window_width = 800
        window_height = 100
        x = (self.screen_width - window_width) // 2
        y = self.screen_height - window_height - 30
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _start_drag(self, event) -> None:
        """Inicia o arrasto da janela."""
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()

    def _drag(self, event) -> None:
        """Movimenta a janela durante o arrasto."""
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def _setup_tray(self) -> None:
        """Configura o ícone na bandeja do sistema (somente Windows/Linux)."""
        icon_image = self._create_icon_image()
        menu = Menu(
            MenuItem("Mostrar/Ocultar", self._toggle_visibility_from_tray),
            MenuItem("Sobre", self._show_about),
            MenuItem("Sair", self._exit_app),
        )
        self.tray_icon = Icon(
            "meeting-translator",
            icon_image,
            menu=menu,
            title="Tradutor de Reuniões",
        )

    def _create_icon_image(self) -> Image.Image:
        """Cria imagem simples para o ícone da bandeja."""
        size = (64, 64)
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([10, 10, 54, 54], fill=(52, 152, 219), outline=(41, 128, 185))
        draw.text((28, 26), "MT", fill=(255, 255, 255), anchor="mm")
        return image

    def _toggle_visibility_from_tray(self, icon, item) -> None:
        """Alterna visibilidade a partir do menu da bandeja (thread-safe)."""
        self.toggle_visibility()

    def _show_about(self, icon, item) -> None:
        """Exibe informações sobre o app."""
        print("Tradutor de Reuniões em Tempo Real — Versão 1.0")

    def _exit_app(self, icon, item) -> None:
        """Encerra o app a partir da bandeja (thread-safe)."""
        self.root.after(0, self.root.quit)

    def _setup_keyboard_listener(self) -> None:
        """Configura listener global de teclado para atalho Alt+T (não macOS)."""
        if _IS_MACOS:
            return

        def on_press(key):
            try:
                if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self._alt_pressed = True
                elif hasattr(key, "char") and key.char == "t":
                    if getattr(self, "_alt_pressed", False):
                        self.toggle_visibility()
            except AttributeError:
                pass

        def on_release(key):
            try:
                if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                    self._alt_pressed = False
            except AttributeError:
                pass

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def start(self) -> None:
        """Inicia a janela de overlay e o ícone da bandeja."""
        self._setup_keyboard_listener()

        if not _IS_MACOS and self.tray_icon:
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()

        self.label.bind("<Button-3>", self._show_context_menu)
        self.root.mainloop()

    def _show_context_menu(self, event) -> None:
        """Exibe menu de contexto ao clicar com botão direito."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Mostrar/Ocultar", command=self.toggle_visibility)
        menu.add_separator()
        menu.add_command(label="Sair", command=self.root.quit)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def toggle_visibility(self) -> None:
        """Alterna visibilidade da janela (thread-safe via root.after)."""
        def _toggle():
            if self._hidden:
                self.root.deiconify()
                self._hidden = False
            else:
                self.root.withdraw()
                self._hidden = True
        self.root.after(0, _toggle)

    def update_text(self, text: str, lang: str) -> None:
        """
        Atualiza o texto do overlay de forma thread-safe.

        Args:
            text: Texto a exibir.
            lang: Código do idioma (ISO 639-1).
        """
        self.current_text = text
        self.current_lang = lang

        def update():
            if text and text.strip():
                flag = LANGUAGE_FLAGS.get(lang, "🌐")
                self.label.config(text=f"{flag} {text}")
            else:
                self.label.config(text="Aguardando áudio...")

        self.root.after(0, update)

    def _on_close_click(self) -> None:
        """Trata clique no botão ✕ — chama callback se definido."""
        if self.on_close_callback:
            self.on_close_callback()
        else:
            self.root.quit()

    def set_speaker_profile_active(self, active: bool) -> None:
        """
        Define indicador de perfil de falante ativo.

        Args:
            active: True se um perfil está sendo usado
        """
        self.speaker_profile_active = active

    def increment_phrase_count(self) -> None:
        """Incrementa o contador de frases traduzidas."""
        self.phrase_count += 1

    def get_session_stats(self) -> dict:
        """
        Retorna estatísticas da sessão atual.

        Returns:
            Dicionário com start_time, elapsed_minutes, phrase_count, speaker_profile_active
        """
        elapsed = datetime.now() - self.session_start_time
        return {
            "start_time": self.session_start_time,
            "elapsed_minutes": int(elapsed.total_seconds() / 60),
            "phrase_count": self.phrase_count,
            "speaker_profile_active": self.speaker_profile_active,
        }

    def get_position(self) -> tuple:
        """
        Retorna a posição atual da janela.

        Returns:
            Tupla (x, y)
        """
        return (self.root.winfo_x(), self.root.winfo_y())

    def set_position(self, x: int, y: int) -> None:
        """
        Define a posição da janela.

        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        self.root.geometry(f"+{x}+{y}")

    def destroy(self) -> None:
        """Encerra e destrói a janela de forma segura."""
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        try:
            self.root.destroy()
        except tk.TclError:
            pass
