import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
import bcrypt


class RoleManagementView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_ui()

    def build_ui(self):
        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.grid(row=0, column=0, sticky="nsew")
        self.inner.grid_columnconfigure(0, weight=1, minsize=320)
        self.inner.grid_columnconfigure(1, weight=2, minsize=600)
        self.inner.grid_rowconfigure(0, weight=1)

        self.build_form_panel()
        self.build_table_panel()

    # ==========================================
    # LEFT: Register / Add User Form
    # ==========================================
    def build_form_panel(self):
        form_card = ctk.CTkScrollableFrame(
            self.inner, fg_color="white", corner_radius=10, width=300)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(form_card, text="Register New User",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(
            anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(form_card,
                     text="Fill in all required fields to create a new account.",
                     font=("Inter", 11), text_color="gray", wraplength=240,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 15))

        def field(label, ph, show=None):
            ctk.CTkLabel(form_card, text=label, font=("Inter", 12, "bold"),
                         text_color="#1A1A1A").pack(anchor="w", padx=20)
            kw = dict(placeholder_text=ph)
            if show:
                kw["show"] = show
            e = ctk.CTkEntry(form_card, **kw)
            e.pack(fill="x", padx=20, pady=(5, 10))
            return e

        self.reg_emp_id = field("Employee ID *", "e.g., EMP-001")
        self.reg_name = field("Full Name *",    "Juan Dela Cruz")
        self.reg_email = field("Email Address",  "employee@champion.com")

        ctk.CTkLabel(form_card, text="Role *",
                     font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.reg_role = ctk.CTkOptionMenu(form_card, values=["Staff", "Admin"],
                                          fg_color="#F9FAFB", text_color="black")
        self.reg_role.pack(fill="x", padx=20, pady=(5, 10))

        self.reg_pass = field(
            "Password *",         "Min. 8 characters", show="•")
        self.reg_confirm = field("Confirm Password *",
                                 "Re-enter password",  show="•")

        btn_row = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(5, 20))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Register",
                      fg_color="#1E4528", hover_color="#14301C",
                      font=("Inter", 12, "bold"),
                      command=self.execute_register).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(btn_row, text="Clear",
                      fg_color="white", text_color="black",
                      border_width=1, border_color="#E0E0E0", hover_color="#F0F0F0",
                      font=("Inter", 12, "bold"),
                      command=self.clear_form).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def execute_register(self):
        emp_id = self.reg_emp_id.get().strip()
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        role = self.reg_role.get()
        pwd = self.reg_pass.get().strip()
        cpwd = self.reg_confirm.get().strip()

        if not all([emp_id, name, pwd, cpwd]):
            messagebox.showerror("Validation Error",
                                 "Employee ID, Full Name, and Password are required.",
                                 parent=self.winfo_toplevel())
            return
        if pwd != cpwd:
            messagebox.showerror("Password Mismatch", "Passwords do not match.",
                                 parent=self.winfo_toplevel())
            return
        if len(pwd) < 8:
            messagebox.showerror("Weak Password", "Password must be at least 8 characters.",
                                 parent=self.winfo_toplevel())
            return

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM user WHERE employee_id = %s", (emp_id,))
            if cursor.fetchone():
                messagebox.showerror("Duplicate",
                                     "An account with that Employee ID already exists.",
                                     parent=self.winfo_toplevel())
                return

            hashed = bcrypt.hashpw(pwd.encode(
                "utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute("""
                INSERT INTO user (employee_id, full_name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (emp_id, name, email or None, hashed, role))
            conn.commit()

            messagebox.showinfo("Success", f"Account registered successfully as {role}.",
                                parent=self.winfo_toplevel())
            self.clear_form()
            self.load_user_table()
        except Exception as e:
            messagebox.showerror("Database Error", str(e),
                                 parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def clear_form(self):
        self.reg_emp_id.delete(0, "end")
        self.reg_name.delete(0, "end")
        self.reg_email.delete(0, "end")
        self.reg_role.set("Staff")
        self.reg_pass.delete(0, "end")
        self.reg_confirm.delete(0, "end")

    # ==========================================
    # RIGHT: User Management Table
    # ==========================================
    def build_table_panel(self):
        table_card = ctk.CTkFrame(
            self.inner, fg_color="white", corner_radius=10)
        table_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(table_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(top, text="Registered Users",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")

        self.user_search = ctk.CTkEntry(
            top, placeholder_text="Search name or ID...", width=200)
        self.user_search.pack(side="right", padx=(5, 0))
        self.user_search.bind("<Return>", lambda e: self.load_user_table())
        ctk.CTkButton(top, text="Search", width=70,
                      fg_color="#1E4528", hover_color="#14301C",
                      font=("Inter", 11, "bold"),
                      command=self.load_user_table).pack(side="right", padx=5)
        ctk.CTkButton(top, text="↻", width=40,
                      fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC",
                      command=lambda: [self.user_search.delete(0, "end"),
                                       self.load_user_table()]).pack(side="right")

        headers = ["Employee ID", "Full Name", "Email", "Role", "Actions"]
        weights = [2,             3,            3,       1,      2]

        hdr = ctk.CTkFrame(table_card, fg_color="#1E4528",
                           corner_radius=5, height=38)
        hdr.pack(fill="x", padx=(20, 36))
        hdr.pack_propagate(False)
        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=10, pady=8, sticky="w")

        self.user_scroll = ctk.CTkScrollableFrame(
            table_card, fg_color="transparent")
        self.user_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.load_user_table()

    def load_user_table(self):
        for w in self.user_scroll.winfo_children():
            w.destroy()

        q = self.user_search.get().strip() if hasattr(self, "user_search") else ""
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT user_id, employee_id, full_name,
                       IFNULL(email,'—') as email, role
                FROM user WHERE 1=1
            """
            params = []
            if q:
                sql += " AND (full_name LIKE %s OR employee_id LIKE %s)"
                params = [f"%{q}%", f"%{q}%"]
            sql += " ORDER BY full_name ASC"
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            weights = [2, 3, 3, 1, 2]

            if not rows:
                ctk.CTkLabel(self.user_scroll, text="No users found.",
                             text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(rows):
                rf = ctk.CTkFrame(self.user_scroll,
                                  fg_color="#F9FAFB" if i % 2 == 0 else "white",
                                  height=40)
                rf.pack(fill="x", pady=2)
                rf.pack_propagate(False)

                vals = [row["employee_id"], row["full_name"],
                        row["email"], row["role"]]
                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    color = "#2ECC71" if col == 3 and val == "Admin" else "#1A1A1A"
                    ctk.CTkLabel(rf, text=val, font=("Inter", 11),
                                 text_color=color).grid(row=0, column=col, padx=10, pady=8, sticky="w")

                rf.grid_columnconfigure(4, weight=weights[4])
                action_frame = ctk.CTkFrame(rf, fg_color="transparent")
                action_frame.grid(row=0, column=4, padx=5, pady=4, sticky="w")
                ctk.CTkButton(action_frame, text="Edit", width=55, height=28,
                              fg_color="#F1C40F", text_color="black",
                              hover_color="#D4AC0D", font=("Inter", 10, "bold"),
                              command=lambda r=row: self.open_edit_modal(r)).pack(side="left", padx=(0, 4))
                ctk.CTkButton(action_frame, text="Delete", width=55, height=28,
                              fg_color="#FFEAEA", text_color="#D8000C",
                              hover_color="#FFC0C0", font=("Inter", 10, "bold"),
                              command=lambda r=row: self.delete_user(r)).pack(side="left")

        except Exception as e:
            ctk.CTkLabel(self.user_scroll,
                         text=f"Error: {e}", text_color="red").pack(pady=10)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def open_edit_modal(self, row):
        # --- FIX: Wider modal so buttons and fields are never compressed ---
        modal = ctk.CTkToplevel(self)
        modal.title(f"Edit User — {row['full_name']}")
        modal.geometry("500x460")
        modal.configure(fg_color="white")
        modal.resizable(False, False)
        modal.attributes("-topmost", True)
        modal.grab_set()
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - 250
        y = (modal.winfo_screenheight() // 2) - 230
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"Edit: {row['full_name']}",
                     font=("Inter", 15, "bold"), text_color="black").pack(pady=(20, 3))
        ctk.CTkLabel(modal, text=f"Employee ID: {row['employee_id']}",
                     font=("Inter", 11), text_color="gray").pack(pady=(0, 15))

        form = ctk.CTkFrame(modal, fg_color="transparent")
        form.pack(fill="x", padx=30)

        def make_row(lbl, val):
            ctk.CTkLabel(form, text=lbl, font=("Inter", 11, "bold"),
                         text_color="#1A1A1A").pack(anchor="w")
            e = ctk.CTkEntry(form, height=35)
            e.insert(0, val)
            e.pack(fill="x", pady=(4, 10))
            return e

        name_e = make_row("Full Name",  row["full_name"])
        email_e = make_row(
            "Email",      row["email"] if row["email"] != "—" else "")

        ctk.CTkLabel(form, text="Role", font=("Inter", 11, "bold"),
                     text_color="#1A1A1A").pack(anchor="w")
        role_menu = ctk.CTkOptionMenu(form, values=["Staff", "Admin"],
                                      fg_color="#F9FAFB", text_color="black", height=35)
        role_menu.set(row["role"])
        role_menu.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(form, text="New Password (leave blank to keep current)",
                     font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w")
        pass_e = ctk.CTkEntry(form, placeholder_text="Optional new password",
                              show="•", height=35)
        pass_e.pack(fill="x", pady=(4, 15))

        def save_edit():
            new_name = name_e.get().strip()
            new_email = email_e.get().strip()
            new_role = role_menu.get()
            new_pass = pass_e.get().strip()

            if not new_name:
                messagebox.showerror(
                    "Error", "Full Name is required.", parent=modal)
                return

            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                if new_pass:
                    if len(new_pass) < 8:
                        messagebox.showerror("Weak Password",
                                             "Password must be at least 8 characters.",
                                             parent=modal)
                        return
                    hashed = bcrypt.hashpw(new_pass.encode("utf-8"),
                                           bcrypt.gensalt()).decode("utf-8")
                    cursor.execute("""
                        UPDATE user SET full_name=%s, email=%s, role=%s, password_hash=%s
                        WHERE user_id=%s
                    """, (new_name, new_email or None, new_role, hashed, row["user_id"]))
                else:
                    cursor.execute("""
                        UPDATE user SET full_name=%s, email=%s, role=%s
                        WHERE user_id=%s
                    """, (new_name, new_email or None, new_role, row["user_id"]))
                conn.commit()
                messagebox.showinfo(
                    "Updated", "User account updated successfully.", parent=modal)
                modal.destroy()
                self.load_user_table()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkButton(btn_row, text="Save Changes", height=38,
                      fg_color="#1E4528", hover_color="#14301C",
                      command=save_edit).pack(side="left", padx=(0, 10), fill="x", expand=True)
        ctk.CTkButton(btn_row, text="Cancel", height=38,
                      fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC",
                      command=modal.destroy).pack(side="right", fill="x", expand=True)

    def delete_user(self, row):
        if messagebox.askyesno(
            "Confirm Delete",
            f"Permanently delete the account for '{row['full_name']}' ({row['employee_id']})?\n"
            "Their transaction history will remain in the system.",
            parent=self.winfo_toplevel()
        ):
            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM user WHERE user_id = %s", (row["user_id"],))
                conn.commit()
                messagebox.showinfo("Deleted", "User account deleted.",
                                    parent=self.winfo_toplevel())
                self.load_user_table()
            except Exception as e:
                messagebox.showerror("Error", str(
                    e), parent=self.winfo_toplevel())
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
