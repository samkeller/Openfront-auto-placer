"""Canvas-drawn widgets providing the rounded, flat look ttk cannot render."""

from typing import Callable
import tkinter as tk
from tkinter import font as tkfont

from src.gui.theme import ACCENT, BORDER, FONT, INPUT_BG, MUTED, SURFACE


def round_rect(canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float,
               radius: float, **kwargs) -> int:
    """Draw a rounded rectangle, which Tk canvases do not provide natively."""
    points = (
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    )
    return canvas.create_polygon(points, smooth=True, **kwargs)


def repaint_children(widget: tk.Misc, color: str) -> None:
    """Propagate a new surface colour to plain Tk descendants."""
    for child in widget.winfo_children():
        if isinstance(child, (FlatButton, Segmented)):
            child.set_parent_bg(color)
        elif isinstance(child, (tk.Frame, tk.Label, tk.Canvas)):
            child.configure(bg=color)
            repaint_children(child, color)


class Card(tk.Frame):
    """Container drawing a rounded surface behind regular Tk children."""

    def __init__(self, master: tk.Misc, parent_bg: str, *, fill: str = SURFACE,
                 border: str = BORDER, radius: int = 14, padding: int = 16) -> None:
        super().__init__(master, bg=parent_bg, highlightthickness=0, bd=0)
        self._fill, self._border, self._radius = fill, border, radius
        self._backdrop = tk.Canvas(self, bg=parent_bg, highlightthickness=0, bd=0)
        self._backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        self.body = tk.Frame(self, bg=fill, highlightthickness=0, bd=0)
        self.body.pack(fill="both", expand=True, padx=padding, pady=padding)
        self.bind("<Configure>", lambda _event: self._draw())

    def _draw(self) -> None:
        self._backdrop.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        round_rect(self._backdrop, 1, 1, width - 1, height - 1, self._radius,
                   fill=self._fill, outline=self._border)

    def recolor(self, fill: str, border: str) -> None:
        self._fill, self._border = fill, border
        self.body.configure(bg=fill)
        repaint_children(self.body, fill)
        self._draw()


class Dot(tk.Canvas):
    """Small status indicator kept in sync with its surrounding surface."""

    def __init__(self, master: tk.Misc, parent_bg: str, color: str, size: int = 10) -> None:
        super().__init__(master, width=size, height=size, bg=parent_bg,
                         highlightthickness=0, bd=0)
        self._item = self.create_oval(1, 1, size - 1, size - 1, fill=color, outline=color)

    def recolor(self, color: str) -> None:
        self.itemconfigure(self._item, fill=color, outline=color)


class FlatButton(tk.Canvas):
    """Rounded borderless button, since ttk cannot render corner radii."""

    def __init__(self, master: tk.Misc, text: str, command: Callable[[], None], *,
                 parent_bg: str, fill: str, hover: str, fg: str, outline: str = "",
                 radius: int = 10, padx: int = 20, pady: int = 11, size: int = 10) -> None:
        self._font = tkfont.Font(family=FONT, size=size, weight="bold")
        width = self._font.measure(text) + padx * 2
        height = self._font.metrics("linespace") + pady * 2
        super().__init__(master, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self._text, self._command = text, command
        self._fill, self._hover, self._fg = fill, hover, fg
        self._outline, self._radius = outline, radius
        self._current = fill
        self._draw()
        self.bind("<Enter>", lambda _event: self._repaint(self._hover))
        self.bind("<Leave>", lambda _event: self._repaint(self._fill))
        self.bind("<Button-1>", lambda _event: self._command())

    def _draw(self) -> None:
        self.delete("all")
        width, height = int(self["width"]), int(self["height"])
        round_rect(self, 1, 1, width - 1, height - 1, self._radius,
                   fill=self._current, outline=self._outline or self._current)
        self.create_text(width / 2, height / 2, text=self._text, fill=self._fg, font=self._font)

    def _repaint(self, color: str) -> None:
        self._current = color
        self._draw()

    def set_parent_bg(self, color: str) -> None:
        self.configure(bg=color)
        self._draw()


class Segmented(tk.Canvas):
    """Inline selector replacing the combobox for short value lists."""

    def __init__(self, master: tk.Misc, variable: tk.StringVar,
                 options: tuple[tuple[str, str], ...], *, parent_bg: str) -> None:
        self._font = tkfont.Font(family=FONT, size=9, weight="bold")
        # Not named _options: tkinter.Misc._options is an internal method.
        self._items = options
        self._segment = max(self._font.measure(label) for _, label in options) + 18
        width = self._segment * len(options) + 6
        height = self._font.metrics("linespace") + 14
        super().__init__(master, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self._variable = variable
        variable.trace_add("write", lambda *_: self._draw())
        self.bind("<Button-1>", self._select)
        self._draw()

    def _select(self, event: "tk.Event[tk.Canvas]") -> None:
        index = int((event.x - 3) // self._segment)
        self._variable.set(self._items[min(max(index, 0), len(self._items) - 1)][0])

    def _draw(self) -> None:
        self.delete("all")
        width, height = int(self["width"]), int(self["height"])
        round_rect(self, 1, 1, width - 1, height - 1, 9, fill=INPUT_BG, outline=INPUT_BG)
        current = self._variable.get()
        for index, (value, label) in enumerate(self._items):
            left = 3 + index * self._segment
            selected = value == current
            if selected:
                round_rect(self, left, 3, left + self._segment, height - 3, 7,
                           fill=ACCENT, outline=ACCENT)
            self.create_text(left + self._segment / 2, height / 2, text=label,
                             font=self._font, fill="#ffffff" if selected else MUTED)

    def set_parent_bg(self, color: str) -> None:
        self.configure(bg=color)
        self._draw()
