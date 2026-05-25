import os
import json
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import bcrypt
from database import get_connection, log_action
from dashboard import DashboardApp
from database import log_action

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.REMEMBER_FILE = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "remember_config.json")
        self.title("Champion Fine Tooling - Automated Management System")
        self.configure(fg_color="#F4F6F8")
        self.minsize(450, 680)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        w, h = 450, 680
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        self.icon_path = os.path.join(os.path.dirname(__file__), "assets", "login_logo.png")
        try:
            icon_img = tk.PhotoImage(file=self.icon_path)
            self.iconphoto(False, icon_img)
        except Exception:
            pass

        self.failed_attempts = 0

        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10,
                                        border_width=1, border_color="#E0E0E0")
        self.main_frame.pack(pady=40, padx=40, fill="both", expand=True)

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

        try:
            self.main_logo_img = ctk.CTkImage(light_image=Image.open(self.icon_path), size=(110, 100))
            ctk.CTkLabel(self.content_frame, image=self.main_logo_img, text="").pack(pady=(0, 10))
        except FileNotFoundError:
            ctk.CTkLabel(self.content_frame, text="[ LOGO ]",
                         font=("Inter", 20, "bold"), text_color="green").pack(pady=(0, 10))

        ctk.CTkLabel(self.content_frame, text="Champion Fine Tooling Corp.",
                     font=("Inter", 22, "bold"), text_color="#1A1A1A").pack(pady=(0, 2))
        ctk.CTkLabel(self.content_frame, text="Automated Management System",
                     font=("Inter", 16), text_color="#888888").pack(pady=(0, 20))

        self.user_entry = ctk.CTkEntry(self.content_frame,
                                        placeholder_text="Employee ID (Username)",
                                        width=280, height=40, corner_radius=6,
                                        fg_color="#F9FAFB", border_color="#D1D5DB",
                                        text_color="black")
        self.user_entry.pack(pady=(0, 15))
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())

        self.pass_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=280, height=40)
        self.pass_frame.pack(pady=(0, 10))
        self.pass_frame.pack_propagate(False)

        self.pass_entry = ctk.CTkEntry(self.pass_frame,
                                        placeholder_text="Password",
                                        width=235, height=40, corner_radius=6,
                                        fg_color="#F9FAFB", border_color="#D1D5DB",
                                        text_color="black", show="•")
        self.pass_entry.pack(side="left")
        self.pass_entry.bind("<Return>", lambda e: self.login())

        self.show_pwd = False
        self.eye_btn = ctk.CTkButton(self.pass_frame, text="👁", width=40, height=40,
                                      corner_radius=6, fg_color="#F3F4F6",
                                      text_color="#4B5563", hover_color="#E5E7EB",
                                      command=self.toggle_password)
        self.eye_btn.pack(side="right", padx=(5, 0))

        self.remember_check = ctk.CTkCheckBox(self.content_frame, text="Remember me",
                                               font=("Inter", 11), checkbox_width=18,
                                               checkbox_height=18, border_color="#D1D5DB",
                                               text_color="#666666")
        self.remember_check.pack(anchor="w", pady=(0, 15))

        self.error_banner = ctk.CTkLabel(self.content_frame, text="",
                                          fg_color="transparent", text_color="#D8000C",
                                          font=("Inter", 11, "bold"), corner_radius=5)
        self.error_banner.pack(fill="x", pady=(0, 10))

        self.login_button = ctk.CTkButton(self.content_frame, text="Login",
                                           command=self.login, width=280, height=40,
                                           corner_radius=6, fg_color="#1E4528",
                                           hover_color="#14301C",
                                           font=("Inter", 13, "bold"))
        self.login_button.pack(pady=(0, 15))

        footer = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        footer.pack(pady=5)
        lbl_u = ctk.CTkLabel(footer, text="Forgot Username?",
                              font=("Inter", 11), text_color="#666666", cursor="hand2")
        lbl_u.pack(side="left", padx=5)
        lbl_u.bind("<Button-1>", lambda e: self.open_forgot_username())
        ctk.CTkLabel(footer, text="|", font=("Inter", 11), text_color="#CCCCCC").pack(side="left")
        lbl_p = ctk.CTkLabel(footer, text="Forgot Password?",
                              font=("Inter", 11), text_color="#666666", cursor="hand2")
        lbl_p.pack(side="left", padx=5)
        lbl_p.bind("<Button-1>", lambda e: self.open_forgot_password())

        reg_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        reg_frame.pack(pady=5)
        lbl_r = ctk.CTkLabel(reg_frame, text="Don't have an account? Register Here",
                              font=("Inter", 11, "bold"), text_color="#1E4528", cursor="hand2")
        lbl_r.pack()
        lbl_r.bind("<Button-1>", lambda e: self.open_register_window())

        self.load_remember_me()

    def center_window(self, window, width, height):
        window.update_idletasks()
        sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")

    def toggle_password(self):
        if self.show_pwd:
            self.pass_entry.configure(show="•")
            self.eye_btn.configure(text="👁")
        else:
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="✕")
        self.show_pwd = not self.show_pwd

    def show_error(self, message):
        self.error_banner.configure(text=f"⚠ {message}", fg_color="#FFD2D2")

    def load_remember_me(self):
        if os.path.exists(self.REMEMBER_FILE):
            try:
                with open(self.REMEMBER_FILE, "r") as f:
                    data = json.load(f)
                    if "username" in data:
                        self.user_entry.delete(0, 'end')
                        self.user_entry.insert(0, data["username"])
                        self.remember_check.select()
            except Exception:
                pass

    def handle_remember_me(self, username):
        if str(self.remember_check.get()) == "1":
            try:
                with open(self.REMEMBER_FILE, "w") as f:
                    json.dump({"username": username}, f)
            except Exception:
                pass
        else:
            if os.path.exists(self.REMEMBER_FILE):
                os.remove(self.REMEMBER_FILE)

    def login(self, event=None):
        if self.login_button.cget("state") == "disabled":
            return
        self.login_button.configure(state="disabled", text="Authenticating...")
        self.update_idletasks()

        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            self.show_error("Please fill in all fields.")
            self.login_button.configure(state="normal", text="Login")
            return

        conn = get_connection()
        if not conn:
            self.show_error("Database connection failed.")
            self.login_button.configure(state="normal", text="Login")
            return

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE employee_id = %s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'),
                                        user['password_hash'].encode('utf-8')):
                self.failed_attempts = 0
                self.handle_remember_me(username)
                self.show_loading_screen(user)
                return

            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                messagebox.showwarning("Security Alert",
                                       "Too many failed attempts. Please reset your password.", parent=self)
                self.failed_attempts = 0
                self.open_forgot_password()
            else:
                self.show_error(f"Invalid Credentials. {3 - self.failed_attempts} attempt(s) left.")
            self.login_button.configure(state="normal", text="Login")
        except Exception as e:
            self.show_error(f"System Error: {e}")
            self.login_button.configure(state="normal", text="Login")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def show_loading_screen(self, user):
        self.withdraw()
        load_win = ctk.CTkToplevel(self)
        self.center_window(load_win, 400, 200)
        load_win.overrideredirect(True)
        load_win.configure(fg_color="#1E4528")
        ctk.CTkLabel(load_win, text="Automated Management System",
                     font=("Inter", 16, "bold"), text_color="white").pack(pady=(40, 5))
        ctk.CTkLabel(load_win, text="Initializing environment...",
                     font=("Inter", 11), text_color="#A8D5BA").pack(pady=(0, 20))
        progress = ctk.CTkProgressBar(load_win, width=300, fg_color="#14301C", progress_color="#2ECC71")
        progress.pack()
        progress.set(0)

        def update_progress(val=0):
            if val < 1.0:
                progress.set(val)
                load_win.after(30, lambda: update_progress(val + 0.05))
            else:
                # -> LOG ACTION GOES HERE <- 
                try:
                    log_action(user['user_id'], "Login", "Authentication", f"User '{user['full_name']}' logged in.")
                except Exception as e:
                    print(f"Failed to log login action: {e}")
                
                load_win.destroy()
                self.launch_dashboard(user)

        update_progress()

    def launch_dashboard(self, user):
        try:
            dashboard = DashboardApp(self, user_info=user)
            self.center_window(dashboard, 1350, 850)
            self.login_button.configure(state="normal", text="Login")
            if self.remember_check.get() == 0:
                self.user_entry.delete(0, 'end')
            self.pass_entry.delete(0, 'end')
        except Exception as e:
            self.show_error(f"Dashboard Error: {e}")
            self.deiconify()
            self.login_button.configure(state="normal", text="Login")

    def open_register_window(self):
        reg_win = ctk.CTkToplevel(self)
        reg_win.title("Register Account")
        self.center_window(reg_win, 450, 550)
        reg_win.minsize(450, 550)
        reg_win.configure(fg_color="#F4F6F8")
        reg_win.attributes("-topmost", True)
        reg_win.grab_set()

        main_frame = ctk.CTkFrame(reg_win, fg_color="white", corner_radius=10,
                                   border_width=1, border_color="#E0E0E0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(content, text="CREATE ACCOUNT",
                     font=("Inter", 18, "bold"), text_color="#1A1A1A").pack(pady=(5, 5))
        ctk.CTkLabel(content, text="Register as Staff or Administrator",
                     font=("Inter", 12), text_color="gray").pack(pady=(0, 10))

        emp_id = ctk.CTkEntry(content, placeholder_text="Employee ID (e.g. EMP-001)",
                               width=300, height=35)
        emp_id.pack(pady=5)
        full_name = ctk.CTkEntry(content, placeholder_text="Full Name",
                                  width=300, height=35)
        full_name.pack(pady=5)
        email_entry = ctk.CTkEntry(content, placeholder_text="Email Address",
                                    width=300, height=35)
        email_entry.pack(pady=5)
        role_var = ctk.StringVar(value="Staff")
        role_menu = ctk.CTkOptionMenu(content, variable=role_var,
                                       values=["Staff", "Admin"],
                                       width=300, height=35,
                                       fg_color="#F9FAFB", text_color="black",
                                       button_color="#D1D5DB")
        role_menu.pack(pady=5)
        password = ctk.CTkEntry(content, placeholder_text="Password",
                                 show="•", width=300, height=35)
        password.pack(pady=5)
        confirm_pass = ctk.CTkEntry(content, placeholder_text="Confirm Password",
                                     show="•", width=300, height=35)
        confirm_pass.pack(pady=5)

        def submit_registration():
            e_id = emp_id.get().strip()
            name = full_name.get().strip()
            email_val = email_entry.get().strip()
            pwd = password.get().strip()
            cpwd = confirm_pass.get().strip()
            role = role_var.get()

            if not all([e_id, name, email_val, pwd, cpwd]):
                messagebox.showerror("Error", "All fields are required.", parent=reg_win)
                return
            if pwd != cpwd:
                messagebox.showerror("Error", "Passwords do not match.", parent=reg_win)
                return

            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE employee_id=%s OR email=%s", (e_id, email_val))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Employee ID or Email already exists.", parent=reg_win)
                    return
                hashed_pw = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    INSERT INTO user (employee_id, full_name, email, password_hash, role)
                    VALUES (%s, %s, %s, %s, %s)
                """, (e_id, name, email_val, hashed_pw, role))
                conn.commit()
                new_uid = cursor.lastrowid
                log_action(new_uid, "Registered", "Authentication",
                           f"New account registered: '{name}' ({e_id}) as {role}.")
                messagebox.showinfo("Success", f"Account registered as {role}.", parent=reg_win)
                reg_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to register: {e}", parent=reg_win)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        ctk.CTkButton(content, text="Register", fg_color="#1E4528", hover_color="#14301C",
                      width=300, height=40,
                      command=submit_registration).pack(pady=(15, 10))
        ctk.CTkButton(content, text="Cancel", fg_color="transparent",
                      text_color="gray", hover_color="#F3F4F6", width=300,
                      command=reg_win.destroy).pack(pady=(0, 5))

    def open_forgot_username(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Forgot Username")
        self.center_window(dialog, 450, 300)
        dialog.configure(fg_color="#F4F6F8")
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        main_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=10,
                                   border_width=1, border_color="#E0E0E0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(content, text="RETRIEVE USERNAME",
                     font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(content,
                     text="Enter your registered email address to\nretrieve your Employee ID.",
                     font=("Inter", 11), text_color="gray", justify="left").pack(anchor="w", padx=10, pady=(0, 15))
        email_entry = ctk.CTkEntry(content, placeholder_text="Registered Email",
                                    width=340, height=35)
        email_entry.pack(padx=10, pady=(0, 15))

        def retrieve():
            email_val = email_entry.get().strip()
            if not email_val:
                messagebox.showerror("Error", "Please enter your email.", parent=dialog)
                return
            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT employee_id, full_name FROM user WHERE email=%s", (email_val,))
                result = cursor.fetchone()
                if result:
                    messagebox.showinfo("Found",
                                        f"Account: {result['full_name']}\nUsername: {result['employee_id']}",
                                        parent=dialog)
                    dialog.destroy()
                else:
                    messagebox.showerror("Not Found", "No account found with that email.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}", parent=dialog)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Retrieve Username", fg_color="#1E4528",
                      hover_color="#14301C",
                      command=retrieve).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", width=80, fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC",
                      command=dialog.destroy).pack(side="right")

    def open_forgot_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Forgot Password")
        self.center_window(dialog, 450, 400)
        dialog.configure(fg_color="#F4F6F8")
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        main_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=10,
                                   border_width=1, border_color="#E0E0E0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        title_lbl = ctk.CTkLabel(content, text="RESET PASSWORD",
                                  font=("Inter", 14, "bold"), text_color="#1A1A1A")
        title_lbl.pack(anchor="w", padx=10, pady=(10, 5))
        desc_lbl = ctk.CTkLabel(content,
                                 text="Verify your identity with your Employee ID and email.",
                                 font=("Inter", 11), text_color="gray", justify="left")
        desc_lbl.pack(anchor="w", padx=10, pady=(0, 15))
        emp_id = ctk.CTkEntry(content, placeholder_text="Employee ID",
                               width=340, height=35)
        emp_id.pack(padx=10, pady=5)
        email_entry = ctk.CTkEntry(content, placeholder_text="Registered Email",
                                    width=340, height=35)
        email_entry.pack(padx=10, pady=(5, 15))

        def verify_and_reset():
            e_id = emp_id.get().strip()
            e_mail = email_entry.get().strip()
            if not e_id or not e_mail:
                messagebox.showerror("Error", "Fill in both fields.", parent=dialog)
                return
            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE employee_id=%s AND email=%s", (e_id, e_mail))
                if cursor.fetchone():
                    emp_id.pack_forget()
                    email_entry.pack_forget()
                    btn_frame.pack_forget()
                    title_lbl.configure(text="SET NEW PASSWORD")
                    desc_lbl.configure(text="Identity verified! Enter your new password.")
                    new_pass = ctk.CTkEntry(content, placeholder_text="New Password",
                                            show="•", width=340, height=35)
                    new_pass.pack(padx=10, pady=5)
                    confirm_pass = ctk.CTkEntry(content, placeholder_text="Confirm New Password",
                                                show="•", width=340, height=35)
                    confirm_pass.pack(padx=10, pady=(5, 15))

                    def submit_new_password():
                        pwd = new_pass.get().strip()
                        cpwd = confirm_pass.get().strip()
                        if not pwd or not cpwd:
                            messagebox.showerror("Error", "Fill in all fields.", parent=dialog)
                            return
                        if pwd != cpwd:
                            messagebox.showerror("Error", "Passwords do not match.", parent=dialog)
                            return
                        conn2 = get_connection()
                        if not conn2:
                            return
                        try:
                            c2 = conn2.cursor()
                            hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            c2.execute("UPDATE user SET password_hash=%s WHERE employee_id=%s",
                                       (hashed, e_id))
                            conn2.commit()
                            messagebox.showinfo("Success", "Password reset! You can now log in.",
                                                parent=dialog)
                            dialog.destroy()
                        except Exception as e:
                            messagebox.showerror("Error", f"Update error: {e}", parent=dialog)
                        finally:
                            if conn2.is_connected():
                                c2.close()
                                conn2.close()

                    ctk.CTkButton(content, text="Confirm Reset", fg_color="#1E4528",
                                  hover_color="#14301C", width=340, height=40,
                                  command=submit_new_password).pack(padx=10, pady=5)
                else:
                    messagebox.showerror("Access Denied",
                                         "No matching account with that ID and Email.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}", parent=dialog)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Verify Account", fg_color="#1E4528",
                      hover_color="#14301C",
                      command=verify_and_reset).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", width=80, fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC",
                      command=dialog.destroy).pack(side="right")

    def on_closing(self):
        if messagebox.askyesno("Exit Application", "Close the entire system?"):
            os._exit(0)


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()