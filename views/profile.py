import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from database import get_connection
import re # <-- ADD THIS FOR VALIDATION
import bcrypt # <-- ADD THIS TO HASH THE NEW PASSWORD

class ProfileView(ctk.CTkFrame):
    def __init__(self, parent, user_info, dashboard_app):
        super().__init__(parent, fg_color="transparent")
        
        self.user_info = user_info
        self.dashboard = dashboard_app # Reference to main dashboard to sync UI
        self.db_conn = get_connection()

        # Layout: 1 column for Left Profile Card, 1 column for Right Forms
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(self, text="PROFILE", font=("Inter", 24, "bold"), text_color="#1A1A1A").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        self.build_left_card()
        self.build_right_cards()

    def build_left_card(self):
        self.left_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # Profile Picture
        self.pic_label = ctk.CTkLabel(self.left_card, text="", cursor="hand2")
        self.pic_label.pack(pady=(40, 5))
        self.pic_label.bind("<Button-1>", lambda e: self.upload_picture())
        
        ctk.CTkLabel(self.left_card, text="Click to upload profile picture", font=("Inter", 10), text_color="gray").pack()
        self.load_profile_picture()

        # User Info Text
        ctk.CTkLabel(self.left_card, text=self.user_info['full_name'], font=("Inter", 18, "bold"), text_color="#1A1A1A").pack(pady=(20, 0))
        ctk.CTkLabel(self.left_card, text=self.user_info['role'], font=("Inter", 12), text_color="green").pack()

        # Separator Line
        ctk.CTkFrame(self.left_card, height=1, fg_color="#E0E0E0").pack(fill="x", padx=30, pady=20)

        # Detail Rows
        details = [
            ("Username", self.user_info['employee_id']),
            ("Employee ID", self.user_info['employee_id']),
            ("Email", self.user_info.get('email', 'N/A')),
            ("Role", self.user_info['role'])
        ]
        for label, val in details:
            row = ctk.CTkFrame(self.left_card, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(row, text=label, font=("Inter", 12), text_color="gray").pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(side="right")

    def build_right_cards(self):
        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_container.grid_rowconfigure(0, weight=1)
        right_container.grid_rowconfigure(1, weight=1)

        # --- TOP RIGHT: Edit Profile Form ---
        edit_card = ctk.CTkFrame(right_container, fg_color="white", corner_radius=10)
        edit_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        ctk.CTkLabel(edit_card, text="Edit Profile", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=(20, 10))

        form_frame = ctk.CTkFrame(edit_card, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # Fields (Matches Figma layout)
        self.entry_name = self.create_form_field(form_frame, "Full Name *", self.user_info['full_name'], 0, 0)
        
        # Disabled fields
        user_entry = self.create_form_field(form_frame, "Username (Disabled)", self.user_info['employee_id'], 0, 1)
        user_entry.configure(state="disabled", fg_color="#F0F0F0")

        self.entry_email = self.create_form_field(form_frame, "Email *", self.user_info.get('email', ''), 1, 0)
        self.entry_dept = self.create_form_field(form_frame, "Department", "Operations (Default)", 1, 1)

        # Buttons
        btn_frame = ctk.CTkFrame(edit_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        # ACTION GUARD: Save Confirmation
        ctk.CTkButton(btn_frame, text="Save Profile", fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=self.confirm_save).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Change Password", fg_color="#F1C40F", hover_color="#D4AC0D", text_color="black", font=("Inter", 12, "bold"), command=self.open_password_modal).pack(side="left")

        # --- BOTTOM RIGHT: Borrowing History ---
        history_card = ctk.CTkFrame(right_container, fg_color="white", corner_radius=10)
        history_card.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        ctk.CTkLabel(history_card, text="My Borrowing History", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=20)
        
        # Placeholder for history table
        ctk.CTkLabel(history_card, text="No recent borrowing history found.", text_color="gray").pack(pady=30)

    def create_form_field(self, parent, label_text, default_val, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(frame, text=label_text, font=("Inter", 12), text_color="gray").pack(anchor="w")
        entry = ctk.CTkEntry(frame, height=35)
        entry.insert(0, default_val)
        entry.pack(fill="x", pady=(5, 0))
        return entry

    # --- FUNCTIONALITY ---

    def load_profile_picture(self):
        # Syncs the image with the local assets folder
        pic_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "profiles", f"{self.user_info['employee_id']}.png")
        if not os.path.exists(pic_path):
            pic_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
            
        try:
            img = ctk.CTkImage(light_image=Image.open(pic_path), size=(120, 120))
            self.pic_label.configure(image=img)
        except Exception:
            self.pic_label.configure(text="No Image")

    def upload_picture(self):
        # ACTION GUARD: Image Upload
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            if messagebox.askyesno("Confirm Upload", "Set this image as your new profile picture?"):
                dest_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "profiles")
                os.makedirs(dest_dir, exist_ok=True) # Ensure folder exists
                
                # Copy and rename file to employee_id
                dest_path = os.path.join(dest_dir, f"{self.user_info['employee_id']}.png")
                shutil.copy(file_path, dest_path)
                
                # Refresh UI globally
                self.load_profile_picture()
                self.dashboard.refresh_topbar()
                messagebox.showinfo("Success", "Profile picture updated successfully.")

    def confirm_save(self):
        # ACTION GUARD: Profile Data Update
        new_name = self.entry_name.get().strip()
        new_email = self.entry_email.get().strip()

        if not new_name or not new_email:
            messagebox.showwarning("Validation Error", "Full Name and Email are required.")
            return

        if messagebox.askyesno("Confirm Update", "Are you sure you want to save these changes to your profile?"):
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("UPDATE User SET full_name = %s, email = %s WHERE employee_id = %s", 
                               (new_name, new_email, self.user_info['employee_id']))
                self.db_conn.commit()
                
                # Update local state and trigger global refresh
                self.user_info['full_name'] = new_name
                self.user_info['email'] = new_email
                self.dashboard.refresh_topbar()
                
                # Refresh the left card text
                self.build_left_card() 
                messagebox.showinfo("Success", "Profile information updated securely.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save profile: {e}")

    def open_password_modal(self):
        # ACTION GUARD: Change Password Modal
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x350")
        
        # Center the dialog
        dialog.update_idletasks()
        x = int((dialog.winfo_screenwidth() / 2) - (400 / 2))
        y = int((dialog.winfo_screenheight() / 2) - (350 / 2))
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color="white")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="CHANGE PASSWORD", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=(20, 10))
        
        curr_entry = ctk.CTkEntry(dialog, placeholder_text="Current Password", width=340, height=35, show="*")
        curr_entry.pack(padx=30, pady=(0, 10))
        
        new_entry = ctk.CTkEntry(dialog, placeholder_text="New Password", width=340, height=35, show="*")
        new_entry.pack(padx=30, pady=(0, 10))
        
        conf_entry = ctk.CTkEntry(dialog, placeholder_text="Confirm New Password", width=340, height=35, show="*")
        conf_entry.pack(padx=30, pady=(0, 20))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30)
        
        # --- THE VALIDATION LOGIC ---
        def process_pwd_change():
            curr_pwd = curr_entry.get()
            new_pwd = new_entry.get()
            conf_pwd = conf_entry.get()

            # 1. Check for empty fields
            if not curr_pwd or not new_pwd or not conf_pwd:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return

            # 2. Check if new passwords match
            if new_pwd != conf_pwd:
                messagebox.showerror("Error", "New passwords do not match.", parent=dialog)
                return

            # 3. ENFORCE PASSWORD COMPLEXITY GUIDELINES
            if len(new_pwd) < 8:
                messagebox.showerror("Weak Password", "Password must be at least 8 characters long.", parent=dialog)
                return
            if not re.search(r"[A-Z]", new_pwd):
                messagebox.showerror("Weak Password", "Password must contain at least one uppercase letter (A-Z).", parent=dialog)
                return
            if not re.search(r"[a-z]", new_pwd):
                messagebox.showerror("Weak Password", "Password must contain at least one lowercase letter (a-z).", parent=dialog)
                return
            if not re.search(r"\d", new_pwd):
                messagebox.showerror("Weak Password", "Password must contain at least one number (0-9).", parent=dialog)
                return
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_pwd):
                messagebox.showerror("Weak Password", "Password must contain at least one special character (e.g., !@#$%).", parent=dialog)
                return

            # 4. Database Verification & Execution
            if messagebox.askyesno("Confirm", "Change password? You will need it for your next login.", parent=dialog):
                try:
                    cursor = self.db_conn.cursor(dictionary=True)
                    
                    # Verify current password matches the database
                    cursor.execute("SELECT password_hash FROM User WHERE employee_id = %s", (self.user_info['employee_id'],))
                    result = cursor.fetchone()
                    
                    if result and bcrypt.checkpw(curr_pwd.encode('utf-8'), result['password_hash'].encode('utf-8')):
                        # Hash the valid, strong new password
                        new_hashed = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt())
                        
                        # Save to database
                        cursor.execute("UPDATE User SET password_hash = %s WHERE employee_id = %s", 
                                       (new_hashed.decode('utf-8'), self.user_info['employee_id']))
                        self.db_conn.commit()
                        
                        messagebox.showinfo("Success", "Password updated successfully!", parent=dialog)
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Incorrect current password.", parent=dialog)
                        
                except Exception as e:
                    messagebox.showerror("Database Error", f"Failed to update password: {e}", parent=dialog)
                finally:
                    cursor.close()

        ctk.CTkButton(btn_frame, text="Change Password", fg_color="#1E4528", hover_color="#14301C", command=process_pwd_change).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=dialog.destroy).pack(side="right", width=80)