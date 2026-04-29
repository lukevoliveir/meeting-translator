"""Tela de seleção de idioma — primeira UI exibida ao usuário."""

import platform
import tkinter as tk

from config import SUPPORTED_LANGUAGES

_BG = "#1a1a2e"
_ROW_BG = "#16213e"
_INDIGO = "#6366f1"
_INDIGO_DARK = "#4f46e5"
_TEXT = "#ffffff"
_SUBTEXT = "#9ca3af"


class LanguageSelector:
    """Janela Tkinter para seleção do idioma alvo das legendas."""

    def __init__(self, root: tk.Tk):
        """
        Inicializa a janela de seleção de idioma.

        Args:
            root: Janela raiz do Tkinter
        """
        self.root = root
        self.root.title("Meeting Translator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.configure(bg=_BG)

        # Centraliza na tela
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"400x600+{(sw - 400) // 2}+{(sh - 600) // 2}")

        # macOS: traz a janela para frente para garantir renderização
        if platform.system() == "Darwin":
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.focus_force()

        self.selected_language = None
        self._selected_index = tk.IntVar(value=0)
        self._build_ui()

    def _build_ui(self) -> None:
        """Constrói todos os widgets da interface."""

        # ── CABEÇALHO via Canvas ──────────────────────────────────────
        # Canvas garante cores corretas no macOS independente do tema do sistema.
        hc = tk.Canvas(self.root, bg=_BG, height=148, highlightthickness=0, bd=0)
        hc.pack(fill=tk.X, pady=(8, 0))

        cx = 200  # centro horizontal (janela fixa 400 px)

        # Badge "MT"
        bx0, by0, bx1, by1 = cx - 32, 10, cx + 32, 52
        hc.create_rectangle(bx0, by0, bx1, by1, fill=_INDIGO, outline="")
        hc.create_text(cx, (by0 + by1) // 2, text="MT",
                       font=("Helvetica", 20, "bold"), fill=_TEXT, anchor="center")

        # Título
        hc.create_text(cx, 74, text="Meeting Translator",
                       font=("Helvetica", 16, "bold"), fill=_TEXT, anchor="center")

        # Subtítulo
        hc.create_text(cx, 104, text="Escolha o idioma das legendas",
                       font=("Helvetica", 11), fill=_SUBTEXT, anchor="center")

        # ── BOTÕES (base) — empacotados ANTES do container expansível ──
        # Em Tkinter, widgets com expand=True consomem todo espaço
        # restante, então os botões devem ser registrados antes.
        btn_frame = tk.Frame(self.root, bg=_BG)
        btn_frame.pack(fill=tk.X, padx=24, pady=(8, 20), side=tk.BOTTOM)

        # "Próximo →" — Frame colorido + Label dentro (mais confiável no macOS
        # do que depender de Label.bg sozinho)
        next_frame = tk.Frame(btn_frame, bg=_INDIGO, cursor="hand2")
        next_frame.pack(fill=tk.X, pady=(0, 10))
        next_lbl = tk.Label(
            next_frame,
            text="Próximo  →",
            font=("Helvetica", 13, "bold"),
            bg=_INDIGO,
            fg=_TEXT,
            cursor="hand2",
            pady=12,
        )
        next_lbl.pack(fill=tk.X)

        def _next_enter(e):
            next_frame.config(bg=_INDIGO_DARK)
            next_lbl.config(bg=_INDIGO_DARK)

        def _next_leave(e):
            next_frame.config(bg=_INDIGO)
            next_lbl.config(bg=_INDIGO)

        for w in (next_frame, next_lbl):
            w.bind("<Button-1>", lambda e: self._on_next())
            w.bind("<Enter>", _next_enter)
            w.bind("<Leave>", _next_leave)

        # "Pular configuração e iniciar"
        skip_lbl = tk.Label(
            btn_frame,
            text="Pular configuração e iniciar",
            font=("Helvetica", 10),
            bg=_BG,
            fg=_INDIGO,
            cursor="hand2",
        )
        skip_lbl.pack()
        skip_lbl.bind("<Button-1>", lambda e: self._on_skip())
        skip_lbl.bind("<Enter>", lambda e: skip_lbl.config(fg=_TEXT))
        skip_lbl.bind("<Leave>", lambda e: skip_lbl.config(fg=_INDIGO))

        # ── LISTA DE IDIOMAS (meio, expansível) ───────────────────────
        container = tk.Frame(self.root, bg=_BG)
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=(4, 6))

        # Scrollbar antes do canvas (garante espaço)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas com largura inicial explícita (evita rows invisíveis no 1º render)
        canvas = tk.Canvas(
            container,
            bg=_BG,
            highlightthickness=0,
            bd=0,
            yscrollcommand=scrollbar.set,
            width=340,
        )
        scrollbar.config(command=canvas.yview)

        inner = tk.Frame(canvas, bg=_BG)
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        win = canvas.create_window((0, 0), window=inner, anchor="nw", width=340)

        def _on_canvas_resize(event):
            canvas.itemconfig(win, width=event.width)

        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scroll com mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(
                -1 * (event.delta // 120 or (1 if event.delta > 0 else -1)),
                "units",
            )

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Linhas de idioma com Radiobutton
        row_font = ("Helvetica", 13)
        for idx, (code, flag, name) in enumerate(SUPPORTED_LANGUAGES):
            row = tk.Frame(inner, bg=_ROW_BG)
            row.pack(fill=tk.X, pady=2, padx=2)
            tk.Radiobutton(
                row,
                text=f"  {flag}  {name}",
                variable=self._selected_index,
                value=idx,
                font=row_font,
                bg=_ROW_BG,
                fg=_TEXT,
                selectcolor="#2d2d6b",
                activebackground="#2d2d6b",
                activeforeground=_TEXT,
                highlightthickness=0,
                bd=0,
                anchor="w",
                padx=10,
                pady=7,
                indicatoron=True,
                cursor="hand2",
            ).pack(fill=tk.X)

    def _on_next(self) -> None:
        """Trata clique em 'Próximo': salva idioma e fecha a janela."""
        self.selected_language = SUPPORTED_LANGUAGES[self._selected_index.get()][0]
        self.root.quit()

    def _on_skip(self) -> None:
        """Trata clique em 'Pular': usa o idioma selecionado e fecha."""
        self.selected_language = SUPPORTED_LANGUAGES[self._selected_index.get()][0]
        self.root.quit()

    def get_selected_language(self) -> str:
        """
        Retorna o código do idioma selecionado.

        Returns:
            Código ISO 639-1 (ex: "pt", "en")
        """
        return self.selected_language or SUPPORTED_LANGUAGES[0][0]


def show_language_selector() -> str:
    """
    Exibe a tela de seleção de idioma e retorna o código do idioma escolhido.

    Returns:
        Código ISO 639-1 do idioma selecionado (chamada bloqueante)
    """
    root = tk.Tk()
    selector = LanguageSelector(root)
    root.mainloop()
    root.destroy()
    return selector.get_selected_language()
