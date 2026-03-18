import tkinter as tk
from tkinter import ttk, messagebox
from key_locker.core import (
    add_entry, get_entry, delete_entry,
    list_entries, vault_exists, change_master_password,
    get_vault_path
)


class LoginScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Key Locker")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self._build_ui()
        self._center()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        is_new = not vault_exists()

        tk.Label(self, text="🔐  Key Locker", font=("Segoe UI", 17, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, columnspan=2, pady=(20, 4))

        subtitle = "Create a master password" if is_new else "Enter your master password"
        tk.Label(self, text=subtitle, font=("Segoe UI", 10),
                 bg="#1e1e2e", fg="#6c7086").grid(row=1, column=0, columnspan=2, pady=(0, 14))

        tk.Label(self, text="Master Password:", bg="#1e1e2e", fg="#a6adc8",
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="e", padx=12, pady=6)

        self.pw_var = tk.StringVar()
        pw_entry = tk.Entry(self, textvariable=self.pw_var, show="•",
                            font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4",
                            relief="flat", width=22, insertbackground="#cdd6f4")
        pw_entry.grid(row=2, column=1, sticky="w", padx=12, pady=6)
        pw_entry.focus()

        self.confirm_var = tk.StringVar()
        if is_new:
            tk.Label(self, text="Confirm:", bg="#1e1e2e", fg="#a6adc8",
                     font=("Segoe UI", 10)).grid(row=3, column=0, sticky="e", padx=12, pady=6)
            tk.Entry(self, textvariable=self.confirm_var, show="•",
                     font=("Segoe UI", 11), bg="#313244", fg="#cdd6f4",
                     relief="flat", width=22, insertbackground="#cdd6f4").grid(
                row=3, column=1, sticky="w", padx=12, pady=6)

        btn_row = 4 if is_new else 3
        label = "Create Vault" if is_new else "Unlock"
        tk.Button(self, text=label, command=self._unlock,
                  font=("Segoe UI", 11, "bold"), bg="#89b4fa", fg="#1e1e2e",
                  relief="flat", cursor="hand2", padx=20, pady=6).grid(
            row=btn_row, column=0, columnspan=2, pady=16)

        pw_entry.bind("<Return>", lambda e: self._unlock())
        self.is_new = is_new

    def _unlock(self):
        master = self.pw_var.get()
        if not master:
            messagebox.showwarning("Empty", "Please enter a master password.")
            return

        if self.is_new:
            if master != self.confirm_var.get():
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return

        try:
            if not self.is_new:
                list_entries(master)  # validate password
        except ValueError:
            messagebox.showerror("Wrong Password", "Incorrect master password.")
            return

        self.withdraw()
        app = VaultApp(master, self)
        app.mainloop()


class VaultApp(tk.Toplevel):
    def __init__(self, master_password, login_window):
        super().__init__()
        self.master_password = master_password
        self.login_window = login_window
        self.title("Key Locker — Vault")
        self.configure(bg="#1e1e2e")
        self.resizable(False, False)
        self._build_ui()
        self._load_entries()
        self._center()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _on_close(self):
        self.destroy()
        self.login_window.destroy()

    def _build_ui(self):
        # header
        header = tk.Frame(self, bg="#181825", pady=10)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(header, text="🔐  Key Locker", font=("Segoe UI", 14, "bold"),
                 bg="#181825", fg="#cdd6f4").pack(side="left", padx=16)

        vault_path = str(get_vault_path())
        tk.Label(header, text=f"vault: {vault_path}", font=("Segoe UI", 8),
                 bg="#181825", fg="#45475a").pack(side="right", padx=16)

        # left — entry list
        left = tk.Frame(self, bg="#1e1e2e")
        left.grid(row=1, column=0, sticky="ns", padx=(14, 6), pady=14)

        tk.Label(left, text="Saved Entries", font=("Segoe UI", 10, "bold"),
                 bg="#1e1e2e", fg="#a6adc8").pack(anchor="w")

        self.listbox = tk.Listbox(left, width=22, height=16,
                                  font=("Segoe UI", 10), bg="#313244", fg="#cdd6f4",
                                  selectbackground="#89b4fa", selectforeground="#1e1e2e",
                                  relief="flat", activestyle="none")
        self.listbox.pack(pady=(6, 0))
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        tk.Button(left, text="Delete Selected", command=self._delete_entry,
                  font=("Segoe UI", 9), bg="#f38ba8", fg="#1e1e2e",
                  relief="flat", cursor="hand2", pady=4).pack(fill="x", pady=(8, 0))

        # right — detail / add form
        right = tk.Frame(self, bg="#1e1e2e")
        right.grid(row=1, column=1, sticky="n", padx=(6, 14), pady=14)

        # detail view
        self.detail_frame = tk.LabelFrame(right, text=" Entry Details ",
                                          bg="#1e1e2e", fg="#a6adc8",
                                          font=("Segoe UI", 9), padx=12, pady=10)
        self.detail_frame.pack(fill="x", pady=(0, 10))

        for label, attr in [("Name", "d_name"), ("Username", "d_user"),
                             ("Password", "d_pass"), ("Note", "d_note")]:
            tk.Label(self.detail_frame, text=f"{label}:", bg="#1e1e2e", fg="#6c7086",
                     font=("Segoe UI", 9)).grid(row=list(["Name","Username","Password","Note"]).index(label),
                                                column=0, sticky="e", pady=3)
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Label(self.detail_frame, textvariable=var, bg="#1e1e2e", fg="#cdd6f4",
                     font=("Segoe UI", 10), width=24, anchor="w").grid(
                row=list(["Name","Username","Password","Note"]).index(label),
                column=1, sticky="w", padx=8)

        tk.Button(self.detail_frame, text="Copy Password", command=self._copy_password,
                  font=("Segoe UI", 9), bg="#a6e3a1", fg="#1e1e2e",
                  relief="flat", cursor="hand2", pady=3).grid(
            row=4, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        # add new entry form
        add_frame = tk.LabelFrame(right, text=" Add New Entry ",
                                  bg="#1e1e2e", fg="#a6adc8",
                                  font=("Segoe UI", 9), padx=12, pady=10)
        add_frame.pack(fill="x")

        fields = [("Name *", "new_name"), ("Username", "new_user"),
                  ("Password *", "new_pass"), ("Note", "new_note")]

        for i, (label, attr) in enumerate(fields):
            tk.Label(add_frame, text=label, bg="#1e1e2e", fg="#6c7086",
                     font=("Segoe UI", 9)).grid(row=i, column=0, sticky="e", pady=3)
            var = tk.StringVar()
            setattr(self, attr, var)
            show = "•" if "pass" in attr else ""
            tk.Entry(add_frame, textvariable=var, show=show,
                     font=("Segoe UI", 10), bg="#313244", fg="#cdd6f4",
                     relief="flat", width=20, insertbackground="#cdd6f4").grid(
                row=i, column=1, sticky="w", padx=8, pady=3)

        tk.Button(add_frame, text="Save Entry", command=self._add_entry,
                  font=("Segoe UI", 10, "bold"), bg="#89b4fa", fg="#1e1e2e",
                  relief="flat", cursor="hand2", pady=5).grid(
            row=len(fields), column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def _load_entries(self):
        self.listbox.delete(0, "end")
        try:
            entries = list_entries(self.master_password)
            for name in entries:
                self.listbox.insert("end", name)
        except Exception:
            pass

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        name = self.listbox.get(sel[0])
        try:
            entry = get_entry(self.master_password, name)
            self.d_name.set(name)
            self.d_user.set(entry["username"])
            self.d_pass.set(entry["password"])
            self.d_note.set(entry["note"] or "—")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _copy_password(self):
        pw = self.d_pass.get()
        if not pw or pw == "":
            messagebox.showinfo("Nothing", "Select an entry first.")
            return
        self.clipboard_clear()
        self.clipboard_append(pw)
        messagebox.showinfo("Copied", "Password copied to clipboard.")

    def _add_entry(self):
        name = self.new_name.get().strip()
        password = self.new_pass.get().strip()

        if not name or not password:
            messagebox.showwarning("Missing", "Name and Password are required.")
            return

        try:
            add_entry(self.master_password, name,
                      self.new_user.get(), password, self.new_note.get())
            self.new_name.set("")
            self.new_user.set("")
            self.new_pass.set("")
            self.new_note.set("")
            self._load_entries()
            messagebox.showinfo("Saved", f"'{name}' saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_entry(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select an entry to delete.")
            return
        name = self.listbox.get(sel[0])
        if not messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            return
        try:
            delete_entry(self.master_password, name)
            self.d_name.set("")
            self.d_user.set("")
            self.d_pass.set("")
            self.d_note.set("")
            self._load_entries()
        except Exception as e:
            messagebox.showerror("Error", str(e))


def run_gui():
    app = LoginScreen()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
