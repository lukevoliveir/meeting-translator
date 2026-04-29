"""Ponto de entrada principal do Tradutor de Reuniões em Tempo Real."""

import sys
import threading
from typing import Optional

from audio import AudioCapture
from config import TARGET_LANG, GLOSSARY_PROFILE, WHISPER_MODEL
from transcriber import WhisperTranscriber
from translator.translate import translate
from translator.glossary import merge_glossary
from speaker_profile.profiler import SpeakerProfile
from ui.language_selector import show_language_selector
from ui.speaker_profile_window import show_speaker_profile_window
from ui.overlay import OverlayWindow
from ui.session_summary import ExitConfirmDialog, SessionSummaryWindow


class MeetingTranslator:
    """Orquestrador principal da aplicação."""

    def __init__(self):
        """Inicializa o tradutor de reuniões."""
        self.target_lang: str = TARGET_LANG
        self.speaker_profile: Optional[SpeakerProfile] = None
        self.glossary: dict = {}
        self.overlay: Optional[OverlayWindow] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.transcriber: Optional[WhisperTranscriber] = None
        self.audio_thread: Optional[threading.Thread] = None
        self.running: bool = False
        self.last_captions = []  # últimas 5 legendas (original, traduzido)

    # ──────────────────────────────────────────────────────────────────
    # Fluxo de inicialização
    # ──────────────────────────────────────────────────────────────────

    def _show_language_selector(self) -> None:
        """Exibe a tela de seleção de idioma e salva o resultado."""
        print("Abrindo seletor de idioma...")
        self.target_lang = show_language_selector()
        print(f"Idioma selecionado: {self.target_lang}")

    def _show_speaker_profile_window(self) -> None:
        """Exibe a janela de perfil do falante e salva o resultado."""
        print("Abrindo janela de perfil do falante...")
        profile = show_speaker_profile_window()
        if profile:
            self.speaker_profile = profile
            print(f"Perfil carregado: {profile.accent} | {len(profile.vocab_list)} palavras")
        else:
            print("Nenhum perfil selecionado — iniciando sem perfil")

    def _load_glossary(self) -> None:
        """Carrega e mescla glossários (base + perfil do falante)."""
        speaker_glossary = self.speaker_profile.glossary if self.speaker_profile else None
        self.glossary = merge_glossary(GLOSSARY_PROFILE, speaker_glossary)
        print(f"Glossário carregado com {len(self.glossary)} termos")

    def _create_overlay(self) -> None:
        """Cria a janela de overlay com callback de fechamento."""
        self.overlay = OverlayWindow(on_close=self._handle_exit_request)
        if self.speaker_profile:
            self.overlay.set_speaker_profile_active(True)

    # ──────────────────────────────────────────────────────────────────
    # Processamento de áudio (thread background)
    # ──────────────────────────────────────────────────────────────────

    def start_audio_processing(self) -> None:
        """Inicia a captura e processamento de áudio em thread background."""

        def audio_loop():
            try:
                self.audio_capture = AudioCapture()
                self.transcriber = WhisperTranscriber()

                # Sinaliza para o overlay que o modelo está carregando
                if self.overlay:
                    self.overlay.update_text("⏳ Carregando modelo Whisper...", "pt")

                print("Iniciando processamento de áudio...")
                self.audio_capture.start()

                while self.running:
                    audio_chunk = self.audio_capture.get_chunk()

                    # Prompt inicial do perfil de falante (se disponível)
                    initial_prompt = (
                        self.speaker_profile.initial_prompt
                        if self.speaker_profile
                        else None
                    )

                    text, detected_lang = self.transcriber.transcribe(
                        audio_chunk,
                        initial_prompt=initial_prompt,
                    )

                    if not text or detected_lang == "silent":
                        continue

                    # Traduz se necessário
                    if detected_lang == self.target_lang:
                        display_text = text
                        display_lang = detected_lang
                    else:
                        translated = translate(text, detected_lang, self.target_lang)
                        display_text = translated
                        display_lang = self.target_lang

                    if display_text and display_text != "[Erro na tradução]":
                        if self.overlay:
                            self.overlay.update_text(display_text, display_lang)
                            self.overlay.increment_phrase_count()

                        # Mantém as últimas 5 legendas
                        self.last_captions.append((text, display_text))
                        if len(self.last_captions) > 5:
                            self.last_captions.pop(0)

                        print(f"[{detected_lang}→{display_lang}] {display_text}")

            except Exception as exc:
                print(f"Erro no processamento de áudio: {exc}")
                if self.overlay:
                    self.overlay.update_text(f"Erro: {exc}", "error")
            finally:
                if self.audio_capture:
                    self.audio_capture.stop()

        self.audio_thread = threading.Thread(target=audio_loop, daemon=True)
        self.audio_thread.start()

    # ──────────────────────────────────────────────────────────────────
    # Encerramento
    # ──────────────────────────────────────────────────────────────────

    def _handle_exit_request(self) -> None:
        """Trata clique no botão ✕ do overlay."""
        if not self.overlay:
            return

        stats = self.overlay.get_session_stats()

        dialog = ExitConfirmDialog(
            self.overlay.root,
            elapsed_minutes=stats["elapsed_minutes"],
            phrase_count=stats["phrase_count"],
        )
        should_exit = dialog.show()

        if should_exit:
            SessionSummaryWindow(
                self.overlay.root,
                elapsed_minutes=stats["elapsed_minutes"],
                phrase_count=stats["phrase_count"],
                source_lang="auto",
                target_lang=self.target_lang,
                whisper_model=WHISPER_MODEL,
                profile_active=stats["speaker_profile_active"],
                last_captions=self.last_captions,
            ).show()
            self.shutdown()

    def shutdown(self) -> None:
        """Encerra a aplicação de forma elegante."""
        print("Encerrando aplicação...")
        self.running = False

        if self.audio_capture:
            self.audio_capture.stop()

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2)

        if self.overlay:
            self.overlay.destroy()

        print("Aplicação encerrada com sucesso.")

    # ──────────────────────────────────────────────────────────────────
    # Ponto de entrada
    # ──────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Inicia a aplicação com o fluxo completo de UI."""
        print("=" * 60)
        print("Tradutor de Reuniões em Tempo Real")
        print("=" * 60)

        try:
            # 1. Seleção de idioma
            self._show_language_selector()

            # 2. Perfil do falante
            self._show_speaker_profile_window()

            # 3. Glossário
            self._load_glossary()

            # 4. Overlay
            self._create_overlay()

            # 5. Processamento de áudio (background)
            self.running = True
            self.start_audio_processing()

            print("\nControles:")
            print("- Clique e arraste: Mover janela")
            print("- Clique em ✕: Encerrar sessão")
            print("- Ctrl+C: Sair da aplicação")
            print("=" * 60)

            # 6. Loop principal do Tkinter (bloqueia até fechar)
            self.overlay.start()

        except KeyboardInterrupt:
            print("\n\nAplicação interrompida pelo usuário.")
            self.shutdown()
        except Exception as exc:
            print(f"\nErro fatal: {exc}")
            import traceback
            traceback.print_exc()
            self.shutdown()
            sys.exit(1)


def main() -> None:
    """Ponto de entrada da aplicação."""
    app = MeetingTranslator()
    app.run()


if __name__ == "__main__":
    main()
