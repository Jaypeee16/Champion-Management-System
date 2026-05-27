import os
import customtkinter as ctk
import sys
from tkinter import messagebox
from datetime import datetime
from PIL import Image
from database import get_connection, log_action

# Data Visualization
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import Views
from views.projects import ProjectsView
from views.inventory import InventoryView
from views.profile import ProfileView
from views.tagging import TaggingView
from views.borrowing import BorrowingView
from views.tracking import TrackingView
from views.reports import ReportsView
from views.maintenance import MaintenanceView
from views.role_management import RoleManagementView
from views.help import HelpView


class DashboardApp(ctk.CTkToplevel):
    def __init__(self, parent, user_info):
        super().__init__(master=parent)

        self.user_info = user_info
        self.title("Champion Fine Tooling - Automated Management System")

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = int(sw * 0.85)
        h = int(sh * 0.85)
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(1100, 700)

        self.protocol("WM_DELETE_WINDOW", self.confirm_logout)

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

        self.icon_path = os.path.join(os.path.dirname(__file__), "assets", "login_logo.png")
        try:
            self.sidebar_icon_img = ctk.CTkImage(light_image=Image.open(self.icon_path), size=(50, 50))
            self.sidebar_logo = ctk.CTkLabel(self.sidebar_frame, image=self.sidebar_icon_img, text="")
            self.sidebar_logo.pack(pady=(30, 10))
        except FileNotFoundError:
            self.sidebar_logo = ctk.CTkLabel(self.sidebar_frame, text="🟢", font=("Inter", 40))
            self.sidebar_logo.pack(pady=(30, 10))

        ctk.CTkLabel(self.sidebar_frame, text="Automated Management\nSystem",
                     font=("Inter", 14, "bold"), text_color="white").pack(pady=(0, 30))

        is_admin = self.user_info.get("role", "Staff") == "Admin"

        # FIX: Tinanggal ang "Reports" dito sa public view
        nav_items = [
            "Dashboard",
            "Project Management",
            "Products / Inventory",
            "Tagging",
            "Issuance & Retrieval",
            "Tracking & Accountability",
        ]
        
        # FIX: Nilipat ang "Reports" dito para Admin lang ang makakita
        if is_admin:
            nav_items += ["Reports", "Maintenance", "Role Management"]
            
        nav_items.append("Help")

        self.nav_buttons = {}
        for item in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame, text=item, anchor="w",
                fg_color="transparent", hover_color="#2A6038",
                text_color="white", font=("Inter", 13, "bold"),
                command=lambda m=item: self.show_frame(m)
            )
            btn.pack(fill="x", pady=2, padx=10)
            self.nav_buttons[item] = btn

        ctk.CTkButton(
            self.sidebar_frame, text="Exit", anchor="w",
            fg_color="transparent", hover_color="#8B0000",
            text_color="white", font=("Inter", 13, "bold"),
            command=self.confirm_logout
        ).pack(side="bottom", fill="x", pady=20, padx=10)

    def build_topbar(self):
        self.topbar_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="white")
        self.topbar_frame.grid(row=0, column=1, sticky="ew")
        self.topbar_frame.pack_propagate(False)

        self.logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        try:
            self.topbar_logo_img = ctk.CTkImage(light_image=Image.open(self.logo_path), size=(30, 30))
            self.header_logo = ctk.CTkLabel(
                self.topbar_frame, image=self.topbar_logo_img,
                text=" Champion Fine Tooling", compound="left",
                font=("Inter", 14, "bold"), text_color="#1A3B22"
            )
            self.header_logo.pack(side="left", padx=30)
        except FileNotFoundError:
            self.header_logo = ctk.CTkLabel(
                self.topbar_frame, text="Champion Fine Tooling",
                font=("Inter", 14, "bold"), text_color="#1A3B22"
            )
            self.header_logo.pack(side="left", padx=30)

        self.time_label = ctk.CTkLabel(self.topbar_frame, text="", font=("Inter", 12), text_color="#666666")
        self.time_label.pack(side="right", padx=(10, 30), pady=20)
        self._update_clock()

        self.user_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent", cursor="hand2")
        self.user_frame.pack(side="right", padx=15, pady=5)
        self.user_frame.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.user_text_frame = ctk.CTkFrame(self.user_frame, fg_color="transparent", cursor="hand2")
        self.user_text_frame.pack(side="right", padx=(10, 0))
        self.user_text_frame.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.user_name_label = ctk.CTkLabel(
            self.user_text_frame, text=f"{self.user_info['full_name']}",
            font=("Inter", 14, "bold"), text_color="black"
        )
        self.user_name_label.pack(anchor="w")
        self.user_name_label.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.user_role_label = ctk.CTkLabel(
            self.user_text_frame, text=f"{self.user_info['role']}",
            font=("Inter", 12, "bold"), text_color="#2ECC71"
        )
        self.user_role_label.pack(anchor="w")
        self.user_role_label.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.profile_pic_label = ctk.CTkLabel(self.user_frame, text="")
        self.profile_pic_label.pack(side="right")
        self.profile_pic_label.bind("<Button-1>", lambda e: self.show_frame("Profile"))

        self.refresh_topbar()

    def _update_clock(self):
        current_time = datetime.now().strftime("%a, %b %d, %Y  %I:%M:%S %p")
        self.time_label.configure(text=current_time)
        self._clock_job = self.after(1000, self._update_clock)

    def refresh_topbar(self):
        self.user_name_label.configure(text=f"{self.user_info['full_name']}")
        self.user_role_label.configure(text=f"{self.user_info['role']}")
        pic_path = os.path.join(
            os.path.dirname(__file__), "assets", "profiles",
            f"{self.user_info['employee_id']}.png"
        )
        if not os.path.exists(pic_path):
            pic_path = os.path.join(os.path.dirname(__file__), "assets", "login_logo.png")
        try:
            self.topbar_profile_img = ctk.CTkImage(light_image=Image.open(pic_path), size=(40, 40))
            self.profile_pic_label.configure(image=self.topbar_profile_img)
        except Exception:
            self.profile_pic_label.configure(text="👤")

    def confirm_logout(self):
        if hasattr(self, "_clock_job"):
            self.after_cancel(self._clock_job)
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of your account?"):
            log_action(self.user_info.get("user_id"), "Logout", "Authentication",
                       f"User {self.user_info.get('full_name')} logged out.")
            self.destroy()
            self.master.deiconify()
            self.master.pass_entry.delete(0, "end")
            self.master.error_banner.configure(text="", fg_color="transparent")
            self.master.failed_attempts = 0

    def show_frame(self, page_name):
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#2A6038", text_color="#F1C40F")
            else:
                btn.configure(fg_color="transparent", text_color="white")

        if self.current_frame is not None:
            self.current_frame.destroy()

        uid = self.user_info.get("user_id")
        if uid and page_name != "Dashboard":
            log_action(uid, "Viewed", page_name, f"Navigated to {page_name}")

        if page_name == "Profile":
            self.current_frame = ProfileView(self.main_container, self.user_info, self)
        elif page_name == "Project Management":
            self.current_frame = ProjectsView(self.main_container, self.user_info)
        elif page_name == "Products / Inventory":
            self.current_frame = InventoryView(self.main_container, self.user_info)
        elif page_name == "Tagging":
            self.current_frame = TaggingView(self.main_container)
        elif page_name == "Issuance & Retrieval":
            self.current_frame = BorrowingView(self.main_container, self.user_info)
        elif page_name == "Tracking & Accountability":
            self.current_frame = TrackingView(self.main_container, self.user_info)
        elif page_name == "Reports":
            self.current_frame = ReportsView(self.main_container)
        elif page_name == "Maintenance":
            self.current_frame = MaintenanceView(self.main_container)
        elif page_name == "Role Management":
            self.current_frame = RoleManagementView(self.main_container)
        elif page_name == "Help":
            self.current_frame = HelpView(self.main_container, self.user_info)
        elif page_name == "Dashboard":
            self.current_frame = self.create_home_dashboard()
        else:
            self.current_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
            ctk.CTkLabel(self.current_frame, text=f"{page_name.upper()} MODULE",
                         font=("Inter", 20), text_color="gray").pack(expand=True)

        self.current_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)

    def get_live_metrics(self):
        metrics = {"total_types": 0, "available_qty": 0, "borrowed_qty": 0, "employees": 0}
        activities = []
        chart_data = [0, 0, 0, 0]

        conn = get_connection()
        if not conn:
            return metrics, activities, chart_data

        try:
            cursor = conn.cursor(dictionary=True)
            # ... (keep your existing metrics logic here) ...
            cursor.execute("SELECT COUNT(*) as cnt FROM tool WHERE is_archived = 0")
            metrics["total_types"] = cursor.fetchone()["cnt"] or 0

            # In dashboard.py, inside get_live_metrics:
            cursor.execute("""
    SELECT ts, action, item, actor FROM (
        -- Select flagged requests AND solved requests
        SELECT
            DATE_FORMAT(DATE_ADD(sl.timestamp, INTERVAL 8 HOUR), '%Y-%m-%d %I:%M %p') as ts,
            sl.action_type as action,
            IFNULL(sl.module, '—') as item,
            IFNULL(u.full_name, 'System') as actor
        FROM system_logs sl
        LEFT JOIN user u ON sl.user_id = u.user_id
        WHERE sl.action_type IN ('Flagged', 'Solved') -- Ensure both are tracked

        UNION ALL

        SELECT
            DATE_FORMAT(DATE_ADD(tr.borrow_date, INTERVAL 8 HOUR), '%Y-%m-%d %I:%M %p') as ts,
            tr.type as action,
            t.name as item,
            u.full_name as actor
        FROM transaction tr
        JOIN tool t ON tr.tool_id = t.tool_id
        JOIN user u ON tr.user_id = u.user_id
            ) combined
         ORDER BY (action = 'Flagged') DESC, ts DESC
              LIMIT 8
            """)
            for row in cursor.fetchall():
                activities.append((row["ts"], row["action"], row["item"], row["actor"]))
            
            # ... (keep your existing chart_data logic here) ...
            cursor.execute("SELECT `condition`, COUNT(*) as cnt FROM tool WHERE is_archived = 0 GROUP BY `condition`")
            cond_map = {"Good": 0, "Needs Repair": 1, "Damaged": 2, "Lost": 3}
            for row in cursor.fetchall():
                c = row["condition"]
                if c in cond_map: chart_data[cond_map[c]] = row["cnt"]

        except Exception as e:
            print(f"Dashboard Sync Error: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        return metrics, activities, chart_data

    def create_home_dashboard(self):
        frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", orientation="vertical")

        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(inner_frame, text="DASHBOARD", font=("Inter", 24, "bold"),
                     text_color="#1A1A1A").pack(anchor="w", pady=(0, 20))

        metrics, activities, chart_data = self.get_live_metrics()

        cards_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))

        data = [
            ("Unique Tool Profiles", str(metrics["total_types"]), "#1E4528"),
            ("Total Physical Items", str(metrics["available_qty"]), "#2ECC71"),
            ("Items Borrowed", str(metrics["borrowed_qty"]), "#F1C40F"),
            ("Registered Employees", str(metrics["employees"]), "#D35400"),
        ]

        for i, (title, val, color) in enumerate(data):
            cards_frame.grid_columnconfigure(i, weight=1)
            card = ctk.CTkFrame(cards_frame, fg_color=color, corner_radius=10, height=100)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            card.pack_propagate(False)
            txt_color = "black" if color == "#F1C40F" else "white"
            ctk.CTkLabel(card, text=val, font=("Inter", 28, "bold"),
                         text_color=txt_color).pack(anchor="w", padx=20, pady=(20, 0))
            ctk.CTkLabel(card, text=title, font=("Inter", 12),
                         text_color=txt_color).pack(anchor="w", padx=20)

        bottom_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=2)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)

        activity_card = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        activity_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        ctk.CTkLabel(activity_card, text="Recent Activity",
                     font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=20)

        header_frame = ctk.CTkFrame(activity_card, fg_color="#1E4528", corner_radius=5, height=35)
        header_frame.pack(fill="x", padx=(20, 36))
        header_frame.pack_propagate(False)
        for col, text in enumerate(["Date & Time", "Action", "Item / Module", "User"]):
            header_frame.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        if not activities:
            activities = [("-", "No recent activity recorded.", "-", "-")]

        for i, row_data in enumerate(activities):
            row_frame = ctk.CTkFrame(activity_card,
                                     fg_color="#F9FAFB" if i % 2 == 0 else "white",
                                     height=35)
            row_frame.pack(fill="x", padx=20)
            row_frame.pack_propagate(False)
            for col, text in enumerate(row_data):
                row_frame.grid_columnconfigure(col, weight=1)
                ctk.CTkLabel(row_frame, text=text, font=("Inter", 11),
                             text_color="#1A1A1A").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        analytics_card = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        analytics_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        ctk.CTkLabel(analytics_card, text="Tool Condition Metrics",
                     font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 5))
        self.embed_chart(analytics_card, chart_data)
        row_frame = ctk.CTkFrame(activity_card, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=35)
             

        return frame

    def embed_chart(self, parent_frame, chart_data):
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        categories = ["Good", "Repair", "Damaged", "Lost"]
        colors = ["#2ECC71", "#F1C40F", "#E67E22", "#95A5A6"]

        bars = ax.bar(categories, chart_data, color=colors, width=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.get_yaxis().set_ticks([])

        for bar in bars:
            yval = bar.get_height()
            offset = max(chart_data) * 0.05 + 0.1 if max(chart_data) > 0 else 0.1
            ax.text(bar.get_x() + bar.get_width() / 2, yval + offset,
                    int(yval), ha="center", va="bottom",
                    fontdict={"family": "sans-serif", "weight": "bold", "color": "#333333"})

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))