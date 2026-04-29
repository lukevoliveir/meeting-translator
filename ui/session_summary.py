"""Diálogo de confirmação de saída e janela de resumo da sessão."""

import platform
import tkinter as tk
from tkinter import font as tkfont
from typing import List, Tuple, Optional

_BG = "#1a1a2e"
_CARD = "#16213e"
_INDIGO = "#6366f1"
_INDIGO_DARK = "#4f46e5"
_TEXT = "#ffffff"
_SUBTEXT = "#9ca3af"
_GREEN = "#22c55e"
_RED = "#ef4444"


def _make_btn(parent, text, command, bg=_INDIGO, fg=_TEXT, pady=10):
    """Cria um Label que funciona como botão (cores corretas no macOS)."""
    lbl = tk.Label(
        parent,
        text=text,
        font=tkfont.Font(family="Helvetica", size=12, weight="bold"),
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


class ExitConfirmDialog:
    """Modal de confirmação exibido ao clicar no botão ✕ do overlay."""

    def __init__(
        self,
        parent: tk.Tk,
        elapsed_minutes: int,
        phrase_count: int,
    ):
        """
        Inicializa o diálogo de confirmação de saída.

        Args:
            parent: Janela pai (root do overlay)
            elapsed_minutes: Minutos decorridos na sessão
            phrase_count: Número de frases traduzidas
        """
        self.result = False
        self.parent = parent
        self.elapsed_minutes = elapsed_minutes
        self.phrase_count = phrase_count

    def show(self) -> bool:
        """
        Exibe o diálogo e aguarda a escolha do usuário.

        Returns:
            True se o usuário confirmou encerramento, False para continuar
        """
        self.win = tk.Toplevel(self.parent)
        self.win.title("Encerrar tradução?")
        self.win.configure(bg=_BG)
        self.win.resizable(False, False)
        self.win.grab_set()  # Modal

        # Centraliza em relação ao parent
        self.win.update_idletasks()
        pw = self.parent.winfo_x()
        ph = self.parent.winfo_y()
        self.win.geometry(f"360x280+{pw - 80}+{ph - 200}")

        if platform.system() == "Darwin":
            self.win.lift()
            self.win.attributes("-topmost", True)
            self.win.focus_force()

        # ── Conteúdo ──────────────────────────────────────────────────
        tk.Label(
            self.win,
            text="Encerrar tradução?",
            font=tkfont.Font(family="Helvetica", size=16, weight="bold"),
            bg=_BG,
            fg=_TEXT,
        ).pack(pady=(24, 6))

        tk.Label(
            self.win,
            text="A sessão será finalizada e um resumo será gerado.",
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_BG,
            fg=_SUBTEXT,
            wraplength=300,
        ).pack(pady=(0, 16))

        # Stats
        stats_frame = tk.Frame(self.win, bg=_CARD)
        stats_frame.pack(fill=tk.X, padx=24, pady=(0, 20))

        tk.Label(
            stats_frame,
            text=f"⏱  {self.elapsed_minutes} min  •  {self.phrase_count} frases traduzidas",
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_CARD,
            fg=_SUBTEXT,
            pady=10,
        ).pack()

        # Botões
        btn_frame = tk.Frame(self.win, bg=_BG)
        btn_frame.pack(fill=tk.X, padx=24)

        continuar = _make_btn(btn_frame, "Continuar sessão", self._on_continue, bg=_CARD, fg=_TEXT)
        continuar.pack(fill=tk.X, pady=(0, 8))

        encerrar = _make_btn(btn_frame, "Encerrar e ver resumo", self._on_exit, bg=_RED)
        encerrar.pack(fill=tk.X)

        self.win.wait_window(self.win)
        return self.result

    def _on_continue(self) -> None:
        """Fecha o diálogo sem encerrar a sessão."""
        self.result = False
        self.win.destroy()

    def _on_exit(self) -> None:
        """Confirma encerramento da sessão."""
        self.result = True
        self.win.destroy()


class SessionSummaryWindow:
    """Janela de resumo exibida ao encerrar a sessão de tradução."""

    def __init__(
        self,
        parent: tk.Tk,
        elapsed_minutes: int,
        phrase_count: int,
        source_lang: str,
        target_lang: str,
        whisper_model: str,
        profile_active: bool,
        last_captions: Optional[List[Tuple[str, str]]] = None,
    ):
        """
        Inicializa a janela de resumo da sessão.

        Args:
            parent: Janela pai
            elapsed_minutes: Duração da sessão em minutos
            phrase_count: Total de frases traduzidas
            source_lang: Idioma de origem (auto-detectado)
            target_lang: Idioma alvo
            whisper_model: Modelo Whisper utilizado
            profile_active: Se um perfil de falante estava ativo
            last_captions: Últimas 5 legendas (original, traduzido)
        """
        self.parent = parent
        self.elapsed_minutes = elapsed_minutes
        self.phrase_count = phrase_count
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.whisper_model = whisper_model
        self.profile_active = profile_active
        self.last_captions = last_captions or []

    def show(self) -> None:
        """Exibe a janela de resumo e aguarda o fechamento."""
        self.win = tk.Toplevel(self.parent)
        self.win.title("Resumo da Sessão")
        self.win.configure(bg=_BG)
        self.win.resizable(False, False)
        self.win.grab_set()

        self.win.update_idletasks()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        self.win.geometry(f"440x580+{(sw-440)//2}+{(sh-580)//2}")

        if platform.system() == "Darwin":
            self.win.lift()
            self.win.attributes("-topmost", True)
            self.win.focus_force()

        # Scrollable
        canvas = tk.Canvas(self.win, bg=_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.win, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = tk.Frame(canvas, bg=_BG)
        win_id = canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

        self._build_content(content)

        self.win.wait_window(self.win)

    def _build_content(self, parent: tk.Frame) -> None:
        """Constrói o conteúdo da janela de resumo."""
        pad = {"padx": 24}

        # Título
        tk.Label(
            parent,
            text="✅  Sessão encerrada",
            font=tkfont.Font(family="Helvetica", size=17, weight="bold"),
            bg=_BG,
            fg=_TEXT,
        ).pack(pady=(24, 4), **pad)

        tk.Label(
            parent,
            text=f"Duração: {self.elapsed_minutes} minuto(s)",
            font=tkfont.Font(family="Helvetica", size=11),
            bg=_BG,
            fg=_SUBTEXT,
        ).pack(pady=(0, 16), **pad)

        # Grid de estatísticas
        stats_frame = tk.Frame(parent, bg=_CARD)
        stats_frame.pack(fill=tk.X, padx=24, pady=(0, 12))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        stats = [
            ("Frases traduzidas", str(self.phrase_count)),
            ("Par de idiomas", f"{self.source_lang} → {self.target_lang}"),
            ("Modelo Whisper", self.whisper_model),
            ("Participantes", "~1–5 est."),
        ]
        for i, (label, value) in enumerate(stats):
            row, col = divmod(i, 2)
            cell = tk.Frame(stats_frame, bg=_CARD)
            cell.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            tk.Label(cell, text=label, font=tkfont.Font(family="Helvetica", size=9),
                     bg=_CARD, fg=_SUBTEXT).pack(anchor="w")
            tk.Label(cell, text=value, font=tkfont.Font(family="Helvetica", size=13, weight="bold"),
                     bg=_CARD, fg=_TEXT).pack(anchor="w")

        # Banner de perfil ativo
        if self.profile_active:
            banner = tk.Frame(parent, bg="#1e3a2e")
            banner.pack(fill=tk.X, padx=24, pady=(0, 12))
            tk.Label(
                banner,
                text="👤  Perfil de falante utilizado nesta sessão",
                font=tkfont.Font(family="Helvetica", size=10),
                bg="#1e3a2e",
                fg=_GREEN,
                pady=8,
            ).pack()

        # Últimas legendas
        if self.last_captions:
            tk.Label(
                parent,
                text="Últimas legendas",
                font=tkfont.Font(family="Helvetica", size=12, weight="bold"),
                bg=_BG,
                fg=_TEXT,
            ).pack(anchor="w", padx=24, pady=(4, 6))

            for original, translated in self.last_captions[-5:]:
                card = tk.Frame(parent, bg=_CARD)
                card.pack(fill=tk.X, padx=24, pady=3)
                tk.Label(
                    card,
                    text=original,
                    font=tkfont.Font(family="Helvetica", size=9),
                    bg=_CARD,
                    fg=_SUBTEXT,
                    anchor="w",
                    wraplength=360,
                ).pack(fill=tk.X, padx=10, pady=(6, 1))
                tk.Label(
                    card,
                    text=translated,
                    font=tkfont.Font(family="Helvetica", size=11),
                    bg=_CARD,
                    fg=_TEXT,
                    anchor="w",
                    wraplength=360,
                ).pack(fill=tk.X, padx=10, pady=(1, 6))

        # Botão Fechar
        close_btn = tk.Label(
            parent,
            text="Fechar",
            font=tkfont.Font(family="Helvetica", size=12, weight="bold"),
            bg=_INDIGO,
            fg=_TEXT,
            cursor="hand2",
            pady=10,
        )
        close_btn.pack(fill=tk.X, padx=24, pady=(16, 24))
        close_btn.bind("<Button-1>", lambda e: self._on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=_INDIGO_DARK))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=_INDIGO))

    def _on_close(self) -> None:
        """Fecha a janela de resumo e encerra o app."""
        self.win.destroy()
        self.parent.quit()
