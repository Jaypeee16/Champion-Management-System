import customtkinter as ctk


class HelpView(ctk.CTkFrame):
    """
    Help Module — Figure 4 in the procedural flowchart.
    Provides Help Guide, FAQs, and System Requirements.
    Keyword search uses a linear scan (O(n)) over section/FAQ text,
    consistent with the system's simplicity goals documented in Chapter 3.
    Admin-only sections are hidden from Staff users.
    """

    # Sections tagged True are shown only to Admins
    GUIDE_SECTIONS = [
        (False, "1. Logging In", [
            "Enter your Employee ID (username) and password on the login screen.",
            "Click 'Login' or press Enter. Your role (Admin or Staff) determines which modules are accessible.",
            "After 3 failed attempts the system will prompt you to reset your password.",
            "Use 'Forgot Username?' or 'Forgot Password?' links if needed.",
        ]),
        (False, "2. Dashboard", [
            "The Dashboard shows live metrics: unique tool profiles, total physical items, borrowed items, and registered employees.",
            "The 'Recent Activity' table shows the last 5 system events across all modules.",
            "The 'Tool Condition Metrics' bar chart gives a quick visual health snapshot.",
        ]),
        (True, "3. Products / Inventory (Admin)", [
            "Use the left form to add a new tool: select Category, Supplier, enter Name, optional Price, Quantity, Location, and Status.",
            "Click any row in the table to open the Edit/Archive modal for that tool.",
            "Use the Search bar to filter by any field. Sort by Newest, Oldest, or Name.",
            "'Archive' hides a tool from active inventory without deleting its history.",
        ]),
        (False, "4. Products / Inventory (Staff — View Only)", [
            "Staff can view, search, and sort the tool list but cannot add, edit, or archive.",
        ]),
        (False, "5. Tagging", [
            "Click any tool row to open the Tag Manager for that tool.",
            "Enter or scan a Tag ID, or click '↻ Auto-Gen' to generate a smart tag based on Category and Supplier.",
            "Click 'Save Tag Link to Database' to assign the tag.",
            "The live QR preview updates as you type. Click '⎙ Generate Print File' to produce a printable PDF label.",
            "Use '📷 Scan & Test QR' to verify any existing tag with your webcam.",
        ]),
        (False, "6. Borrowing & Return", [
            "BORROW: Scan Employee ID → verify → scan tool Tag ID(s) to add to cart → enter Purpose → click 'Confirm Borrow'. A receipt PDF is generated.",
            "RETURN: Scan Employee ID → verify → scan Tool Tag or enter TRN number from receipt → set condition and quantity → click 'Confirm Return'.",
            "The Transaction History table shows the last 50 grouped transactions.",
        ]),
        (True, "7. Tracking & Accountability (Admin)", [
            "Borrow/Return Logs: Full list of every individual transaction.",
            "Audit Records: Filter by status (Active/Returned) and run comparisons to detect discrepancies.",
            "Manage Issues: Flag tools for review with condition and notes. Click any issue row to resolve it and sync the tool's condition.",
        ]),
        (False, "8. Tracking & Accountability (Staff)", [
            "Staff see only their own personal borrowing and return history.",
        ]),
        (False, "9. Reports", [
            "ABC Analysis: Categorizes tools by borrowing frequency using the Pareto principle (A = top 70%, B = next 20%, C = bottom 10%).",
            "Tool Usage Report: Shows each tool's total borrows, current checkouts, and available stock.",
            "Employee Activity: Summarizes per-employee borrow counts and active items.",
            "All three tabs have an '⎙ Export PDF' button.",
        ]),
        (True, "10. Maintenance (Admin Only)", [
            "Backup: Select tables and save a timestamped JSON backup file.",
            "Restore: Load a previous JSON backup to overwrite matching records.",
            "Archived Tools: View, restore, or permanently delete archived tools.",
        ]),
        (True, "11. Role Management (Admin Only)", [
            "Register new users with Employee ID, Full Name, Email, Role, and Password.",
            "View all registered accounts in the table on the right.",
            "Click 'Edit' to update name, email, role, or reset a user's password.",
            "Click 'Delete' to remove an account (transaction history is preserved).",
        ]),
        (False, "12. Profile", [
            "View and edit your Full Name and Email.",
            "Change your password via the 'Change Password' button (requires current password for verification).",
            "Click your profile picture to upload a new one.",
            "Click '⎙ Print My ID QR Badge' to generate a scannable employee ID card.",
            "The 'My Borrowing History' section shows your personal transaction records.",
        ]),
    ]

    FAQS = [
        (False, "I scanned my QR code but the scanner didn't detect it. What do I do?",
         "Ensure the QR code is well-lit and held steady inside the green targeting box. "
         "If the code is a printed label, make sure it isn't crumpled or smudged. "
         "You can also manually type the Tag ID into the entry field and press Enter."),
        (False, "Why can't I see the 'Add Tool' form in the Inventory module?",
         "Only Admin accounts have access to add, edit, or archive tools. "
         "Staff accounts have view-only access. Contact your system administrator to update your role if needed."),
        (False, "A tool shows 'Unassigned' in the Tag ID column. Can it still be borrowed?",
         "Yes — untagged tools can still be borrowed if they have available stock. "
         "However, assigning a Tag ID first through the Tagging module is recommended for accurate scanning and tracking."),
        (False, "I forgot my password. How do I reset it?",
         "On the login screen, click 'Forgot Password?' and enter your Employee ID and registered email address. "
         "If they match, you will be prompted to set a new password. If you have no registered email, contact your Admin."),
        (False, "Can I borrow multiple tools at once?",
         "Yes. On the Borrowing & Return screen, scan your Employee ID first, then scan each tool's tag one by one. "
         "Each scan adds it to the cart. Confirm the checkout when all tools are in the cart."),
        (True, "What happens when I 'Archive' a tool?",
         "Archiving removes the tool from the active inventory list but does not delete it or its transaction history. "
         "Archived tools can be viewed and restored in Maintenance → Archived Tools."),
        (False, "Can I return only some of the tools I borrowed?",
         "Yes. On the Return panel, scan your Employee ID and the Tool Tag or TRN, then set the Qty field to the number "
         "you want to return (up to the total amount you currently have checked out for that tool)."),
        (False, "What is ABC Analysis in the Reports module?",
         "ABC Analysis applies the Pareto (80/20) principle to tool borrowing data. Category A tools are the top 20% most "
         "frequently borrowed and need the strictest monitoring. Category B is the middle tier, and Category C are the "
         "least-used tools which typically need minimal reorder attention."),
        (True, "How do I back up data, and where is the backup file saved?",
         "Go to Maintenance → Backup Data, select the tables to include, click 'Select Backup Destination & Export', "
         "and choose a folder on your computer. The file is saved as a timestamped .json file."),
        (False, "Is my password stored securely?",
         "Yes. All passwords are hashed using bcrypt before being stored in the database. "
         "The original password is never saved — even administrators cannot view it. "
         "This complies with the Philippines' Data Privacy Act of 2012 (RA 10173)."),
    ]

    def __init__(self, parent, user_info=None):
        super().__init__(parent, fg_color="transparent")

        self.user_info = user_info or {}
        self.is_admin = self.user_info.get("role", "Staff") == "Admin"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.build_ui()

    def build_ui(self):
        tab_bar = ctk.CTkFrame(self, fg_color="white",
                               corner_radius=10, height=50)
        tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tab_bar.grid_propagate(False)

        self.tab_content = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_content.grid(row=1, column=0, sticky="nsew")
        self.tab_content.grid_columnconfigure(0, weight=1)
        self.tab_content.grid_rowconfigure(0, weight=1)

        tabs = [("Help Guide", "guide"), ("FAQs", "faq"),
                ("System Requirements", "sysreq")]

        self.tab_buttons = {}
        for text, key in tabs:
            btn = ctk.CTkButton(
                tab_bar, text=text,
                fg_color="#1E4528" if key == "guide" else "transparent",
                text_color="white" if key == "guide" else "#1A1A1A",
                hover_color="#2A6038", font=("Inter", 12, "bold"),
                command=lambda k=key: self.switch_tab(k, tabs)
            )
            btn.pack(side="left", padx=10, pady=8)
            self.tab_buttons[key] = btn

        self.render_guide_tab()

    def switch_tab(self, key, tabs):
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        for _, k in tabs:
            btn = self.tab_buttons.get(k)
            if btn:
                btn.configure(
                    fg_color="#1E4528" if k == key else "transparent",
                    text_color="white" if k == key else "#1A1A1A"
                )
        if key == "guide":
            self.render_guide_tab()
        elif key == "faq":
            self.render_faq_tab()
        elif key == "sysreq":
            self.render_sysreq_tab()

    # ==========================================
    # Shared: keyword search bar builder
    # ==========================================
    def _build_search_bar(self, parent, on_search, placeholder="Search keywords..."):
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(12, 4))
        entry = ctk.CTkEntry(bar, placeholder_text=placeholder, width=300)
        entry.pack(side="left", padx=(0, 8))
        entry.bind("<Return>", lambda e: on_search(entry.get().strip()))
        ctk.CTkButton(bar, text="Search", width=75, fg_color="#1E4528",
                      hover_color="#14301C", font=("Inter", 11, "bold"),
                      command=lambda: on_search(entry.get().strip())).pack(side="left", padx=(0, 6))
        ctk.CTkButton(bar, text="↻ Clear", width=70, fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC",
                      command=lambda: [entry.delete(0, "end"), on_search("")]).pack(side="left")
        return entry

    # ------------------------------------------
    # Linear keyword search algorithm (O(n))
    # Scans title + each bullet point for the keyword.
    # Returns True if any text contains the keyword (case-insensitive).
    # Consistent with the simple, practical algorithms described in Ch.3.
    # ------------------------------------------
    @staticmethod
    def _section_matches(title, points, keyword):
        kw = keyword.lower()
        if kw in title.lower():
            return True
        for p in points:
            if kw in p.lower():
                return True
        return False

    # ==========================================
    # HELP GUIDE TAB
    # ==========================================
    def render_guide_tab(self):
        outer = ctk.CTkFrame(
            self.tab_content, fg_color="white", corner_radius=10)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # Header
        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        ctk.CTkLabel(hdr, text="User Guide — Automated Management System",
                     font=("Inter", 18, "bold"), text_color="#1E4528").pack(side="left")

        self._guide_search_entry = self._build_search_bar(
            outer, self._filter_guide, "Search guide sections..."
        )

        # Scrollable content
        self._guide_scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent")
        self._guide_scroll.pack(
            fill="both", expand=True, padx=10, pady=(0, 10))

        self._render_guide_sections("")

    def _filter_guide(self, keyword):
        self._render_guide_sections(keyword)

    def _render_guide_sections(self, keyword):
        scroll = self._guide_scroll
        for w in scroll.winfo_children():
            w.destroy()

        found_any = False
        for admin_only, title, points in self.GUIDE_SECTIONS:
            # Skip admin-only sections for staff
            if admin_only and not self.is_admin:
                continue
            # Keyword filter — linear scan
            if keyword and not self._section_matches(title, points, keyword):
                continue

            found_any = True
            card = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=8)
            card.pack(fill="x", padx=10, pady=(0, 6))

            ctk.CTkLabel(card, text=title, font=("Inter", 12, "bold"),
                         text_color="#1E4528").pack(anchor="w", padx=14, pady=(8, 3))
            for point in points:
                ctk.CTkLabel(card, text=f"  •  {point}",
                             font=("Inter", 11), text_color="#1A1A1A",
                             wraplength=780, justify="left").pack(anchor="w", padx=14, pady=1)
            # compact bottom spacer
            ctk.CTkFrame(card, height=6, fg_color="transparent").pack()

        if not found_any:
            ctk.CTkLabel(scroll, text=f'No sections found for "{keyword}".',
                         text_color="gray").pack(pady=20)

    # ==========================================
    # FAQs TAB
    # ==========================================
    def render_faq_tab(self):
        outer = ctk.CTkFrame(
            self.tab_content, fg_color="white", corner_radius=10)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(outer, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        ctk.CTkLabel(hdr, text="Frequently Asked Questions",
                     font=("Inter", 18, "bold"), text_color="#1E4528").pack(side="left")

        self._build_search_bar(outer, self._filter_faq, "Search FAQs...")

        self._faq_scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent")
        self._faq_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._render_faq_items("")

    def _filter_faq(self, keyword):
        self._render_faq_items(keyword)

    def _render_faq_items(self, keyword):
        scroll = self._faq_scroll
        for w in scroll.winfo_children():
            w.destroy()

        idx = 1
        found_any = False
        for admin_only, q, a in self.FAQS:
            if admin_only and not self.is_admin:
                continue
            if keyword and not self._section_matches(q, [a], keyword):
                continue

            found_any = True
            card = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=8)
            card.pack(fill="x", padx=10, pady=(0, 6))

            ctk.CTkLabel(card, text=f"Q{idx}.  {q}",
                         font=("Inter", 11, "bold"), text_color="#1E4528",
                         wraplength=780, justify="left").pack(anchor="w", padx=14, pady=(10, 2))
            ctk.CTkLabel(card, text=f"      {a}",
                         font=("Inter", 11), text_color="#1A1A1A",
                         wraplength=780, justify="left").pack(anchor="w", padx=14, pady=(0, 10))
            idx += 1

        if not found_any:
            ctk.CTkLabel(scroll, text=f'No FAQs found for "{keyword}".',
                         text_color="gray").pack(pady=20)

    # ==========================================
    # SYSTEM REQUIREMENTS TAB
    # ==========================================
    def render_sysreq_tab(self):
        frame = ctk.CTkScrollableFrame(
            self.tab_content, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(frame, text="System Requirements",
                     font=("Inter", 18, "bold"), text_color="#1E4528").pack(
            anchor="w", padx=20, pady=(16, 10))

        hardware_specs = [
            ("Processor",        "Intel Core i7 or equivalent (64-bit)"),
            ("RAM",              "Minimum 8 GB"),
            ("Storage",          "At least 500 MB free disk space"),
            ("Operating System", "Windows 10 (64-bit) — recommended and tested"),
            ("Display",          "Minimum 1280×720 resolution (1920×1080 recommended)"),
            ("Webcam",           "HD Webcam 1080P — required for QR scanning features"),
            ("Printer",
             "Any standard printer — required for label and receipt printing"),
            ("Network",          "LAN connection for database access (no internet required)"),
        ]
        software_specs = [
            ("Python",            "3.11"),
            ("Database",          "MySQL 8.0"),
            ("GUI Framework",     "Tkinter 8.6 + CustomTkinter 5.2.2"),
            ("IDE (Dev)",         "PyCharm Community Edition 2023.3"),
            ("QR Code Library",   "qrcode, pyzbar"),
            ("Image Processing",  "Pillow (PIL)"),
            ("CV Scanner",        "OpenCV (cv2)"),
            ("Password Hashing",  "bcrypt"),
        ]

        def render_table(parent, title, specs):
            ctk.CTkLabel(parent, text=title, font=("Inter", 13, "bold"),
                         text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(6, 4))
            card = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=8)
            card.pack(fill="x", padx=20, pady=(0, 12))
            for i, (label, val) in enumerate(specs):
                row = ctk.CTkFrame(card, fg_color="#F0F0F0" if i %
                                   2 == 0 else "#F9FAFB", height=34)
                row.pack(fill="x")
                row.pack_propagate(False)
                row.grid_columnconfigure(0, weight=1)
                row.grid_columnconfigure(1, weight=2)
                ctk.CTkLabel(row, text=label, font=("Inter", 11, "bold"),
                             text_color="#555555").grid(row=0, column=0, padx=14, pady=6, sticky="w")
                ctk.CTkLabel(row, text=val, font=("Inter", 11),
                             text_color="#1A1A1A").grid(row=0, column=1, padx=14, pady=6, sticky="w")

        render_table(frame, "Hardware Requirements", hardware_specs)
        render_table(frame, "Software Requirements", software_specs)

        ctk.CTkLabel(
            frame,
            text="Note: The system is a LAN-based desktop application. No internet connection is required "
                 "for normal operation. All data is stored locally in the MySQL database.",
            font=("Inter", 11), text_color="gray", wraplength=780, justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 20))
