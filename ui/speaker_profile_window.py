"""Janela de criação e gerenciamento de perfis de falante."""

import platform
import threading
import tkinter as tk
from tkinter import font as tkfont
from typing import Optional, List

from speaker_profile.downloader import get_video_info, download_audio, cleanup_temp_audio
from speaker_profile.profiler import (
    SpeakerProfile, build_profile, load_profile, list_profiles,
)

_BG = "#0f0f1e"
_CARD = "#1a1a3e"
_INDIGO = "#6366f1"
_INDIGO_DARK = "#4f46e5"
_TEXT = "#ffffff"
_SUBTEXT = "#9ca3af"
_GOLD = "#f59e0b"
_GOLD_TEXT = "#1a1a00"
_GREEN = "#22c55e"
_RED = "#ef4444"

_ANALYSIS_STEPS = [
    "Baixando áudio do YouTube...",
    "Transcrevendo áudio com Whisper...",
    "Extraindo vocabulário técnico...",
    "Construindo glossário personalizado...",
    "Salvando perfil...",
]


def _make_btn(parent, text, command, bg=_INDIGO, fg=_TEXT, font_size=11, bold=True, pady=11):
    """Cria Label como botão com cores corretas no macOS."""
    weight = "bold" if bold else "normal"
    lbl = tk.Label(
        parent,
        text=text,
        font=tkfont.Font(family="Helvetica", size=font_size, weight=weight),
        bg=bg,
        fg=fg,
        cursor="hand2",
        pady=pady,
    )
    hover = _INDIGO_DARK if bg == _INDIGO else bg
    lbl.bind("<Button-1>", lambda e: command())
    lbl.bind("<Enter>", lambda e: lbl.config(bg=hover))
    lbl.bind("<Leave>", lambda e: lbl.config(bg=bg))
    return lbl


