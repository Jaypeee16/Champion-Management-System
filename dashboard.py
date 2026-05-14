import os
import customtkinter as ctk
import sys
from tkinter import messagebox
from datetime import datetime
from PIL import Image

# Data Visualization
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import Views
from views.inventory import InventoryView
from views.profile import ProfileView
from views.tagging import TaggingView
from views.borrowing import BorrowingView

class DashboardApp(ctk.CTkToplevel): 
    def __init__(self, parent, user_info):
        
        # 2. Add master=parent inside the super() call
        super().__init__(master=parent) 

        self.user_info = user_info 
        self.title("Champion Fine Tooling - Automated Management System")
        self.geometry("1350x850")
        self.configure(fg_color="#F4F6F8") 
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.build_sidebar()
        self.build_topbar()
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=1, sticky="nsew", padx=30, pady=30)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.current_frame = None
        self.show_frame("Dashboard")

    def build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1A3B22")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # Circular Icon at the top left of the SIDEBAR
        self.icon_path = os.path.join(os.path.dirname(__file__), "assets", "login_logo.png") # The circle icon
        try:
            self.sidebar_icon_img = ctk.CTkImage(light_image=Image.open(self.icon_path), size=(50, 50))
            self.sidebar_logo = ctk.CTkLabel(self.sidebar_frame, image=self.sidebar_icon_img, text="")
            self.sidebar_logo.pack(pady=(30, 10))
        except FileNotFoundError:
            self.sidebar_logo = ctk.CTkLabel(self.sidebar_frame, text="🟢", font=("Inter", 40))
            self.sidebar_logo.pack(pady=(30, 10))

        ctk.CTkLabel(self.sidebar_frame, text="Automated Management\nSystem", font=("Inter", 14, "bold"), text_color="white").pack(pady=(0, 30))

        nav_items = [
            "Dashboard", "Products / Inventory", "Tagging", 
            "Borrowing & Return", "Tracking & Accountability", 
            "Reports", "Maintenance", "Role Management", "Help"
        ]

        self.nav_buttons = {}

        for item in nav_items:
            btn = ctk.CTkButton(self.sidebar_frame, text=item, anchor="w", fg_color="transparent",
                                hover_color="#2A6038", text_color="white", font=("Inter", 13, "bold"),
                                command=lambda m=item: self.show_frame(m))
            btn.pack(fill="x", pady=2, padx=10)
            self.nav_buttons[item] = btn

        exit_btn = ctk.CTkButton(self.sidebar_frame, text="Exit", anchor="w", fg_color="transparent",
                                hover_color="#8B0000", text_color="white", font=("Inter", 13, "bold"),
                                command=self.confirm_exit)
        exit_btn.pack(side="bottom", fill="x", pady=20, padx=10)

    def build_topbar(self):
        self.topbar_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="white")
        self.topbar_frame.grid(row=0, column=1, sticky="ew")
        self.topbar_frame.pack_propagate(False)

        # Company Logo at the top left of the TOPBAR (Next to "Champion Fine Tooling")
        self.logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        try:
            self.topbar_logo_img = ctk.CTkImage(light_image=Image.open(self.logo_path), size=(30, 30))
            self.header_logo = ctk.CTkLabel(self.topbar_frame, image=self.topbar_logo_img, text=" Champion Fine Tooling", compound="left", font=("Inter", 14, "bold"), text_color="#1A3B22")
            self.header_logo.pack(side="left", padx=30)
        except FileNotFoundError:
            self.header_logo = ctk.CTkLabel(self.topbar_frame, text="Champion Fine Tooling", font=("Inter", 14, "bold"), text_color="#1A3B22")
            self.header_logo.pack(side="left", padx=30)

        current_time = datetime.now().strftime("%a, %b %d, %Y, %I:%M %p")
        self.time_label = ctk.CTkLabel(self.topbar_frame, text=current_time, font=("Inter", 12), text_color="#666666")
        self.time_label.pack(side="right", padx=(10, 30), pady=20)

        self.user_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent", cursor="hand2")
        self.user_frame.pack(side="right", padx=15, pady=5)
        self.user_frame.bind("<Button-1>", lambda e: self.show_frame("Profile"))

       # Create a tiny invisible frame to stack the texts properly
        self.user_text_frame = ctk.CTkFrame(self.user_frame, fg_color="transparent", cursor="hand2")
        self.user_text_frame.pack(side="right", padx=(10, 0))
        self.user_text_frame.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        # The Name Label (Black)
        self.user_name_label = ctk.CTkLabel(self.user_text_frame, text=f"{self.user_info['full_name']}", 
                                       font=("Inter", 14, "bold"), text_color="black")
        self.user_name_label.pack(anchor="w") # 'w' forces it to align perfectly LEFT
        self.user_name_label.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        # The Role Label (Green)
        self.user_role_label = ctk.CTkLabel(self.user_text_frame, text=f"{self.user_info['role']}", 
                                       font=("Inter", 12, "bold"), text_color="#2ECC71")
        self.user_role_label.pack(anchor="w") # 'w' forces it to align perfectly LEFT
        self.user_role_label.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.profile_pic_label = ctk.CTkLabel(self.user_frame, text="")
        self.profile_pic_label.pack(side="right")
        self.profile_pic_label.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.refresh_topbar()

    def refresh_topbar(self):
        self.user_name_label.configure(text=f"{self.user_info['full_name']}")
        self.user_role_label.configure(text=f"{self.user_info['role']}")
        pic_path = os.path.join(os.path.dirname(__file__), "assets", "profiles", f"{self.user_info['employee_id']}.png")
        if not os.path.exists(pic_path):
            pic_path = os.path.join(os.path.dirname(__file__), "assets", "login_logo.png") 
        try:
            self.topbar_profile_img = ctk.CTkImage(light_image=Image.open(pic_path), size=(40, 40))
            self.profile_pic_label.configure(image=self.topbar_profile_img)
        except Exception:
            self.profile_pic_label.configure(text="👤")

    def confirm_exit(self):
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to close the Automated Management System?"):
            self.master.quit()     # 1. Stops the Tkinter main event loop
            self.master.destroy()  # 2. Destroys the hidden login window (and this dashboard)
            sys.exit(0)            # 3. Kills the Python process completely, stopping all background timers
    
    def confirm_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of your account?"):
            self.destroy() # Closes the dashboard
            self.master.deiconify() # Un-hides the login window!
            self.master.pass_entry.delete(0, 'end') # Clears the password for security

    def show_frame(self, page_name):
        # Handle Active Highlighting
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#2A6038", text_color="#F1C40F")
            else:
                btn.configure(fg_color="transparent", text_color="white")

        if self.current_frame is not None:
            self.current_frame.destroy()

        # REMOVED self.db_conn passing to fix the crash!
        if page_name == "Profile":
            self.current_frame = ProfileView(self.main_container, self.user_info, self)
        elif page_name == "Products / Inventory":
            self.current_frame = InventoryView(self.main_container)
        elif page_name == "Tagging":
            self.current_frame = TaggingView(self.main_container)
        elif page_name == "Borrowing & Return":
            self.current_frame = BorrowingView(self.main_container)
        elif page_name == "Dashboard":
            self.current_frame = self.create_home_dashboard()
        else:
            self.current_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
            ctk.CTkLabel(self.current_frame, text=f"{page_name.upper()} MODULE", font=("Inter", 20), text_color="gray").pack(expand=True)

        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def create_home_dashboard(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="DASHBOARD", font=("Inter", 24, "bold"), text_color="#1A1A1A").pack(anchor="w", pady=(0, 20))
        
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))

        # --- DASHBOARD CARD COLORS ---
        # Tuple format: (Title, Value, Color HEX)
        data = [
            ("Total Tools", "245", "#1E4528"),       # Dark Green
            ("Available Tools", "198", "#2ECC71"),   # Light Green
            ("Borrowed", "47", "#F1C40F"),           # Yellow
            ("Registered Employees", "86", "#D35400") # Orange
        ]
        
        for i, (title, val, color) in enumerate(data):
            cards_frame.grid_columnconfigure(i, weight=1)
            # Color the entire frame
            card = ctk.CTkFrame(cards_frame, fg_color=color, corner_radius=10, height=100)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            card.pack_propagate(False)
            
            # Contrast logic: Black text for yellow, white text for dark colors
            txt_color = "black" if color == "#F1C40F" else "white"
            
            ctk.CTkLabel(card, text=val, font=("Inter", 28, "bold"), text_color=txt_color).pack(anchor="w", padx=20, pady=(20, 0))
            ctk.CTkLabel(card, text=title, font=("Inter", 12), text_color=txt_color).pack(anchor="w", padx=20)

        # Bottom Area: Table and Analytics
        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        # Left: Recent Activity Table
        activity_card = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        activity_card.grid(row=0, column=0, sticky="nsew", padx=(5, 10))
        ctk.CTkLabel(activity_card, text="Recent Activity", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(activity_card, fg_color="#1E4528", corner_radius=5, height=35)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)
        headers = ["Date", "Action", "Item", "User"]
        for col, text in enumerate(headers):
            header_frame.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 11, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        dummy_activity = [
            ("2026-05-02 09:23", "Borrowed", "3/8 Drill Bit", "J. Santos"),
            ("2026-05-02 08:15", "Returned", "Hammer 1kg", "M. Cruz"),
            ("2026-05-01 16:45", "Added", "Caliper 150mm", "Admin")
        ]
        for i, row_data in enumerate(dummy_activity):
            row_frame = ctk.CTkFrame(activity_card, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=35)
            row_frame.pack(fill="x", padx=20)
            row_frame.pack_propagate(False)
            for col, text in enumerate(row_data):
                row_frame.grid_columnconfigure(col, weight=1)
                ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color="#1A1A1A").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Right: Matplotlib Analytics Visualization
        analytics_card = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        analytics_card.grid(row=0, column=1, sticky="nsew", padx=(10, 5))
        ctk.CTkLabel(analytics_card, text="Tool Availability Metrics", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 5))

        self.embed_chart(analytics_card)
        
        return frame

    def embed_chart(self, parent_frame):
        # Create a Matplotlib Figure
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        categories = ['Active', 'Borrowed', 'Maintenance', 'Archived']
        counts = [198, 47, 12, 5]
        colors = ['#2ECC71', '#F1C40F', '#E67E22', '#95A5A6']

        bars = ax.bar(categories, counts, color=colors, width=0.6)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_yaxis().set_ticks([])
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 2, int(yval), ha='center', va='bottom', fontdict={'family': 'sans-serif', 'weight': 'bold', 'color': '#333333'})

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
