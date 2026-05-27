import customtkinter as ctk
from tkinter import messagebox, filedialog
from database import get_connection
import os
import json
from datetime import datetime

class MaintenanceView(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs): 
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1)

        self.build_ui()

    def build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tabs = ["Manage Issues", "Archived Tools", "Database Backup", "Database Restore"]
        
        self.seg_btn = ctk.CTkSegmentedButton(
            top_bar, values=tabs, command=self.switch_tab,
            fg_color="#F0F0F0", selected_color="#1E4528", 
            selected_hover_color="#14301C" 
        )
        self.seg_btn.pack(side="right", padx=20)
        self.seg_btn.set(tabs[0]) 

        self.content_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        self.switch_tab(tabs[0])

    def switch_tab(self, key):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if key == "Database Backup":
            self.render_backup_tab()
        elif key == "Database Restore":
            self.render_restore_tab()
        elif key == "Archived Tools":
            self.render_archived_tab()
        elif key == "Manage Issues":
            self.render_issues_tab()

    # ==========================================
    # PHASE 6: MANAGE ISSUES TAB
    # ==========================================
    def render_issues_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(top, text="Manage Tool Issues", font=("Inter", 20, "bold"), text_color="#D8000C").pack(side="left")
        ctk.CTkLabel(frame, text="Tools flagged as 'Damaged' or 'Needs Repair' during retrieval.", font=("Inter", 12), text_color="gray").pack(anchor="w", padx=30, pady=(0, 15))

        hdr = ctk.CTkFrame(frame, fg_color="#D8000C", corner_radius=5, height=40)
        hdr.pack(fill="x", padx=30)
        hdr.pack_propagate(False)

        headers = ["Tool ID", "Name", "Category", "Condition", "Actions"]
        weights = [1, 3, 2, 2, 2]

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self._issues_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self._issues_scroll.pack(fill="both", expand=True, padx=30, pady=(5, 30))

        self.load_issues()

    def load_issues(self):
        for w in self._issues_scroll.winfo_children(): w.destroy()
        conn = get_connection()
        if not conn: return
        try:
            c = conn.cursor(dictionary=True)
            c.execute("SELECT tool_id, name, IFNULL(category,'—') as category, `condition` FROM tool WHERE `condition` IN ('Needs Repair', 'Damaged') AND is_archived = 0")
            rows = c.fetchall()
            
            if not rows:
                ctk.CTkLabel(self._issues_scroll, text="✓ All active tools are currently in good condition.", font=("Inter", 12, "bold"), text_color="#2ECC71").pack(pady=30)
                return
            
            for i, row in enumerate(rows):
                rf = ctk.CTkFrame(self._issues_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=45)
                rf.pack(fill="x", pady=2)
                rf.pack_propagate(False)
                
                vals = [str(row['tool_id']), row['name'], row['category'], row['condition']]
                weights = [1, 3, 2, 2]
                
                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    txt_col = "#D8000C" if col == 3 else "#1A1A1A"
                    ctk.CTkLabel(rf, text=val, font=("Inter", 11, "bold" if col==3 else "normal"), text_color=txt_col).grid(row=0, column=col, padx=10, pady=12, sticky="w")
                
                rf.grid_columnconfigure(4, weight=2)
                btn_frame = ctk.CTkFrame(rf, fg_color="transparent")
                btn_frame.grid(row=0, column=4, sticky="e", padx=10, pady=8)
                
                ctk.CTkButton(btn_frame, text="✓ Mark Repaired", width=90, fg_color="#2ECC71", hover_color="#27AE60", text_color="black", font=("Inter", 11, "bold"), command=lambda r=row: self.mark_fixed(r)).pack(side="left", padx=5)
                ctk.CTkButton(btn_frame, text="Archive/Dispose", width=90, fg_color="#D3B8A7", text_color="black", hover_color="#BFA595", font=("Inter", 11, "bold"), command=lambda r=row: self.archive_issue(r)).pack(side="left", padx=5)
                
        finally:
            if conn.is_connected(): c.close(); conn.close()

    def mark_fixed(self, row):
        if messagebox.askyesno("Confirm Repair", f"Mark '{row['name']}' as repaired and ready for deployment again?", parent=self.winfo_toplevel()):
            conn = get_connection()
            if conn:
                c = conn.cursor()
                c.execute("UPDATE tool SET `condition` = 'Good' WHERE tool_id = %s", (row['tool_id'],))
                conn.commit()
                c.close(); conn.close()
                messagebox.showinfo("Restored", "Tool status reverted to 'Good'.", parent=self.winfo_toplevel())
                self.load_issues()

    def archive_issue(self, row):
        if messagebox.askyesno("Confirm Disposal", f"Archive '{row['name']}'? It is unrepairable and will be removed from active inventory.", parent=self.winfo_toplevel()):
            conn = get_connection()
            if conn:
                c = conn.cursor()
                c.execute("UPDATE tool SET is_archived = 1, archived_at = NOW() WHERE tool_id = %s", (row['tool_id'],))
                conn.commit()
                c.close(); conn.close()
                self.load_issues()

    # ==========================================
    # BACKUP TAB
    # ==========================================
    def render_backup_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(frame, text="Database Backup", font=("Inter", 20, "bold"), text_color="#1E4528").pack(anchor="w", padx=30, pady=(30, 5))
        ctk.CTkLabel(frame, text="Export selected database tables to a timestamped JSON backup file.", font=("Inter", 12), text_color="gray").pack(anchor="w", padx=30, pady=(0, 20))

        options_frame = ctk.CTkFrame(frame, fg_color="#F9FAFB", corner_radius=8)
        options_frame.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(options_frame, text="Tables to include in backup:", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(15, 5))

        self.backup_vars = {}
        tables = ["tool", "inventory", "transaction", "user", "projects", "project_requirements"]
        for tbl in tables:
            var = ctk.BooleanVar(value=True)
            self.backup_vars[tbl] = var
            ctk.CTkCheckBox(options_frame, text=tbl.capitalize(), variable=var, font=("Inter", 12), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=3)

        ctk.CTkButton(options_frame, text="Select Backup Destination & Export", fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), height=40, command=self.execute_backup).pack(anchor="w", padx=20, pady=(15, 15))

        ctk.CTkLabel(frame, text="Backup Log:", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=(10, 5))
        self.backup_log = ctk.CTkTextbox(frame, height=180, fg_color="#F9FAFB", text_color="#1A1A1A", state="disabled")
        self.backup_log.pack(fill="x", padx=30, pady=(0, 30))

    def execute_backup(self):
        selected_tables = [tbl for tbl, var in self.backup_vars.items() if var.get()]
        if not selected_tables: return messagebox.showwarning("No Tables", "Please select at least one table to back up.", parent=self.winfo_toplevel())

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"ChampionAMS_Backup_{timestamp}.json"

        dest = filedialog.asksaveasfilename(title="Save Backup File", defaultextension=".json", initialfile=default_name, filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not dest: return

        conn = get_connection()
        if not conn: return

        backup_data = {"meta": {"timestamp": timestamp, "tables": selected_tables}}

        try:
            cursor = conn.cursor(dictionary=True)
            for tbl in selected_tables:
                try:
                    cursor.execute(f"SELECT * FROM `{tbl}`")
                    rows = cursor.fetchall()
                    clean_rows = []
                    for row in rows:
                        clean_row = {}
                        for k, v in row.items():
                            if hasattr(v, "isoformat"): clean_row[k] = v.isoformat()
                            else: clean_row[k] = v
                        clean_rows.append(clean_row)
                    backup_data[tbl] = clean_rows
                except Exception: pass 

            with open(dest, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, default=str)

            log_msg = (f"[{datetime.now().strftime('%H:%M:%S')}] SUCCESS — Backup saved to:\n{dest}\n" + "—" * 60 + "\n")
            self.backup_log.configure(state="normal")
            self.backup_log.insert("end", log_msg)
            self.backup_log.configure(state="disabled")

            messagebox.showinfo("Backup Complete", f"Backup saved successfully!\n\nFile: {os.path.basename(dest)}", parent=self.winfo_toplevel())

        except Exception as e: messagebox.showerror("Backup Failed", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # ==========================================
    # RESTORE TAB
    # ==========================================
    def render_restore_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(frame, text="Database Restore", font=("Inter", 20, "bold"), text_color="#1E4528").pack(anchor="w", padx=30, pady=(30, 5))
        ctk.CTkLabel(frame, text="Select a previously exported JSON backup file to restore data.", font=("Inter", 12), text_color="gray").pack(anchor="w", padx=30, pady=(0, 20))

        warning_card = ctk.CTkFrame(frame, fg_color="#FFF3CD", corner_radius=8)
        warning_card.pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkLabel(warning_card, text="⚠  WARNING: Restoring data will overwrite existing records for the selected tables.\nMake sure you have a current backup before proceeding.", font=("Inter", 11), text_color="#856404", justify="left").pack(padx=20, pady=12)

        self.restore_path_label = ctk.CTkLabel(frame, text="No file selected.", font=("Inter", 11), text_color="gray")
        self.restore_path_label.pack(anchor="w", padx=30, pady=(0, 5))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(anchor="w", padx=30, pady=(0, 20))

        ctk.CTkButton(btn_row, text="Browse Backup File", fg_color="#3498DB", hover_color="#2980B9", font=("Inter", 12, "bold"), command=self.browse_restore_file).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Restore Selected File", fg_color="#D8000C", hover_color="#B00000", font=("Inter", 12, "bold"), command=self.execute_restore).pack(side="left")

        self.restore_log = ctk.CTkTextbox(frame, height=220, fg_color="#F9FAFB", text_color="#1A1A1A", state="disabled")
        self.restore_log.pack(fill="x", padx=30, pady=(10, 30))
        self._restore_file_path = None

    def browse_restore_file(self):
        path = filedialog.askopenfilename(title="Select Backup JSON File", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if path:
            self._restore_file_path = path
            self.restore_path_label.configure(text=f"Selected: {os.path.basename(path)}", text_color="#1E4528")

    def execute_restore(self):
        if not getattr(self, "_restore_file_path", None): return messagebox.showwarning("No File", "Please browse and select a backup file first.", parent=self.winfo_toplevel())

        if not messagebox.askyesno("Confirm Restore", "This will overwrite existing records for the backed-up tables.\nAre you sure?", parent=self.winfo_toplevel()): return

        try:
            with open(self._restore_file_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
        except Exception as e:
            return messagebox.showerror("Read Error", f"Could not read backup file:\n{e}", parent=self.winfo_toplevel())

        conn = get_connection()
        if not conn: return
        log_lines = []

        try:
            cursor = conn.cursor()
            tables = backup_data.get("meta", {}).get("tables", [])
            for tbl in tables:
                rows = backup_data.get(tbl, [])
                if not rows:
                    log_lines.append(f"  ⏭ {tbl}: no data found in backup, skipped.")
                    continue
                cols = list(rows[0].keys())
                placeholders = ", ".join(["%s"] * len(cols))
                col_str = ", ".join([f"`{c}`" for c in cols])
                insert_sql = (f"INSERT INTO `{tbl}` ({col_str}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE " + ", ".join([f"`{c}`=VALUES(`{c}`)" for c in cols]))
                
                count = 0
                for row in rows:
                    cursor.execute(insert_sql, list(row.values()))
                    count += 1
                log_lines.append(f"  ✓ {tbl}: {count} record(s) restored.")

            conn.commit()
            log_lines.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] RESTORE COMPLETE:")
            log_lines.append("—" * 60)

            self.restore_log.configure(state="normal")
            self.restore_log.insert("end", "\n".join(log_lines) + "\n")
            self.restore_log.configure(state="disabled")

            messagebox.showinfo("Restore Complete", "Data restored successfully from backup.", parent=self.winfo_toplevel())

        except Exception as e: messagebox.showerror("Restore Failed", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # ==========================================
    # ARCHIVED TOOLS TAB
    # ==========================================
    def render_archived_tab(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(top, text="Archived Tools", font=("Inter", 20, "bold"), text_color="#1E4528").pack(side="left")
        ctk.CTkLabel(frame, text="Tools removed from active inventory. Click a row to restore or permanently delete.", font=("Inter", 12), text_color="gray").pack(anchor="w", padx=30, pady=(0, 15))

        headers = ["Tool ID", "Name", "Category", "Supplier", "Condition", "Archived On"]
        weights = [1, 2, 2, 2, 2, 2]

        hdr = ctk.CTkFrame(frame, fg_color="#1E4528", corner_radius=5, height=40)
        hdr.pack(fill="x", padx=30)
        hdr.pack_propagate(False)

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self._archived_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        self._archived_scroll.pack(fill="both", expand=True, padx=30, pady=(5, 30))

        self.load_archived_tools()

    def load_archived_tools(self):
        scroll = self._archived_scroll
        for w in scroll.winfo_children(): w.destroy()

        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT tool_id, name, IFNULL(category,'—') as category, IFNULL(supplier,'—') as supplier,
                       `condition`, IF(archived_at IS NOT NULL, DATE_FORMAT(archived_at,'%%b %%d %%Y'), 'Unknown') as archived_on
                FROM tool WHERE is_archived = 1 ORDER BY archived_at DESC
            """)
            rows = cursor.fetchall()
            weights = [1, 2, 2, 2, 2, 2]

            if not rows:
                ctk.CTkLabel(scroll, text="No archived tools.", text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(rows):
                vals = [str(row['tool_id']), row['name'], row['category'], row['supplier'], row['condition'], row['archived_on']]
                rf = ctk.CTkFrame(scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
                rf.pack(fill="x", pady=2)
                rf.pack_propagate(False)
                rf.bind("<Button-1>", lambda e, r=row: self.open_archive_modal(r))

                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    lbl = ctk.CTkLabel(rf, text=val, font=("Inter", 11), text_color="#1A1A1A")
                    lbl.grid(row=0, column=col, padx=10, pady=10, sticky="w")
                    lbl.bind("<Button-1>", lambda e, r=row: self.open_archive_modal(r))

        except Exception as e: ctk.CTkLabel(scroll, text=f"Error: {e}", text_color="red").pack(pady=10)
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def open_archive_modal(self, row):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Archived Tool — {row['name']}")
        modal.geometry("400x260")
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - 200
        y = (modal.winfo_screenheight() // 2) - 130
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"{row['name']}", font=("Inter", 15, "bold"), text_color="black").pack(pady=(20, 5))
        ctk.CTkLabel(modal, text=f"Tool ID: {row['tool_id']}  |  Archived on: {row['archived_on']}", font=("Inter", 11), text_color="gray").pack(pady=(0, 20))

        def restore_tool():
            if messagebox.askyesno("Restore", "Restore this tool to active inventory?", parent=modal):
                conn = get_connection()
                if not conn: return
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tool SET is_archived=0, archived_at=NULL WHERE tool_id=%s", (row['tool_id'],))
                    conn.commit()
                    messagebox.showinfo("Restored", "Tool restored to active inventory.", parent=modal)
                    modal.destroy()
                    self.load_archived_tools()
                except Exception as e: messagebox.showerror("Error", str(e), parent=modal)
                finally:
                    if conn.is_connected(): cursor.close(); conn.close()

        def delete_tool():
            if messagebox.askyesno("Delete Permanently", "This will permanently delete the tool and all its transaction records.\nThis action cannot be undone. Proceed?", parent=modal):
                conn = get_connection()
                if not conn: return
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM transaction WHERE tool_id=%s", (row['tool_id'],))
                    cursor.execute("DELETE FROM inventory WHERE tool_id=%s", (row['tool_id'],))
                    cursor.execute("DELETE FROM tool WHERE tool_id=%s", (row['tool_id'],))
                    conn.commit()
                    messagebox.showinfo("Deleted", "Tool permanently deleted.", parent=modal)
                    modal.destroy()
                    self.load_archived_tools()
                except Exception as e: messagebox.showerror("Error", str(e), parent=modal)
                finally:
                    if conn.is_connected(): cursor.close(); conn.close()

        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkButton(btn_row, text="Restore to Active", fg_color="#1E4528", hover_color="#14301C", command=restore_tool).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row, text="Delete Permanently", fg_color="#D8000C", hover_color="#B00000", command=delete_tool).pack(side="left")
        ctk.CTkButton(btn_row, text="Cancel", fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=modal.destroy).pack(side="right")