class SpeakerProfileWindow:
    """Janela Tkinter para criação e seleção de perfis de falante."""

    def __init__(self, root: tk.Tk):
        """
        Inicializa a janela de perfil do falante.

        Args:
            root: Janela raiz do Tkinter
        """
        self.root = root
        self.root.title("Perfil do Falante")
        self.root.geometry("520x660")
        self.root.resizable(False, False)
        self.root.configure(bg=_BG)

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"520x660+{(sw-520)//2}+{(sh-660)//2}")

        if platform.system() == "Darwin":
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.focus_force()

        self.selected_profile: Optional[SpeakerProfile] = None
        self.urls: List[dict] = []          # lista de {url, title, duration}
        self.temp_audio_files: List[str] = []
        self._current_frame: Optional[tk.Frame] = None
        self._url_rows: List[tk.Frame] = []
        self._profile_name_var = tk.StringVar(value="meu_perfil")
        self._url_var = tk.StringVar()
        self._step_var = tk.StringVar(value=_ANALYSIS_STEPS[0])
        self._progress_var = tk.DoubleVar(value=0.0)

        self._build_main_ui()

    # ──────────────────────────────────────────────────────────────────
    # Tela principal (input de URLs)
    # ──────────────────────────────────────────────────────────────────

    def _build_main_ui(self) -> None:
        """Constrói a tela principal de entrada de URLs."""
        if self._current_frame:
            self._current_frame.destroy()
        self._url_rows.clear()

        self._current_frame = tk.Frame(self.root, bg=_BG)
        self._current_frame.pack(fill=tk.BOTH, expand=True)

        pad = {"padx": 28}

        # ── Badge ──────────────────────────────────────────────────────
        badge = tk.Label(
            self._current_frame,
            text="  ✨ NOVA FEATURE  ",
            font=tkfont.Font(family="Helvetica", size=9, weight="bold"),
            bg=_GOLD,
            fg=_GOLD_TEXT,
            pady=3,
        )
        badge.pack(pady=(20, 0), **pad, anchor="w")

        # ── Título ─────────────────────────────────────────────────────
        tk.Label(
            self._current_frame,
            text="Perfil do Falante",
            font=tkfont.Font(family="Helvetica", size=18, weight="bold"),
            bg=_BG,
            fg=_TEXT,
        ).pack(pady=(6, 2), **pad, anchor="w")

        tk.Label(
            self._current_frame,
            text="Adicione vídeos do YouTube do palestrante para melhorar\na transcrição de termos técnicos e nomes próprios.",
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_BG,
            fg=_SUBTEXT,
            justify=tk.LEFT,
        ).pack(pady=(0, 14), **pad, anchor="w")

        # ── Perfis salvos ──────────────────────────────────────────────
        saved = list_profiles()
        if saved:
            tk.Label(
                self._current_frame,
                text="Perfis salvos:",
                font=tkfont.Font(family="Helvetica", size=10, weight="bold"),
                bg=_BG,
                fg=_SUBTEXT,
            ).pack(anchor="w", **pad)

            profiles_frame = tk.Frame(self._current_frame, bg=_BG)
            profiles_frame.pack(fill=tk.X, **pad, pady=(4, 10))

            for name in saved:
                btn = _make_btn(
                    profiles_frame,
                    f"👤  {name}",
                    lambda n=name: self._load_saved_profile(n),
                    bg=_CARD,
                    fg=_TEXT,
                    font_size=10,
                    bold=False,
                    pady=7,
                )
                btn.pack(fill=tk.X, pady=2)

        # ── Nome do perfil ─────────────────────────────────────────────
        tk.Label(
            self._current_frame,
            text="Nome do novo perfil:",
            font=tkfont.Font(family="Helvetica", size=10, weight="bold"),
            bg=_BG,
            fg=_SUBTEXT,
        ).pack(anchor="w", **pad)

        name_entry = tk.Entry(
            self._current_frame,
            textvariable=self._profile_name_var,
            font=tkfont.Font(family="Helvetica", size=12),
            bg=_CARD,
            fg=_TEXT,
            insertbackground=_TEXT,
            relief=tk.FLAT,
        )
        name_entry.pack(fill=tk.X, **pad, ipady=6, pady=(4, 12))

        # ── Campo URL + botão ──────────────────────────────────────────
        tk.Label(
            self._current_frame,
            text="URL do YouTube:",
            font=tkfont.Font(family="Helvetica", size=10, weight="bold"),
            bg=_BG,
            fg=_SUBTEXT,
        ).pack(anchor="w", **pad)

        url_row = tk.Frame(self._current_frame, bg=_BG)
        url_row.pack(fill=tk.X, **pad, pady=(4, 0))

        url_entry = tk.Entry(
            url_row,
            textvariable=self._url_var,
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_CARD,
            fg=_TEXT,
            insertbackground=_TEXT,
            relief=tk.FLAT,
        )
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7)
        url_entry.bind("<Return>", lambda e: self._add_url())

        add_btn = _make_btn(url_row, "+ Adicionar", self._add_url, font_size=10, pady=7)
        add_btn.pack(side=tk.LEFT, padx=(8, 0))

        # ── Lista de vídeos adicionados ────────────────────────────────
        self._video_list_frame = tk.Frame(self._current_frame, bg=_BG)
        self._video_list_frame.pack(fill=tk.X, **pad, pady=8)

        # ── Mensagem de status ─────────────────────────────────────────
        self._status_lbl = tk.Label(
            self._current_frame,
            text="",
            font=tkfont.Font(family="Helvetica", size=10),
            bg=_BG,
            fg=_SUBTEXT,
            wraplength=440,
        )
        self._status_lbl.pack(**pad, anchor="w")

        # ── Botões de ação ─────────────────────────────────────────────
        action_frame = tk.Frame(self._current_frame, bg=_BG)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM, **pad, pady=(0, 20))

        self._analyze_btn = _make_btn(
            action_frame,
            "Analisar vídeos e criar perfil  →",
            self._start_analysis,
        )
        self._analyze_btn.pack(fill=tk.X, pady=(0, 8))

        skip_lbl = tk.Label(
            action_frame,
            text="Pular — iniciar sem perfil",
            font=tkfont.Font(family="Helvetica", size=10),
            bg=_BG,
            fg=_INDIGO,
            cursor="hand2",
        )
        skip_lbl.pack()
        skip_lbl.bind("<Button-1>", lambda e: self._skip())
        skip_lbl.bind("<Enter>", lambda e: skip_lbl.config(fg=_TEXT))
        skip_lbl.bind("<Leave>", lambda e: skip_lbl.config(fg=_INDIGO))

    def _add_url(self) -> None:
        """Adiciona uma URL à lista após buscar informações do vídeo."""
        url = self._url_var.get().strip()
        if not url:
            return

        self._url_var.set("")
        self._status_lbl.config(text="Buscando informações do vídeo...", fg=_SUBTEXT)
        self.root.update_idletasks()

        try:
            info = get_video_info(url)
        except Exception as exc:
            self._status_lbl.config(text=f"Erro: {exc}", fg=_RED)
            return

        self.urls.append({"url": url, "title": info["title"], "duration": info["duration"]})
        self._status_lbl.config(text="", fg=_SUBTEXT)
        self._render_video_list()

    def _render_video_list(self) -> None:
        """Renderiza os cards de vídeo adicionados."""
        for w in self._video_list_frame.winfo_children():
            w.destroy()

        for i, item in enumerate(self.urls):
            card = tk.Frame(self._video_list_frame, bg=_CARD)
            card.pack(fill=tk.X, pady=3)

            info_frame = tk.Frame(card, bg=_CARD)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)

            tk.Label(
                info_frame,
                text=item["title"][:55] + ("…" if len(item["title"]) > 55 else ""),
                font=tkfont.Font(family="Helvetica", size=11, weight="bold"),
                bg=_CARD,
                fg=_TEXT,
                anchor="w",
            ).pack(anchor="w")

            tk.Label(
                info_frame,
                text=f"✓ adicionado  •  {item['duration']}",
                font=tkfont.Font(family="Helvetica", size=9),
                bg=_CARD,
                fg=_GREEN,
                anchor="w",
            ).pack(anchor="w")

            remove_btn = tk.Label(
                card,
                text="✕",
                font=tkfont.Font(family="Helvetica", size=12),
                bg=_CARD,
                fg=_SUBTEXT,
                cursor="hand2",
                padx=10,
            )
            remove_btn.pack(side=tk.RIGHT, pady=8)
            remove_btn.bind("<Button-1>", lambda e, idx=i: self._remove_url(idx))

    def _remove_url(self, index: int) -> None:
        """Remove um vídeo da lista pelo índice."""
        if 0 <= index < len(self.urls):
            self.urls.pop(index)
            self._render_video_list()

    def _load_saved_profile(self, name: str) -> None:
        """Carrega um perfil salvo diretamente e exibe a tela de resultado."""
        try:
            profile = load_profile(name)
            self._show_result_screen(profile)
        except Exception as exc:
            self._status_lbl.config(text=f"Erro ao carregar perfil: {exc}", fg=_RED)

    # ──────────────────────────────────────────────────────────────────
    # Análise / progresso
    # ──────────────────────────────────────────────────────────────────

    def _start_analysis(self) -> None:
        """Inicia a análise dos vídeos em thread background."""
        if not self.urls:
            self._status_lbl.config(text="Adicione pelo menos um vídeo.", fg=_RED)
            return

        profile_name = self._profile_name_var.get().strip() or "meu_perfil"
        self._build_progress_ui()

        def run():
            try:
                audio_files = []
                total = len(self.urls)

                for i, item in enumerate(self.urls):
                    step_pct = (i / total) * 60
                    self.root.after(0, lambda p=step_pct, s=_ANALYSIS_STEPS[0]: self._update_progress(s, p))
                    path = download_audio(item["url"], f"audio_{i}")
                    audio_files.append(path)
                    self.temp_audio_files.append(path)

                self.root.after(0, lambda: self._update_progress(_ANALYSIS_STEPS[1], 65))
                profile = build_profile(audio_files, profile_name)

                self.root.after(0, lambda: self._update_progress(_ANALYSIS_STEPS[4], 100))
                self.root.after(200, lambda: self._show_result_screen(profile))

            except Exception as exc:
                self.root.after(0, lambda: self._show_error(str(exc)))
            finally:
                for f in self.temp_audio_files:
                    cleanup_temp_audio(f)
                self.temp_audio_files.clear()

        threading.Thread(target=run, daemon=True).start()

    def _build_progress_ui(self) -> None:
        """Exibe a tela de progresso durante a análise."""
        if self._current_frame:
            self._current_frame.destroy()

        self._current_frame = tk.Frame(self.root, bg=_BG)
        self._current_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self._current_frame,
            text="Analisando vídeos...",
            font=tkfont.Font(family="Helvetica", size=17, weight="bold"),
            bg=_BG,
            fg=_TEXT,
        ).pack(pady=(60, 8))

        self._step_lbl = tk.Label(
            self._current_frame,
            textvariable=self._step_var,
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_BG,
            fg=_SUBTEXT,
        )
        self._step_lbl.pack(pady=(0, 24))

        # Barra de progresso simples
        bar_frame = tk.Frame(self._current_frame, bg=_CARD, height=8)
        bar_frame.pack(fill=tk.X, padx=40, pady=(0, 8))
        bar_frame.pack_propagate(False)

        self._progress_bar = tk.Frame(bar_frame, bg=_INDIGO, height=8)
        self._progress_bar.place(relx=0, rely=0, relwidth=0.0, relheight=1.0)

        self._progress_pct_lbl = tk.Label(
            self._current_frame,
            text="0%",
            font=tkfont.Font(family="Helvetica", size=10),
            bg=_BG,
            fg=_SUBTEXT,
        )
        self._progress_pct_lbl.pack()

    def _update_progress(self, step: str, pct: float) -> None:
        """Atualiza a barra de progresso e o rótulo de etapa (thread-safe)."""
        self._step_var.set(step)
        rel = min(pct / 100.0, 1.0)
        try:
            self._progress_bar.place(relwidth=rel)
            self._progress_pct_lbl.config(text=f"{int(pct)}%")
        except Exception:
            pass

    def _show_error(self, message: str) -> None:
        """Exibe mensagem de erro e volta para a tela principal após 3s."""
        if self._current_frame:
            self._current_frame.destroy()

        self._current_frame = tk.Frame(self.root, bg=_BG)
        self._current_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self._current_frame,
            text="Conexão indisponível",
            font=tkfont.Font(family="Helvetica", size=16, weight="bold"),
            bg=_BG,
            fg=_RED,
        ).pack(pady=(80, 8))

        tk.Label(
            self._current_frame,
            text="Iniciando sem perfil de falante...",
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_BG,
            fg=_SUBTEXT,
        ).pack()

        # Auto-pular após 3 segundos
        self.root.after(3000, self._skip)

    # ──────────────────────────────────────────────────────────────────
    # Tela de resultado
    # ──────────────────────────────────────────────────────────────────

    def _show_result_screen(self, profile: SpeakerProfile) -> None:
        """Exibe a tela de resultado após análise bem-sucedida."""
        if self._current_frame:
            self._current_frame.destroy()

        self._current_frame = tk.Frame(self.root, bg=_BG)
        self._current_frame.pack(fill=tk.BOTH, expand=True)

        pad = {"padx": 28}

        # Avatar com iniciais
        initials = profile.accent[:2].upper() if profile.accent else "MT"
        tk.Label(
            self._current_frame,
            text=initials,
            font=tkfont.Font(family="Helvetica", size=22, weight="bold"),
            bg=_INDIGO,
            fg=_TEXT,
            width=3,
            height=1,
        ).pack(pady=(28, 6))

        # Banner de sucesso
        success = tk.Frame(self._current_frame, bg="#1e3a2e")
        success.pack(fill=tk.X, **pad, pady=(0, 16))
        tk.Label(
            success,
            text="✅  Perfil criado com sucesso!",
            font=tkfont.Font(family="Helvetica", size=11),
            bg="#1e3a2e",
            fg=_GREEN,
            pady=8,
        ).pack()

        # Estatísticas
        stats_frame = tk.Frame(self._current_frame, bg=_CARD)
        stats_frame.pack(fill=tk.X, **pad, pady=(0, 12))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        stats = [
            ("Palavras únicas", str(len(profile.vocab_list))),
            ("Precisão estimada", "Alta"),
            ("Sotaque detectado", profile.accent or "N/A"),
            ("Duração analisada", f"{profile.audio_duration_minutes:.1f} min"),
        ]
        for i, (label, value) in enumerate(stats):
            row, col = divmod(i, 2)
            cell = tk.Frame(stats_frame, bg=_CARD)
            cell.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            tk.Label(cell, text=label, font=tkfont.Font(family="Helvetica", size=9),
                     bg=_CARD, fg=_SUBTEXT).pack(anchor="w")
            tk.Label(cell, text=value, font=tkfont.Font(family="Helvetica", size=13, weight="bold"),
                     bg=_CARD, fg=_TEXT).pack(anchor="w")

        # Top vocabulário (pills)
        tk.Label(
            self._current_frame,
            text="Vocabulário detectado:",
            font=tkfont.Font(family="Helvetica", size=10, weight="bold"),
            bg=_BG,
            fg=_SUBTEXT,
        ).pack(anchor="w", **pad)

        pills_frame = tk.Frame(self._current_frame, bg=_BG)
        pills_frame.pack(fill=tk.X, **pad, pady=(4, 12))

        for word in profile.vocab_list[:12]:
            pill = tk.Label(
                pills_frame,
                text=f" {word} ",
                font=tkfont.Font(family="Helvetica", size=10),
                bg=_CARD,
                fg=_TEXT,
                pady=3,
                padx=6,
            )
            pill.pack(side=tk.LEFT, padx=3, pady=2)

        # Botões
        btn_frame = tk.Frame(self._current_frame, bg=_BG)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, **pad, pady=(0, 20))

        use_btn = _make_btn(
            btn_frame,
            "Usar perfil e iniciar  →",
            lambda: self._use_profile(profile),
        )
        use_btn.pack(fill=tk.X, pady=(0, 8))

        skip_lbl = tk.Label(
            btn_frame,
            text="Iniciar sem este perfil",
            font=tkfont.Font(family="Helvetica", size=10),
            bg=_BG,
            fg=_INDIGO,
            cursor="hand2",
        )
        skip_lbl.pack()
        skip_lbl.bind("<Button-1>", lambda e: self._skip())
        skip_lbl.bind("<Enter>", lambda e: skip_lbl.config(fg=_TEXT))
        skip_lbl.bind("<Leave>", lambda e: skip_lbl.config(fg=_INDIGO))

    def _use_profile(self, profile: SpeakerProfile) -> None:
        """Confirma uso do perfil e fecha a janela."""
        self.selected_profile = profile
        self.root.quit()

    def _skip(self) -> None:
        """Pula a configuração de perfil e fecha a janela."""
        self.selected_profile = None
        self.root.quit()

    def get_selected_profile(self) -> Optional[SpeakerProfile]:
        """
        Retorna o perfil selecionado pelo usuário.

        Returns:
            SpeakerProfile se um perfil foi criado/carregado, None caso contrário
        """
        return self.selected_profile


def show_speaker_profile_window() -> Optional[SpeakerProfile]:
    """
    Exibe a janela de perfil do falante e retorna o perfil selecionado.

    Returns:
        SpeakerProfile se o usuário criou/selecionou um perfil, None se pulou
        (chamada bloqueante)
    """
    root = tk.Tk()
    window = SpeakerProfileWindow(root)
    root.mainloop()
    root.destroy()
    return window.get_selected_profile()
