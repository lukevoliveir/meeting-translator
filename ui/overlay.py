"""Floating overlay window with system tray integration."""

import platform
import threading
import tkinter as tk
from typing import Optional

from PIL import Image, ImageDraw
from pynput import keyboard
from pystray import Icon, Menu, MenuItem


# Language flag emoji mapping
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
    """Floating overlay window for displaying translated captions."""

    def __init__(self):
        """Initialize the overlay window."""
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.85)
        self.root.attributes("-topmost", True)

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Create main frame with semi-transparent background
        self.root.configure(bg="#000000")

        # Create label for text display
        self.label = tk.Label(
            self.root,
            text="Aguardando áudio...",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#000000",
            wraplength=780,
            justify=tk.CENTER,
            padx=20,
            pady=20,
        )
        self.label.pack()

        # Position at bottom center
        self._position_window()

        # Bind dragging
        self.label.bind("<Button-1>", self._start_drag)
        self.label.bind("<B1-Motion>", self._drag)

        # Keyboard shortcut listener
        self.listener: Optional[keyboard.Listener] = None
        self.is_visible = True

        # Current text state
        self.current_text = ""
        self.current_lang = ""

        # Tray icon
        self.tray_icon: Optional[Icon] = None
        self._setup_tray()

        # Flag to track if we're currently hidden
        self._hidden = False

    def _position_window(self) -> None:
        """Position window at bottom center of screen."""
        window_width = 800
        window_height = 100
        x = (self.screen_width - window_width) // 2
        y = self.screen_height - window_height - 30

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _start_drag(self, event):
        """Start dragging the window."""
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()

    def _drag(self, event):
        """Handle window dragging."""
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def _setup_tray(self) -> None:
        """Setup system tray icon and menu."""
        # Create a simple icon image
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
        """Create a simple icon image for the system tray."""
        size = (64, 64)
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw a simple circle with "MT" text
        draw.ellipse([10, 10, 54, 54], fill=(52, 152, 219), outline=(41, 128, 185))
        draw.text((28, 26), "MT", fill=(255, 255, 255), anchor="mm")

        return image

    def _toggle_visibility_from_tray(self, icon, item) -> None:
        """Toggle visibility from tray menu."""
        self.toggle_visibility()

    def _show_about(self, icon, item) -> None:
        """Show about dialog."""
        about_text = (
            "Tradutor de Reuniões em Tempo Real\n"
            "Versão 1.0\n\n"
            "Captura e traduz áudio em tempo real\n"
            "para suas reuniões online."
        )
        print(f"About: {about_text}")

    def _exit_app(self, icon, item) -> None:
        """Exit the application."""
        self.root.quit()

    def _setup_keyboard_listener(self) -> None:
        """Setup global keyboard listener for Alt+T shortcut."""
        def on_press(key):
            try:
                # Check for Alt+T combination
                if hasattr(key, "char"):
                    if (
                        key == keyboard.Key.alt_l or key == keyboard.Key.alt_r
                    ) and hasattr(self, "_alt_pressed"):
                        self._alt_pressed = True
                elif hasattr(key, "name"):
                    if key.name == "t" and hasattr(self, "_alt_pressed") and self._alt_pressed:
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
        """Start the overlay window and tray icon."""
        # Setup keyboard listener
        self._setup_keyboard_listener()

        # Start tray icon in a separate thread
        if self.tray_icon:
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()

        # Right-click binding for context menu
        self.label.bind("<Button-3>", self._show_context_menu)

        # Start tkinter main loop
        self.root.mainloop()

    def _show_context_menu(self, event) -> None:
        """Show context menu on right-click."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Mostrar/Ocultar", command=self.toggle_visibility)
        menu.add_command(label="Sobre", command=lambda: print("About clicked"))
        menu.add_separator()
        menu.add_command(label="Sair", command=self.root.quit)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def toggle_visibility(self) -> None:
        """Toggle window visibility."""
        if self._hidden:
            self.root.deiconify()
            self._hidden = False
        else:
            self.root.withdraw()
            self._hidden = True

    def update_text(self, text: str, lang: str) -> None:
        """
        Update the overlay text in a thread-safe manner.

        Args:
            text: Text to display.
            lang: Language code for the text (ISO 639-1).
        """
        self.current_text = text
        self.current_lang = lang

        def update():
            if text and text.strip():
                flag = LANGUAGE_FLAGS.get(lang, "🌐")
                display_text = f"{flag} {text}"
                self.label.config(text=display_text)
            else:
                self.label.config(text="Aguardando áudio...")

        self.root.after(0, update)

    def get_position(self) -> tuple:
        """
        Get current window position.

        Returns:
            Tuple of (x, y) coordinates.
        """
        return (self.root.winfo_x(), self.root.winfo_y())

    def set_position(self, x: int, y: int) -> None:
        """
        Set window position.

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.root.geometry(f"+{x}+{y}")

    def destroy(self) -> None:
        """Clean up and destroy the window."""
        if self.listener:
            self.listener.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
