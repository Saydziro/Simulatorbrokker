import tkinter as tk
from tkinter import ttk

def apply_theme(root: tk.Tk, style: ttk.Style, dark_mode: bool):
    if dark_mode:
        bg = "#2e2e2e"
        fg = "white"
        tree_bg = "#3c3f41"
        tree_fg = "white"
        btn_bg = "#5a5a5a"
    else:
        bg = "white"
        fg = "black"
        tree_bg = "white"
        tree_fg = "black"
        btn_bg = "#dcdcdc"

    root.configure(bg=bg)
    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=fg, font=("Arial", 10))
    style.configure("TButton", background=btn_bg, foreground=fg)
    style.configure("Treeview",
                    background=tree_bg,
                    foreground=tree_fg,
                    fieldbackground=tree_bg,
                    rowheight=25)
    style.map("Treeview", background=[('selected', '#0078d7')])
    style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
