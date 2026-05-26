import customtkinter as ctk
from tkinter import messagebox
from database import get_connection


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
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(top_bar, text="Help & Support Hub", font=("Inter", 20, "bold"), text_color="#1A1A1A").pack(side="left", padx=20)

        tabs = ["Help Guide", "FAQs", "System Requirements", "Support Tickets"]
        self.tab_var = ctk.StringVar(value=tabs[0])
        
        self.seg_btn = ctk.CTkSegmentedButton(
            top_bar, values=tabs, variable=self.tab_var, command=self.switch_tab,
            fg_color="#F0F0F0", selected_color="#1E4528", selected_hover_color="#14301C"
        )
        self.seg_btn.pack(side="right", padx=20)
        self.seg_btn.set(tabs[0])

        self.tab_content = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.tab_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.tab_content.grid_columnconfigure(0, weight=1)
        self.tab_content.grid_rowconfigure(0, weight=1)
        
        self.switch_tab(tabs[0])

    def switch_tab(self, selected_tab):
        for widget in self.tab_content.winfo_children(): widget.destroy()
        if selected_tab == "Help Guide": self.render_guide_tab()
        elif selected_tab == "FAQs": self.render_faq_tab()
        elif selected_tab == "System Requirements": self.render_sysreq_tab()
        elif selected_tab == "Support Tickets": self.render_tickets_tab()

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

    # ==========================================
    # SUPPORT TICKETS TAB
    # ==========================================
    def render_tickets_tab(self):
        frame = ctk.CTkFrame(self.tab_content, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Auto-create the table if it doesn't exist
        conn = get_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS help_tickets (
                    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    subject VARCHAR(255),
                    message TEXT,
                    admin_reply TEXT,
                    status VARCHAR(50) DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
                conn.commit()
            except Exception: pass
            finally:
                if conn.is_connected(): c.close(); conn.close()

        # --- STAFF VIEW: Form to submit ---
        if not self.is_admin:
            form_bg = ctk.CTkFrame(frame, fg_color="#F9FAFB", corner_radius=10)
            form_bg.pack(fill="x", padx=20, pady=(20, 10))
            
            ctk.CTkLabel(form_bg, text="Submit an Inquiry", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=15, pady=(15, 5))
            
            subj_entry = ctk.CTkEntry(form_bg, placeholder_text="Subject...")
            subj_entry.pack(fill="x", padx=15, pady=5)
            
            msg_entry = ctk.CTkTextbox(form_bg, height=60)
            msg_entry.pack(fill="x", padx=15, pady=5)
            
            def submit_ticket():
                subj = subj_entry.get().strip()
                msg = msg_entry.get("1.0", "end-1c").strip()
                if not subj or not msg:
                    messagebox.showerror("Error", "Subject and message required.", parent=self.winfo_toplevel())
                    return
                
                db = get_connection()
                if db:
                    c = db.cursor()
                    c.execute("INSERT INTO help_tickets (user_id, subject, message) VALUES (%s, %s, %s)", (self.user_info['user_id'], subj, msg))
                    db.commit(); c.close(); db.close()
                    messagebox.showinfo("Success", "Ticket submitted to the Admin.", parent=self.winfo_toplevel())
                    subj_entry.delete(0, 'end'); msg_entry.delete("1.0", "end")
                    load_ticket_list()

            ctk.CTkButton(form_bg, text="Send to Admin", fg_color="#1E4528", hover_color="#14301C", command=submit_ticket).pack(anchor="e", padx=15, pady=(5, 15))

        # --- LIST VIEW (Shared) ---
        ctk.CTkLabel(frame, text="Ticket Inbox" if self.is_admin else "My Previous Tickets", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(10, 5))
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def load_ticket_list():
            for w in scroll.winfo_children(): w.destroy()
            db = get_connection()
            if not db: return
            try:
                c = db.cursor(dictionary=True)
                if self.is_admin:
                    c.execute("SELECT h.*, u.full_name FROM help_tickets h JOIN user u ON h.user_id = u.user_id ORDER BY h.status ASC, h.created_at DESC")
                else:
                    c.execute("SELECT h.*, u.full_name FROM help_tickets h JOIN user u ON h.user_id = u.user_id WHERE h.user_id = %s ORDER BY h.created_at DESC", (self.user_info['user_id'],))
                
                for t in c.fetchall():
                    card = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=8, border_width=1, border_color="#E0E0E0")
                    card.pack(fill="x", pady=5)
                    
                    header = ctk.CTkFrame(card, fg_color="transparent")
                    header.pack(fill="x", padx=15, pady=(10, 5))
                    
                    status_col = "#D8000C" if t['status'] == 'Open' else "#2ECC71"
                    ctk.CTkLabel(header, text=f"[{t['status']}]", font=("Inter", 12, "bold"), text_color=status_col).pack(side="left", padx=(0, 10))
                    ctk.CTkLabel(header, text=t['subject'], font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(side="left")
                    if self.is_admin:
                        ctk.CTkLabel(header, text=f"From: {t['full_name']}", font=("Inter", 11), text_color="gray").pack(side="right")
                        
                    ctk.CTkLabel(card, text=t['message'], font=("Inter", 11), text_color="#555555", justify="left", wraplength=700).pack(anchor="w", padx=15, pady=5)
                    
                    if t['admin_reply']:
                        reply_box = ctk.CTkFrame(card, fg_color="#E8F8F5", corner_radius=5)
                        reply_box.pack(fill="x", padx=15, pady=(5, 10))
                        ctk.CTkLabel(reply_box, text=f"Admin Reply: {t['admin_reply']}", font=("Inter", 11, "bold"), text_color="#1E4528", justify="left", wraplength=650).pack(anchor="w", padx=10, pady=10)
                    elif self.is_admin and t['status'] == 'Open':
                        # Admin Reply mechanism
                        reply_entry = ctk.CTkEntry(card, placeholder_text="Type reply here...")
                        reply_entry.pack(fill="x", padx=15, pady=5)
                        
                        def send_reply(tid=t['ticket_id'], e=reply_entry):
                            rep = e.get().strip()
                            if not rep: return
                            cx = get_connection()
                            cur = cx.cursor()
                            cur.execute("UPDATE help_tickets SET admin_reply = %s, status = 'Resolved' WHERE ticket_id = %s", (rep, tid))
                            cx.commit(); cur.close(); cx.close()
                            load_ticket_list()
                            
                        ctk.CTkButton(card, text="Reply & Resolve", width=120, height=28, fg_color="#3498DB", hover_color="#2980B9", command=send_reply).pack(anchor="e", padx=15, pady=(0, 10))
            except Exception: pass
            finally:
                if db.is_connected(): c.close(); db.close()
                
        load_ticket_list()