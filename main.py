"""Main entry point for the Meeting Real-Time Translator application."""

import sys
import threading
from typing import Optional

from audio import AudioCapture
from config import TARGET_LANG
from transcriber import WhisperTranscriber
from translator import translate
from ui import OverlayWindow


class MeetingTranslator:
    """Main application orchestrator."""

    def __init__(self):
        """Initialize the translator application."""
        self.overlay: Optional[OverlayWindow] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.transcriber: Optional[WhisperTranscriber] = None
        self.audio_thread: Optional[threading.Thread] = None
        self.running = False

    def start_audio_processing(self) -> None:
        """Start audio capture and processing in a background thread."""
        def audio_loop():
            try:
                self.audio_capture = AudioCapture()
                self.transcriber = WhisperTranscriber()

                print("Starting audio processing...")
                self.audio_capture.start()

                while self.running:
                    # Get audio chunk from queue (blocks until available)
                    audio_chunk = self.audio_capture.get_chunk()

                    # Transcribe the chunk
                    text, detected_lang = self.transcriber.transcribe(audio_chunk)

                    if not text or detected_lang == "silent":
                        continue

                    # Determine target language and translate if needed
                    if detected_lang == TARGET_LANG:
                        # Same language, show original
                        display_text = text
                        display_lang = detected_lang
                    else:
                        # Different language, translate
                        translated_text = translate(text, detected_lang, TARGET_LANG)
                        display_text = translated_text
                        display_lang = TARGET_LANG

                    # Update overlay
                    if display_text and display_text != "[Erro na tradução]":
                        self.overlay.update_text(display_text, display_lang)
                        print(f"[{detected_lang}→{display_lang}] {display_text}")

            except Exception as e:
                print(f"Error in audio processing loop: {e}")
                if self.overlay:
                    self.overlay.update_text(f"Erro: {str(e)}", "error")
            finally:
                if self.audio_capture:
                    self.audio_capture.stop()

        self.audio_thread = threading.Thread(target=audio_loop, daemon=True)
        self.audio_thread.start()

    def run(self) -> None:
        """Start the application."""
        print("=" * 60)
        print("Tradutor de Reuniões em Tempo Real")
        print("=" * 60)
        print(f"Idioma alvo: {TARGET_LANG}")
        print("\nControles:")
        print("- Alt+T: Mostrar/Ocultar janela")
        print("- Clique e arraste: Mover janela")
        print("- Clique direito: Menu de contexto")
        print("- Ctrl+C: Sair da aplicação")
        print("=" * 60)

        try:
            # Create overlay window
            self.overlay = OverlayWindow()

            # Set running flag and start audio processing thread
            self.running = True
            self.start_audio_processing()

            # Run the overlay window on the main thread (tkinter requirement)
            self.overlay.start()

        except KeyboardInterrupt:
            print("\n\nAplicação interrompida pelo usuário.")
            self.shutdown()
        except Exception as e:
            print(f"\nErro fatal: {e}")
            self.shutdown()
            sys.exit(1)

    def shutdown(self) -> None:
        """Gracefully shut down the application."""
        print("Encerrando aplicação...")
        self.running = False

        if self.audio_capture:
            self.audio_capture.stop()

        # Wait for audio thread to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2)

        if self.overlay:
            self.overlay.destroy()

        print("Aplicação encerrada com sucesso.")


def main() -> None:
    """Entry point for the application."""
    app = MeetingTranslator()
    app.run()


if __name__ == "__main__":
    main()
