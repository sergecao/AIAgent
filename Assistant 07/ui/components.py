import tkinter as tk
from tkinter import scrolledtext
from config import COLORS

class UIComponents:
    @staticmethod
    def create_header(parent, title_text, move_callback_start, move_callback_do):
        """Создание заголовка окна"""
        header_frame = tk.Frame(parent, bg=COLORS["header"], height=35)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        lbl_title = tk.Label(header_frame, text=f"   {title_text}",
                           bg=COLORS["header"], fg=COLORS["fg"],
                           font=("Segoe UI", 11, "bold"))
        lbl_title.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lbl_title.bind("<ButtonPress-1>", move_callback_start)
        lbl_title.bind("<B1-Motion>", move_callback_do)
        
        return header_frame, lbl_title

    @staticmethod
    def create_text_area(parent):
        """Создание области результатов"""
        txt_result = scrolledtext.ScrolledText(
            parent,
            bg=COLORS["input_bg"],
            fg=COLORS["success"],
            font=("Consolas", 10),
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        txt_result.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        return txt_result

    @staticmethod
    def create_status_bar(parent):
        """Создание строки состояния"""
        lbl_status = tk.Label(parent, text="Ожидание...",
                            bg=COLORS["bg"], fg="#888888",
                            font=("Segoe UI", 8), anchor=tk.W)
        lbl_status.pack(fill=tk.X, padx=20, pady=(0, 10))
        return lbl_status