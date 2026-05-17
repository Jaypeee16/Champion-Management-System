import os
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

        self.title("Champion Fine Tooling - Automated Management System")
        self.configure(fg_color="#F4F6F8") 
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- FIX 1: Robust Monitor Centering ---
        # We calculate and force the exact window placement instantly on launch
        window_width = 450
        window_height = 650
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

        # Main Container (The White Box)
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#E0E0E0")
        self.main_frame.pack(pady=40, padx=40, fill="both", expand=True)

        # --- FIX 2: Mathematical UI Centering ---
        # We wrap all the inputs in an invisible frame and anchor it to the dead center!
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
        self.sub_label.pack(pady=(0, 30))

        # Username Input
        self.user_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Username", width=280, height=40, 
                                       corner_radius=6, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="black")
        self.user_entry.pack(pady=(0, 15))
        self.user_entry.bind("<Return>", lambda e: self.login())

        # Password Input Frame
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

        # Checkbox & Error Banner
        self.remember_check = ctk.CTkCheckBox(self.content_frame, text="Remember me", font=("Inter", 11), checkbox_width=18, checkbox_height=18, border_color="#D1D5DB", text_color="#666666")
        self.remember_check.pack(anchor="w", pady=(0, 15))

        self.error_banner = ctk.CTkLabel(self.content_frame, text="", fg_color="transparent", text_color="#D8000C", font=("Inter", 11, "bold"), corner_radius=5)
        self.error_banner.pack(fill="x", pady=(0, 10))

        self.login_button = ctk.CTkButton(self.content_frame, text="Login", command=self.login,
                                          width=280, height=40, corner_radius=6,
                                          fg_color="#1E4528", hover_color="#14301C", font=("Inter", 13, "bold"))
        self.login_button.pack(pady=(0, 15))

        self.footer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.footer_frame.pack(pady=10)

        self.lbl_forgot_user = ctk.CTkLabel(self.footer_frame, text="Forgot Username?", font=("Inter", 11), text_color="#666666", cursor="hand2")
        self.lbl_forgot_user.pack(side="left", padx=10)
        self.lbl_forgot_user.bind("<Button-1>", lambda e: self.open_forgot_username())

        self.lbl_forgot_pass = ctk.CTkLabel(self.footer_frame, text="Forgot Password?", font=("Inter", 11), text_color="#666666", cursor="hand2")
        self.lbl_forgot_pass.pack(side="left", padx=10)
        self.lbl_forgot_pass.bind("<Button-1>", lambda e: self.open_forgot_password())

    def center_window(self, window, width, height):
        # ... (Keep this method completely intact, the modals still use it!)
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")

    def toggle_password(self):
        if self.show_pwd:
            self.pass_entry.configure(show="*")
            self.eye_btn.configure(text="👁")
            self.show_pwd = False
        else:
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="✕") 
            self.show_pwd = True

    def show_error(self, message):
        self.error_banner.configure(text=f"⚠ {message}", fg_color="#FFD2D2")

    def login(self, event=None):
        # 1. THE STATE LOCK: Prevent double-clicks / double-Enters
        if self.login_button.cget("state") == "disabled":
            return
            
        self.login_button.configure(state="disabled", text="Authenticating...")
        self.update_idletasks() # Force UI to update instantly
        
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            self.show_error("Please fill in all fields.")
            self.login_button.configure(state="normal", text="Login") # Unlock
            return

        conn = get_connection()
        if not conn:
            self.show_error("Database connection failed.")
            self.login_button.configure(state="normal", text="Login") # Unlock
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
                    
                    # Delay launch by 200ms so animations finish
                    self.after(200, lambda: self.launch_dashboard(user))
                    return # DO NOT unlock the button here; we are transitioning!
            
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                messagebox.showwarning("Security Alert", "Too many failed attempts. Please request an admin reset.", parent=self)
                self.failed_attempts = 0 
                self.open_forgot_password()
            else:
                attempts_left = 3 - self.failed_attempts
                self.show_error(f"Invalid Credentials. {attempts_left} attempts left.")
                
            # Unlock the button if login failed
            self.login_button.configure(state="normal", text="Login")
                
        except Exception as e:
            self.show_error(f"System Error: {e}")
            self.login_button.configure(state="normal", text="Login") # Unlock
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    # --- LAN-ADAPTED MODALS (Centered) ---
    def open_forgot_username(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Forgot Username")
        
        # Center the dialog!
        self.center_window(dialog, 400, 250)
        
        dialog.configure(fg_color="white")
        dialog.attributes("-topmost", True) 
        dialog.grab_set() 

        # Altered text to reflect LAN reality instead of email
        ctk.CTkLabel(dialog, text="FORGOT USERNAME", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=(20, 10))
        ctk.CTkLabel(dialog, text="Please provide your full name to generate\nan admin retrieval request ticket.", font=("Inter", 11), text_color="gray", justify="left").pack(anchor="w", padx=30, pady=(0, 15))
        
        email_entry = ctk.CTkEntry(dialog, placeholder_text="Full Name", width=340, height=35)
        email_entry.pack(padx=30, pady=(0, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30)
        
        ctk.CTkButton(btn_frame, text="Generate Request", fg_color="#1E4528", hover_color="#14301C", command=lambda: messagebox.showinfo("LAN Request", "Please see the Administrator with ID Ticket #4928.")).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=dialog.destroy).pack(side="right", width=80)

    def open_forgot_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Forgot Password")
        
        # Center the dialog!
        self.center_window(dialog, 400, 250)
        
        dialog.configure(fg_color="white")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="ACCOUNT LOCKOUT", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=(20, 10))
        ctk.CTkLabel(dialog, text="For security purposes, passwords cannot be retrieved.\nEnter your username to request a reset.", font=("Inter", 11), text_color="gray", justify="left").pack(anchor="w", padx=30, pady=(0, 15))
        
        user_entry = ctk.CTkEntry(dialog, placeholder_text="Username", width=340, height=35)
        user_entry.pack(padx=30, pady=(0, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30)
        
        ctk.CTkButton(btn_frame, text="Request Reset", fg_color="#1E4528", hover_color="#14301C", command=lambda: messagebox.showinfo("Admin Reset", "Reset requested. Please verify your identity with the System Administrator.")).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=dialog.destroy).pack(side="right", width=80)

    def launch_dashboard(self, user):
        """Builds the dashboard safely after the UI animations finish."""
        try:
            dashboard = DashboardApp(self, user_info=user)
            self.center_window(dashboard, 1350, 850)
            
            self.withdraw() 
            
            # 2. Reset the login button in the background for when they eventually log out
            self.login_button.configure(state="normal", text="Login")
            self.user_entry.delete(0, 'end')
            self.pass_entry.delete(0, 'end')
            
        except Exception as e:
            self.show_error(f"Dashboard Error: {e}")
            self.login_button.configure(state="normal", text="Login") # Unlock on crash

    # --- ADD THIS ENTIRE METHOD HERE ---
    def on_closing(self):
        """Global confirmation for the window's 'X' button."""
        if messagebox.askyesno("Exit Application", "Are you sure you want to close the entire system?"):
            self.quit()     # 1. Stop the Tkinter engine
            self.destroy()  # 2. Delete the window
            import os       # Just in case!
            os._exit(0)     # 3. Hard kill the process to prevent ghost errors

# (Leave this at the very bottom, touching the left wall)
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
