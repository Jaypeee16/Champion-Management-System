import os
import json
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import bcrypt
from database import get_connection
from dashboard import DashboardApp

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("green") 

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Absolute path for the Remember Me file so it never gets lost
        self.REMEMBER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remember_config.json")

        self.title("Champion Fine Tooling - Automated Management System")
        self.configure(fg_color="#F4F6F8") 
        self.minsize(450, 680)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        window_width = 450
        window_height = 680
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.icon_path = os.path.join(os.path.dirname(__file__), "assets", "login_logo.png")
        try:
            icon_img = tk.PhotoImage(file=self.icon_path)
            self.iconphoto(False, icon_img)
        except Exception:
            pass

        self.failed_attempts = 0

        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
        self.main_frame.pack(pady=40, padx=40, fill="both", expand=True)

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

        try:
            self.main_logo_img = ctk.CTkImage(light_image=Image.open(self.icon_path), size=(110, 100))
            self.logo_label = ctk.CTkLabel(self.content_frame, image=self.main_logo_img, text="")
            self.logo_label.pack(pady=(0, 10))
        except FileNotFoundError:
            self.logo_label = ctk.CTkLabel(self.content_frame, text="[ LOGO ]", font=("Inter", 20, "bold"), text_color="green")
            self.logo_label.pack(pady=(0, 10))

        self.label = ctk.CTkLabel(self.content_frame, text="Champion Fine Tooling Corp.", font=("Inter", 22, "bold"), text_color="#1A1A1A")
        self.label.pack(pady=(0, 2))

        self.sub_label = ctk.CTkLabel(self.content_frame, text="Automated Management System", font=("Inter", 16), text_color="#888888")
        self.sub_label.pack(pady=(0, 20))

        self.user_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Employee ID (Username)", width=280, height=40, 
                                       corner_radius=6, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="black")
        self.user_entry.pack(pady=(0, 15))
        self.user_entry.bind("<Return>", lambda e: self.login())

        self.pass_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=280, height=40)
        self.pass_frame.pack(pady=(0, 10))
        self.pass_frame.pack_propagate(False)

        self.pass_entry = ctk.CTkEntry(self.pass_frame, placeholder_text="Password", width=235, height=40, 
                                       corner_radius=6, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="black", show="•")
        self.pass_entry.pack(side="left")
        self.pass_entry.bind("<Return>", lambda e: self.login())

        self.show_pwd = False
        self.eye_btn = ctk.CTkButton(self.pass_frame, text="👁", width=40, height=40, corner_radius=6,
                                     fg_color="#F3F4F6", text_color="#4B5563", hover_color="#E5E7EB", command=self.toggle_password)
        self.eye_btn.pack(side="right", padx=(5, 0))

        self.remember_check = ctk.CTkCheckBox(self.content_frame, text="Remember me", font=("Inter", 11), checkbox_width=18, checkbox_height=18, border_color="#D1D5DB", text_color="#666666")
        self.remember_check.pack(anchor="w", pady=(0, 15))

        self.error_banner = ctk.CTkLabel(self.content_frame, text="", fg_color="transparent", text_color="#D8000C", font=("Inter", 11, "bold"), corner_radius=5)
        self.error_banner.pack(fill="x", pady=(0, 10))

        self.login_button = ctk.CTkButton(self.content_frame, text="Login", command=self.login,
                                          width=280, height=40, corner_radius=6,
                                          fg_color="#1E4528", hover_color="#14301C", font=("Inter", 13, "bold"))
        self.login_button.pack(pady=(0, 15))

        self.footer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.footer_frame.pack(pady=5)

        self.lbl_forgot_user = ctk.CTkLabel(self.footer_frame, text="Forgot Username?", font=("Inter", 11), text_color="#666666", cursor="hand2")
        self.lbl_forgot_user.pack(side="left", padx=5)
        self.lbl_forgot_user.bind("<Button-1>", lambda e: self.open_forgot_username())

        ctk.CTkLabel(self.footer_frame, text="|", font=("Inter", 11), text_color="#CCCCCC").pack(side="left")

        self.lbl_forgot_pass = ctk.CTkLabel(self.footer_frame, text="Forgot Password?", font=("Inter", 11), text_color="#666666", cursor="hand2")
        self.lbl_forgot_pass.pack(side="left", padx=5)
        self.lbl_forgot_pass.bind("<Button-1>", lambda e: self.open_forgot_password())

        self.register_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.register_frame.pack(pady=5)
        
        self.lbl_register = ctk.CTkLabel(self.register_frame, text="Don't have an account? Register Here", font=("Inter", 11, "bold"), text_color="#1E4528", cursor="hand2")
        self.lbl_register.pack()
        self.lbl_register.bind("<Button-1>", lambda e: self.open_register_window())

        self.load_remember_me()

    def center_window(self, window, width, height):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")

    def toggle_password(self):
        if self.show_pwd:
            self.pass_entry.configure(show="•")
            self.eye_btn.configure(text="👁")
            self.show_pwd = False
        else:
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="✕") 
            self.show_pwd = True

    def show_error(self, message):
        self.error_banner.configure(text=f"⚠ {message}", fg_color="#FFD2D2")

    def load_remember_me(self):
        print(f"\n--- BOOT: Checking for file at {self.REMEMBER_FILE} ---")
        if os.path.exists(self.REMEMBER_FILE):
            try:
                with open(self.REMEMBER_FILE, "r") as f:
                    data = json.load(f)
                    print(f"--- BOOT: Found saved data: {data} ---")
                    if "username" in data:
                        self.user_entry.delete(0, 'end') # Clear the box first
                        self.user_entry.insert(0, data["username"]) # Insert the saved ID
                        self.remember_check.select()
                        print("--- BOOT: Successfully injected ID into the login box! ---")
            except Exception as e:
                print(f"--- BOOT ERROR: Failed to read file: {e} ---")
        else:
            print("--- BOOT: No saved file found. ---")

    def handle_remember_me(self, username):
        check_state = self.remember_check.get()
        print(f"\n--- LOGIN: Remember Me checkbox state is: {check_state} ---")
        
        # We check for both integer 1 and string "1" just in case!
        if str(check_state) == "1":
            try:
                with open(self.REMEMBER_FILE, "w") as f:
                    json.dump({"username": username}, f)
                print(f"--- LOGIN: Successfully saved '{username}' to file! ---")
            except Exception as e:
                print(f"--- LOGIN ERROR: Could not save file: {e} ---")
        else:
            if os.path.exists(self.REMEMBER_FILE):
                os.remove(self.REMEMBER_FILE)
                print("--- LOGIN: Removed saved file because box was unchecked. ---")

    def login(self, event=None):
        if self.login_button.cget("state") == "disabled": return
            
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

            if user:
                input_password_bytes = password.encode('utf-8')
                stored_hash_bytes = user['password_hash'].encode('utf-8')
                
                if bcrypt.checkpw(input_password_bytes, stored_hash_bytes):
                    self.failed_attempts = 0
                    self.handle_remember_me(username) 
                    self.show_loading_screen(user)    
                    return 
            
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                messagebox.showwarning("Security Alert", "Too many failed attempts. Please request an admin reset.", parent=self)
                self.failed_attempts = 0 
                self.open_forgot_password()
            else:
                attempts_left = 3 - self.failed_attempts
                self.show_error(f"Invalid Credentials. {attempts_left} attempts left.")
                
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

        ctk.CTkLabel(load_win, text="Automated Management System", font=("Inter", 16, "bold"), text_color="white").pack(pady=(40, 5))
        ctk.CTkLabel(load_win, text="Initializing environment...", font=("Inter", 11), text_color="#A8D5BA").pack(pady=(0, 20))
        
        progress = ctk.CTkProgressBar(load_win, width=300, fg_color="#14301C", progress_color="#2ECC71")
        progress.pack()
        progress.set(0)

        def update_progress(val=0):
            if val < 1.0:
                progress.set(val)
                load_win.after(30, lambda: update_progress(val + 0.05))
            else:
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

        main_frame = ctk.CTkFrame(reg_win, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center") 

        ctk.CTkLabel(content, text="CREATE ACCOUNT", font=("Inter", 18, "bold"), text_color="#1A1A1A").pack(pady=(5, 5))
        ctk.CTkLabel(content, text="Register as Staff or Administrator", font=("Inter", 12), text_color="gray").pack(pady=(0, 10))

        emp_id = ctk.CTkEntry(content, placeholder_text="Employee ID (e.g. EMP-001)", width=300, height=35)
        emp_id.pack(pady=5)

        full_name = ctk.CTkEntry(content, placeholder_text="Full Name", width=300, height=35)
        full_name.pack(pady=5)

        email_entry = ctk.CTkEntry(content, placeholder_text="Email Address", width=300, height=35)
        email_entry.pack(pady=5)

        role_var = ctk.StringVar(value="Staff")
        role_menu = ctk.CTkOptionMenu(content, variable=role_var, values=["Staff", "Admin"], width=300, height=35, fg_color="#F9FAFB", text_color="black", button_color="#D1D5DB")
        role_menu.pack(pady=5)

        password = ctk.CTkEntry(content, placeholder_text="Password", show="•", width=300, height=35)
        password.pack(pady=5)

        confirm_pass = ctk.CTkEntry(content, placeholder_text="Confirm Password", show="•", width=300, height=35)
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
                messagebox.showerror("Database Error", "Cannot connect to the database.", parent=reg_win)
                return

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE employee_id = %s OR email = %s", (e_id, email_val))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Employee ID or Email already exists.", parent=reg_win)
                    return

                hashed_pw = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("""
                    INSERT INTO user (employee_id, full_name, email, password_hash, role) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (e_id, name, email_val, hashed_pw, role))
                conn.commit()

                messagebox.showinfo("Success", f"Account successfully registered as {role}.", parent=reg_win)
                reg_win.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to register: {e}", parent=reg_win)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        ctk.CTkButton(content, text="Register", fg_color="#1E4528", hover_color="#14301C", width=300, height=40, command=submit_registration).pack(pady=(15, 10))
        ctk.CTkButton(content, text="Cancel", fg_color="transparent", text_color="gray", hover_color="#F3F4F6", width=300, command=reg_win.destroy).pack(pady=(0, 5))

    def open_forgot_username(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Forgot Username")
        self.center_window(dialog, 450, 300)
        dialog.minsize(450, 300) 
        dialog.configure(fg_color="#F4F6F8")
        dialog.attributes("-topmost", True) 
        dialog.grab_set() 

        main_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(content, text="RETRIEVE USERNAME", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(content, text="Enter your registered email address to\nretrieve your Employee ID (Username).", font=("Inter", 11), text_color="gray", justify="left").pack(anchor="w", padx=10, pady=(0, 15))
        
        email_entry = ctk.CTkEntry(content, placeholder_text="Registered Email", width=340, height=35)
        email_entry.pack(padx=10, pady=(0, 15))

        def retrieve():
            email_val = email_entry.get().strip()
            if not email_val:
                messagebox.showerror("Error", "Please enter your email.", parent=dialog)
                return

            conn = get_connection()
            if not conn: return
            
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT employee_id, full_name FROM user WHERE email = %s", (email_val,))
                result = cursor.fetchone()
                
                if result:
                    messagebox.showinfo("Success", f"Account found for {result['full_name']}!\n\nYour Username is: {result['employee_id']}", parent=dialog)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "No account found with that email address.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}", parent=dialog)
            finally:
                if conn.is_connected(): cursor.close(); conn.close()

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Retrieve Username", fg_color="#1E4528", hover_color="#14301C", command=retrieve).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", width=80, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=dialog.destroy).pack(side="right")

    def open_forgot_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Forgot Password")
        self.center_window(dialog, 450, 400)
        dialog.minsize(450, 400)
        dialog.configure(fg_color="#F4F6F8")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        title_lbl = ctk.CTkLabel(content, text="RESET PASSWORD", font=("Inter", 14, "bold"), text_color="#1A1A1A")
        title_lbl.pack(anchor="w", padx=10, pady=(10, 5))
        
        desc_lbl = ctk.CTkLabel(content, text="Verify your identity by providing your\nEmployee ID and registered Email.", font=("Inter", 11), text_color="gray", justify="left")
        desc_lbl.pack(anchor="w", padx=10, pady=(0, 15))
        
        emp_id = ctk.CTkEntry(content, placeholder_text="Employee ID", width=340, height=35)
        emp_id.pack(padx=10, pady=5)
        
        email_entry = ctk.CTkEntry(content, placeholder_text="Registered Email", width=340, height=35)
        email_entry.pack(padx=10, pady=(5, 15))

        def verify_and_reset():
            e_id = emp_id.get().strip()
            e_mail = email_entry.get().strip()
            
            if not e_id or not e_mail:
                messagebox.showerror("Error", "Please fill in both fields.", parent=dialog)
                return

            conn = get_connection()
            if not conn: return

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE employee_id = %s AND email = %s", (e_id, e_mail))
                
                if cursor.fetchone():
                    emp_id.pack_forget()
                    email_entry.pack_forget()
                    btn_frame.pack_forget()
                    
                    title_lbl.configure(text="SET NEW PASSWORD")
                    desc_lbl.configure(text="Identity verified! Please enter your new password below.")
                    
                    new_pass = ctk.CTkEntry(content, placeholder_text="New Password", show="•", width=340, height=35)
                    new_pass.pack(padx=10, pady=5)
                    
                    confirm_pass = ctk.CTkEntry(content, placeholder_text="Confirm New Password", show="•", width=340, height=35)
                    confirm_pass.pack(padx=10, pady=(5, 15))
                    
                    def submit_new_password():
                        pwd = new_pass.get().strip()
                        cpwd = confirm_pass.get().strip()
                        
                        if not pwd or not cpwd:
                            messagebox.showerror("Error", "Please fill in all fields.", parent=dialog)
                            return
                        if pwd != cpwd:
                            messagebox.showerror("Error", "Passwords do not match.", parent=dialog)
                            return
                            
                        conn2 = get_connection()
                        if not conn2: return
                        try:
                            cursor2 = conn2.cursor()
                            hashed_pw = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            cursor2.execute("UPDATE user SET password_hash = %s WHERE employee_id = %s", (hashed_pw, e_id))
                            conn2.commit()
                            
                            messagebox.showinfo("Success", "Password successfully reset! You can now log in.", parent=dialog)
                            dialog.destroy()
                        except Exception as e:
                            messagebox.showerror("Error", f"Database error during update: {e}", parent=dialog)
                        finally:
                            if conn2.is_connected(): cursor2.close(); conn2.close()
                    
                    ctk.CTkButton(content, text="Confirm Reset", fg_color="#1E4528", hover_color="#14301C", width=340, height=40, command=submit_new_password).pack(padx=10, pady=5)
                else:
                    messagebox.showerror("Access Denied", "No matching account found with that ID and Email.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}", parent=dialog)
            finally:
                if conn.is_connected(): cursor.close(); conn.close()

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Verify Account", fg_color="#1E4528", hover_color="#14301C", command=verify_and_reset).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", width=80, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=dialog.destroy).pack(side="right")

    def on_closing(self):
        if messagebox.askyesno("Exit Application", "Are you sure you want to close the entire system?"):
            import os
            os._exit(0)    

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
