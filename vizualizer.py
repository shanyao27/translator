import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from src.pipeline import run
from src.errors import TranslatorError


class PascalVisualizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pascal → C++ Переводчик")
        self.root.geometry("1400x700")
        self.root.configure(bg="#2d2d2d")

        self.pascal_code = ""
        self.cpp_code = ""
        self.current_file = ""

        self.create_widgets()
        self.bind_hotkeys()

    # UI
    def create_widgets(self):
        top = tk.Frame(self.root, bg="#3c3c3c")
        top.pack(fill="x", padx=10, pady=10)

        tk.Button(
            top, text="ВЫБРАТЬ ФАЙЛ",
            bg="#00838F", fg="white",
            font=("Arial", 13, "bold"),
            padx=30, pady=12,
            command=self.open_file
        ).pack(side="left", padx=5)

        tk.Button(
            top, text="ПЕРЕВЕСТИ",
            bg="#4CAF50", fg="white",
            font=("Arial", 13, "bold"),
            padx=30, pady=12,
            command=self.translate
        ).pack(side="left", padx=5)

        self.btn_save = tk.Button(
            top, text="СОХРАНИТЬ",
            bg="#1976D2", fg="white",
            font=("Arial", 13, "bold"),
            padx=30, pady=12,
            command=self.save_cpp,
            state="disabled"
        )
        self.btn_save.pack(side="left", padx=5)

        self.file_label = tk.Label(
            top, text="Файл не выбран",
            bg="#3c3c3c", fg="#cccccc"
        )
        self.file_label.pack(side="left", padx=20)

        main = tk.Frame(self.root, bg="#2d2d2d")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Pascal
        left = tk.Frame(main, bg="#1e1e2e")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(left, text="PASCAL КОД", bg="#3c3c6c", fg="white").pack(fill="x")

        self.pascal_text = tk.Text(
            left, bg="#1e1e2e", fg="white",
            font=("Consolas", 11), wrap="word", undo=True
        )
        self.pascal_text.pack(fill="both", expand=True)

        # C++
        right = tk.Frame(main, bg="#1e2e1e")
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        tk.Label(right, text="C++ КОД", bg="#3c6c3c", fg="white").pack(fill="x")

        self.cpp_text = tk.Text(
            right, bg="#1e2e1e", fg="white",
            font=("Consolas", 11), wrap="word", undo=True
        )
        self.cpp_text.pack(fill="both", expand=True)

        self.status = tk.Label(
            self.root, text="Готово. Введите Pascal-код.",
            bg="#3c3c3c", fg="white", anchor="w", padx=20
        )
        self.status.pack(fill="x")

    # Добавление горячих клавиш для работы с кодом
    def bind_hotkeys(self):
        self.root.bind_all("<Control-c>", self.copy)
        self.root.bind_all("<Control-v>", self.paste)
        self.root.bind_all("<Control-x>", self.cut)
        self.root.bind_all("<Control-s>", lambda e: self.save_cpp())

    def copy(self, event=None):
        w = self.root.focus_get()
        if isinstance(w, tk.Text):
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(w.get("sel.first", "sel.last"))
            except tk.TclError:
                pass
        return "break"

    def paste(self, event=None):
        w = self.root.focus_get()
        if isinstance(w, tk.Text):
            try:
                w.insert(tk.INSERT, self.root.clipboard_get())
            except tk.TclError:
                pass
        return "break"

    def cut(self, event=None):
        w = self.root.focus_get()
        if isinstance(w, tk.Text):
            try:
                self.copy()
                w.delete("sel.first", "sel.last")
            except tk.TclError:
                pass
        return "break"

    #Основные методы
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Pascal", "*.pas"), ("All", "*.*")])
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            self.pascal_text.delete("1.0", tk.END)
            self.pascal_text.insert("1.0", f.read())

        self.current_file = Path(path).name
        self.file_label.config(text=self.current_file)
        self.status.config(text="Файл загружен")

    def translate(self):
        try:
            code = self.pascal_text.get("1.0", tk.END).strip()
            if not code:
                return

            self.cpp_text.delete("1.0", tk.END)
            self.cpp_text.insert("1.0", run(code))

            self.btn_save.config(state="normal")
            self.status.config(text="Перевод выполнен")

        except TranslatorError as e:
            messagebox.showerror("Ошибка", str(e))

    def save_cpp(self):
        if not self.cpp_text.get("1.0", tk.END).strip():
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".cpp",
            filetypes=[("C++", "*.cpp")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.cpp_text.get("1.0", tk.END))

        self.status.config(text=f"Сохранено: {Path(path).name}")


def main():
    PascalVisualizer().root.mainloop()


if __name__ == "__main__":
    main()
