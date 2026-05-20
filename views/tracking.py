import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
from datetime import datetime


class TrackingView(ctk.CTkFrame):
    def __init__(self, parent, user_info=None):
        super().__init__(parent, fg_color="transparent")

        self.user_info = user_info or {}
        self.is_admin = self.user_info.get("role", "Staff") == "Admin"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        if self.is_admin:
            self.build_admin_view()
        else:
            self.build_staff_view()

    # ==========================================
    # ADMIN VIEW: Full Audit Trail + Issue Mgmt
    # ==========================================
    def build_admin_view(self):
        notebook_frame = ctk.CTkFrame(self, fg_color="transparent")
        notebook_frame.grid(row=0, column=0, sticky="nsew")
        notebook_frame.grid_columnconfigure(0, weight=1)
        notebook_frame.grid_rowconfigure(1, weight=1)

        # Tab bar
        tab_bar = ctk.CTkFrame(
            notebook_frame, fg_color="white", corner_radius=10, height=50)
        tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tab_bar.pack_propagate(False)

        self.active_tab = ctk.StringVar(value="logs")

        self.tab_content = ctk.CTkFrame(notebook_frame, fg_color="transparent")
        self.tab_content.grid(row=1, column=0, sticky="nsew")
        self.tab_content.grid_columnconfigure(0, weight=1)
        self.tab_content.grid_rowconfigure(0, weight=1)

        tabs = [
            ("Borrow/Return Logs", "logs"),
            ("Audit Records", "audit"),
            ("Manage Issues", "issues"),
        ]

        for text, key in tabs:
            ctk.CTkButton(
                tab_bar, text=text,
                fg_color="#1E4528" if key == "logs" else "transparent",
                text_color="white" if key == "logs" else "#1A1A1A",
                hover_color="#2A6038",
                font=("Inter", 12, "bold"),
                command=lambda k=key: self.switch_tab(k, tabs)
            ).pack(side="left", padx=10, pady=8)

        self.tab_buttons = {key: tab_bar.winfo_children(
        )[i] for i, (_, key) in enumerate(tabs)}
        self.render_logs_tab()

    def switch_tab(self, key, tabs):
        self.active_tab.set(key)
        for widget in self.tab_content.winfo_children():
            widget.destroy()

        for text, k in tabs:
            btn = self.tab_buttons.get(k)
            if btn:
                if k == key:
                    btn.configure(fg_color="#1E4528", text_color="white")
                else:
                    btn.configure(fg_color="transparent", text_color="#1A1A1A")

        if key == "logs":
            self.render_logs_tab()
        elif key == "audit":
            self.render_audit_tab()
        elif key == "issues":
            self.render_issues_tab()

    def render_logs_tab(self):
        frame = ctk.CTkFrame(
            self.tab_content, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Header & search
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top, text="Borrow / Return Transaction Logs",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")

        self.log_search = ctk.CTkEntry(
            top, placeholder_text="Search employee or tool...", width=220)
        self.log_search.pack(side="right", padx=(10, 0))
        self.log_search.bind("<Return>", lambda e: self.load_logs(frame))

        ctk.CTkButton(top, text="Search", width=70, fg_color="#1E4528",
                      hover_color="#14301C", font=("Inter", 11, "bold"),
                      command=lambda: self.load_logs(frame)).pack(side="right", padx=5)
        ctk.CTkButton(top, text="↻", width=40, fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC",
                      command=lambda: [self.log_search.delete(0, "end"), self.load_logs(frame)]).pack(side="right")

        # Table header
        headers = ["TRN", "Type", "Tool Name", "Tag ID", "Qty",
                   "Borrower", "Borrow Date", "Return Date", "Status"]
        weights = [1, 1, 2, 2, 1, 2, 2, 2, 1]

        hdr = ctk.CTkFrame(frame, fg_color="#1E4528",
                           corner_radius=5, height=38)
        hdr.pack(fill="x", padx=20)
        hdr.pack_propagate(False)

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=8, pady=8, sticky="w")

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self._log_scroll = scroll
        self._log_weights = weights

        self.load_logs(frame)

    def load_logs(self, frame=None):
        scroll = self._log_scroll
        weights = self._log_weights

        for w in scroll.winfo_children():
            w.destroy()

        q = self.log_search.get().strip() if hasattr(self, "log_search") else ""
        conn = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT tr.transaction_id, tr.type, t.name as tool_name,
                       IFNULL(t.tag_id,'Unassigned') as tag_id,
                       1 as qty,
                       u.full_name,
                       DATE_FORMAT(DATE_ADD(tr.borrow_date, INTERVAL 8 HOUR),
                           '%%b %%d %%Y %%h:%%i%%p') as borrow_date,
                       IF(tr.return_date IS NOT NULL,
                           DATE_FORMAT(DATE_ADD(tr.return_date, INTERVAL 8 HOUR),
                               '%%b %%d %%Y %%h:%%i%%p'), '—') as return_date,
                       tr.status
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                JOIN user u ON tr.user_id = u.user_id
            """
            params = []
            if q:
                sql += " WHERE u.full_name LIKE %s OR t.name LIKE %s OR t.tag_id LIKE %s"
                params = [f"%{q}%", f"%{q}%", f"%{q}%"]
            sql += " ORDER BY tr.borrow_date DESC LIMIT 100"
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            if not rows:
                ctk.CTkLabel(scroll, text="No transaction records found.",
                             text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(rows):
                vals = [
                    str(row["transaction_id"]),
                    row["type"],
                    row["tool_name"],
                    row["tag_id"],
                    str(row["qty"]),
                    row["full_name"],
                    row["borrow_date"],
                    row["return_date"],
                    row["status"],
                ]
                rf = ctk.CTkFrame(scroll,
                                  fg_color="#F9FAFB" if i % 2 == 0 else "white",
                                  height=36)
                rf.pack(fill="x", pady=1)
                rf.pack_propagate(False)

                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    color = "#1A1A1A"
                    if col == 8:
                        color = "#D8000C" if val == "Active" else "#2ECC71"
                    ctk.CTkLabel(rf, text=val, font=("Inter", 11),
                                 text_color=color).grid(
                        row=0, column=col, padx=8, pady=6, sticky="w")

        except Exception as e:
            ctk.CTkLabel(
                scroll, text=f"Error: {e}", text_color="red").pack(pady=10)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def render_audit_tab(self):
        frame = ctk.CTkFrame(
            self.tab_content, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top, text="Audit Trail — Borrow & Return Records",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")

        # Filter row
        filter_row = ctk.CTkFrame(frame, fg_color="transparent")
        filter_row.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(filter_row, text="Filter by Status:",
                     font=("Inter", 12), text_color="gray").pack(side="left")
        self.audit_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "Active", "Returned", "Overdue"],
            width=130, fg_color="#F9FAFB", text_color="black"
        )
        self.audit_filter.pack(side="left", padx=10)

        self.audit_search = ctk.CTkEntry(filter_row,
                                         placeholder_text="Search name / tool...", width=200)
        self.audit_search.pack(side="left", padx=(0, 5))
        self.audit_search.bind("<Return>", lambda e: self.load_audit())

        ctk.CTkButton(filter_row, text="Run Audit", width=80,
                      fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D",
                      font=("Inter", 11, "bold"),
                      command=self.load_audit).pack(side="left", padx=5)
        ctk.CTkButton(filter_row, text="↻ Reset", width=70,
                      fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC",
                      command=lambda: [self.audit_search.delete(0, "end"),
                                       self.audit_filter.set("All"),
                                       self.load_audit()]).pack(side="left")

        # Summary strip
        self.audit_summary = ctk.CTkLabel(
            frame, text="", font=("Inter", 11, "bold"), text_color="#1E4528"
        )
        self.audit_summary.pack(anchor="w", padx=20, pady=(0, 5))

        headers = ["TRN", "Borrower", "Tool", "Tag ID", "Borrowed On",
                   "Return Date", "Condition @ Borrow", "Condition @ Return", "Status"]
        weights = [1, 2, 2, 2, 2, 2, 2, 2, 1]

        hdr = ctk.CTkFrame(frame, fg_color="#1E4528",
                           corner_radius=5, height=38)
        hdr.pack(fill="x", padx=20)
        hdr.pack_propagate(False)

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=8, pady=8, sticky="w")

        self._audit_scroll = ctk.CTkScrollableFrame(
            frame, fg_color="transparent")
        self._audit_scroll.pack(
            fill="both", expand=True, padx=20, pady=(5, 20))
        self._audit_weights = weights

        self.load_audit()

    def load_audit(self):
        scroll = self._audit_scroll
        weights = self._audit_weights

        for w in scroll.winfo_children():
            w.destroy()

        status_filter = self.audit_filter.get() if hasattr(
            self, "audit_filter") else "All"
        q = self.audit_search.get().strip() if hasattr(self, "audit_search") else ""

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT tr.transaction_id,
                       u.full_name,
                       t.name as tool_name,
                       IFNULL(t.tag_id,'Unassigned') as tag_id,
                       DATE_FORMAT(DATE_ADD(tr.borrow_date, INTERVAL 8 HOUR),
                           '%%b %%d %%Y %%h:%%i%%p') as borrow_date,
                       IF(tr.return_date IS NOT NULL,
                           DATE_FORMAT(DATE_ADD(tr.return_date, INTERVAL 8 HOUR),
                               '%%b %%d %%Y %%h:%%i%%p'), '—') as return_date,
                       IFNULL(tr.condition_at_borrow,'N/A') as cond_borrow,
                       IFNULL(tr.condition_at_return,'N/A') as cond_return,
                       tr.status
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                JOIN user u ON tr.user_id = u.user_id
                WHERE 1=1
            """
            params = []
            if status_filter != "All":
                sql += " AND tr.status = %s"
                params.append(status_filter)
            if q:
                sql += " AND (u.full_name LIKE %s OR t.name LIKE %s)"
                params += [f"%{q}%", f"%{q}%"]
            sql += " ORDER BY tr.borrow_date DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            total = len(rows)
            active = sum(1 for r in rows if r["status"] == "Active")
            returned = sum(1 for r in rows if r["status"] == "Returned")
            self.audit_summary.configure(
                text=f"  Total Records: {total}   |   Active: {active}   |   Returned: {returned}"
            )

            if not rows:
                ctk.CTkLabel(scroll, text="No records match the audit criteria.",
                             text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(rows):
                vals = [
                    str(row["transaction_id"]),
                    row["full_name"],
                    row["tool_name"],
                    row["tag_id"],
                    row["borrow_date"],
                    row["return_date"],
                    row["cond_borrow"],
                    row["cond_return"],
                    row["status"],
                ]
                rf = ctk.CTkFrame(scroll,
                                  fg_color="#FFF8F0" if row["status"] == "Active" else (
                                      "#F9FAFB" if i % 2 == 0 else "white"),
                                  height=36)
                rf.pack(fill="x", pady=1)
                rf.pack_propagate(False)

                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    color = "#1A1A1A"
                    if col == 8:
                        color = "#D8000C" if val == "Active" else "#2ECC71"
                    ctk.CTkLabel(rf, text=val, font=("Inter", 11),
                                 text_color=color).grid(
                        row=0, column=col, padx=8, pady=6, sticky="w")

        except Exception as e:
            ctk.CTkLabel(
                scroll, text=f"Error: {e}", text_color="red").pack(pady=10)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def render_issues_tab(self):
        frame = ctk.CTkFrame(
            self.tab_content, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top, text="Tool Issue Management",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")

        # Flag form
        flag_card = ctk.CTkFrame(frame, fg_color="#F9FAFB", corner_radius=8)
        flag_card.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(flag_card, text="Flag a Tool for Review",
                     font=("Inter", 13, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=15, pady=(12, 5))

        row1 = ctk.CTkFrame(flag_card, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(0, 5))
        row1.grid_columnconfigure((0, 1, 2), weight=1)

        self.flag_tool_id = ctk.CTkEntry(
            row1, placeholder_text="Tool PID or Tag ID")
        self.flag_tool_id.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.flag_reported_by = ctk.CTkEntry(
            row1, placeholder_text="Reported By (Employee ID)")
        self.flag_reported_by.grid(row=0, column=1, padx=5, sticky="ew")

        self.flag_condition = ctk.CTkOptionMenu(
            row1,
            values=["Damaged", "Lost", "Needs Repair", "Discrepancy"],
            fg_color="#F9FAFB", text_color="black"
        )
        self.flag_condition.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        self.flag_notes = ctk.CTkEntry(flag_card,
                                       placeholder_text="Notes / Description of issue...")
        self.flag_notes.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(flag_card, text="Submit Flag",
                      fg_color="#D8000C", hover_color="#B00000",
                      text_color="white", font=("Inter", 11, "bold"),
                      command=self.submit_flag).pack(anchor="e", padx=15, pady=(0, 12))

        # Issues table
        headers = ["Issue ID", "Tool", "Reported By",
                   "Condition", "Notes", "Flagged At", "Resolved"]
        weights = [1, 2, 2, 2, 3, 2, 1]

        hdr = ctk.CTkFrame(frame, fg_color="#1E4528",
                           corner_radius=5, height=38)
        hdr.pack(fill="x", padx=20)
        hdr.pack_propagate(False)

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=8, pady=8, sticky="w")

        self._issues_scroll = ctk.CTkScrollableFrame(
            frame, fg_color="transparent")
        self._issues_scroll.pack(
            fill="both", expand=True, padx=20, pady=(5, 20))
        self._issues_weights = weights

        self.load_issues()

    def submit_flag(self):
        tool_input = self.flag_tool_id.get().strip()
        reported_by = self.flag_reported_by.get().strip()
        condition = self.flag_condition.get()
        notes = self.flag_notes.get().strip()

        if not tool_input or not reported_by:
            messagebox.showerror("Error", "Tool ID/Tag and Reported By are required.",
                                 parent=self.winfo_toplevel())
            return

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)

            # Resolve tool_id from PID or tag
            if tool_input.isdigit():
                cursor.execute(
                    "SELECT tool_id, name FROM tool WHERE tool_id = %s", (tool_input,))
            else:
                cursor.execute(
                    "SELECT tool_id, name FROM tool WHERE tag_id = %s", (tool_input,))
            tool = cursor.fetchone()

            if not tool:
                messagebox.showerror("Not Found",
                                     "No tool found with that PID or Tag ID.",
                                     parent=self.winfo_toplevel())
                return

            # Check if tool_issues table exists; if not, create it inline
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_issues (
                    issue_id INT AUTO_INCREMENT PRIMARY KEY,
                    tool_id INT NOT NULL,
                    reported_by VARCHAR(100),
                    condition_flag VARCHAR(100),
                    notes TEXT,
                    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_resolved TINYINT(1) DEFAULT 0,
                    FOREIGN KEY (tool_id) REFERENCES tool(tool_id)
                )
            """)

            cursor.execute("""
                INSERT INTO tool_issues (tool_id, reported_by, condition_flag, notes)
                VALUES (%s, %s, %s, %s)
            """, (tool["tool_id"], reported_by, condition, notes))

            # Also update tool condition
            cursor.execute("UPDATE tool SET `condition` = %s WHERE tool_id = %s",
                           (condition, tool["tool_id"]))
            conn.commit()

            messagebox.showinfo("Flagged",
                                f"Tool '{tool['name']}' has been flagged for review.",
                                parent=self.winfo_toplevel())

            self.flag_tool_id.delete(0, "end")
            self.flag_reported_by.delete(0, "end")
            self.flag_notes.delete(0, "end")
            self.load_issues()

        except Exception as e:
            messagebox.showerror("Database Error", str(e),
                                 parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def load_issues(self):
        scroll = self._issues_scroll
        weights = self._issues_weights

        for w in scroll.winfo_children():
            w.destroy()

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)

            # Ensure table exists before querying
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_issues (
                    issue_id INT AUTO_INCREMENT PRIMARY KEY,
                    tool_id INT NOT NULL,
                    reported_by VARCHAR(100),
                    condition_flag VARCHAR(100),
                    notes TEXT,
                    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_resolved TINYINT(1) DEFAULT 0,
                    FOREIGN KEY (tool_id) REFERENCES tool(tool_id)
                )
            """)

            cursor.execute("""
                SELECT ti.issue_id, t.name as tool_name, ti.reported_by,
                       ti.condition_flag,
                       IFNULL(ti.notes,'—') as notes,
                       DATE_FORMAT(DATE_ADD(ti.flagged_at, INTERVAL 8 HOUR),
                           '%%b %%d %%Y %%h:%%i%%p') as flagged_at,
                       ti.is_resolved
                FROM tool_issues ti
                JOIN tool t ON ti.tool_id = t.tool_id
                ORDER BY ti.flagged_at DESC
            """)
            rows = cursor.fetchall()

            if not rows:
                ctk.CTkLabel(scroll, text="No issues flagged yet.",
                             text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(rows):
                resolved_text = "✓ Yes" if row["is_resolved"] else "Pending"
                vals = [
                    str(row["issue_id"]),
                    row["tool_name"],
                    row["reported_by"],
                    row["condition_flag"],
                    row["notes"],
                    row["flagged_at"],
                    resolved_text,
                ]
                rf = ctk.CTkFrame(scroll,
                                  fg_color="#F9FAFB" if i % 2 == 0 else "white",
                                  height=36)
                rf.pack(fill="x", pady=1)
                rf.pack_propagate(False)
                rf.bind("<Button-1>",
                        lambda e, r=row: self.open_issue_modal(r))

                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    color = "#2ECC71" if col == 6 and "Yes" in val else (
                        "#D8000C" if col == 6 else "#1A1A1A")
                    lbl = ctk.CTkLabel(rf, text=val, font=("Inter", 11),
                                       text_color=color)
                    lbl.grid(row=0, column=col, padx=8, pady=6, sticky="w")
                    lbl.bind("<Button-1>", lambda e,
                             r=row: self.open_issue_modal(r))

        except Exception as e:
            ctk.CTkLabel(
                scroll, text=f"Error: {e}", text_color="red").pack(pady=10)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def open_issue_modal(self, row):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Issue #{row['issue_id']} — {row['tool_name']}")
        modal.geometry("420x340")
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - 210
        y = (modal.winfo_screenheight() // 2) - 170
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"Manage Issue #{row['issue_id']}",
                     font=("Inter", 15, "bold"), text_color="black").pack(pady=(20, 5))
        ctk.CTkLabel(modal, text=f"Tool: {row['tool_name']}  |  Reported by: {row['reported_by']}",
                     font=("Inter", 12), text_color="gray").pack(pady=(0, 15))

        form = ctk.CTkFrame(modal, fg_color="transparent")
        form.pack(fill="x", padx=30)

        ctk.CTkLabel(form, text="Update Condition:", font=("Inter", 11, "bold"),
                     text_color="#1A1A1A").pack(anchor="w")
        cond_menu = ctk.CTkOptionMenu(form, values=["Good", "Needs Repair", "Damaged", "Lost"],
                                      fg_color="#F9FAFB", text_color="black")
        cond_menu.set(row["condition_flag"])
        cond_menu.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(form, text="Admin Notes:", font=("Inter", 11, "bold"),
                     text_color="#1A1A1A").pack(anchor="w")
        notes_entry = ctk.CTkEntry(
            form, placeholder_text="Resolution notes...")
        notes_entry.pack(fill="x", pady=(5, 15))

        def resolve_issue():
            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tool_issues
                    SET is_resolved = 1,
                        condition_flag = %s,
                        notes = CONCAT(IFNULL(notes,''), ' | Admin: ', %s)
                    WHERE issue_id = %s
                """, (cond_menu.get(), notes_entry.get().strip() or "Resolved", row["issue_id"]))

                # Sync tool condition
                cursor.execute("UPDATE tool SET `condition` = %s WHERE tool_id = (SELECT tool_id FROM tool_issues WHERE issue_id = %s)",
                               (cond_menu.get(), row["issue_id"]))
                conn.commit()
                messagebox.showinfo("Updated", "Issue marked as resolved.",
                                    parent=modal)
                modal.destroy()
                self.load_issues()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkButton(btn_row, text="Mark Resolved", fg_color="#1E4528",
                      hover_color="#14301C", command=resolve_issue).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Close", fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC",
                      command=modal.destroy).pack(side="right")

    # ==========================================
    # STAFF VIEW: Personal history only
    # ==========================================
    def build_staff_view(self):
        frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top, text="My Borrowing & Return History",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")

        ctk.CTkLabel(frame,
                     text="Showing transactions associated with your account only.",
                     font=("Inter", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))

        headers = ["TRN", "Tool Name", "Tag ID", "Borrow Date", "Return Date",
                   "Condition @ Return", "Status"]
        weights = [1, 2, 2, 2, 2, 2, 1]

        hdr = ctk.CTkFrame(frame, fg_color="#1E4528",
                           corner_radius=5, height=38)
        hdr.pack(fill="x", padx=20)
        hdr.pack_propagate(False)

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=8, pady=8, sticky="w")

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        user_id = self.user_info.get("user_id")
        if not user_id:
            ctk.CTkLabel(scroll, text="User session error.",
                         text_color="red").pack(pady=20)
            return

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT tr.transaction_id, t.name as tool_name,
                       IFNULL(t.tag_id,'Unassigned') as tag_id,
                       DATE_FORMAT(DATE_ADD(tr.borrow_date, INTERVAL 8 HOUR),
                           '%%b %%d %%Y %%h:%%i%%p') as borrow_date,
                       IF(tr.return_date IS NOT NULL,
                           DATE_FORMAT(DATE_ADD(tr.return_date, INTERVAL 8 HOUR),
                               '%%b %%d %%Y %%h:%%i%%p'), '—') as return_date,
                       IFNULL(tr.condition_at_return,'—') as cond_return,
                       tr.status
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                WHERE tr.user_id = %s
                ORDER BY tr.borrow_date DESC
            """, (user_id,))
            rows = cursor.fetchall()

            if not rows:
                ctk.CTkLabel(scroll, text="You have no borrowing history.",
                             text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(rows):
                vals = [
                    str(row["transaction_id"]),
                    row["tool_name"],
                    row["tag_id"],
                    row["borrow_date"],
                    row["return_date"],
                    row["cond_return"],
                    row["status"],
                ]
                rf = ctk.CTkFrame(scroll,
                                  fg_color="#F9FAFB" if i % 2 == 0 else "white",
                                  height=36)
                rf.pack(fill="x", pady=1)
                rf.pack_propagate(False)

                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    color = "#1A1A1A"
                    if col == 6:
                        color = "#D8000C" if val == "Active" else "#2ECC71"
                    ctk.CTkLabel(rf, text=val, font=("Inter", 11),
                                 text_color=color).grid(
                        row=0, column=col, padx=8, pady=6, sticky="w")

        except Exception as e:
            ctk.CTkLabel(
                scroll, text=f"Error: {e}", text_color="red").pack(pady=10)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
