import customtkinter as ctk
from tkinter import messagebox
from database import get_connection, log_action
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
from tkcalendar import DateEntry


class ProjectsView(ctk.CTkFrame):
    def __init__(self, parent, user_info):
        super().__init__(parent, fg_color="transparent")

        self.user_info = user_info
        self.is_admin = self.user_info.get("role", "Staff") == "Admin"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.grid(row=0, column=0, sticky="nsew")
        self.inner.grid_columnconfigure(0, weight=1, minsize=380)
        self.inner.grid_columnconfigure(1, weight=2, minsize=600)
        self.inner.grid_rowconfigure(0, weight=1)

        self.req_cart = []
        self.build_form_panel()
        self.build_table_panel()

        uid = self.user_info.get("user_id")
        if uid:
            log_action(uid, "Viewed", "Projects", "Opened Project Management module")

    def build_form_panel(self):
        form_card = ctk.CTkScrollableFrame(self.inner, fg_color="white", corner_radius=10, width=380)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(form_card, text="Draft Project Plan",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 5))

        def field(label, ph):
            ctk.CTkLabel(form_card, text=label, font=("Inter", 12, "bold"),
                         text_color="#1A1A1A").pack(anchor="w", padx=20)
            e = ctk.CTkEntry(form_card, placeholder_text=ph)
            e.pack(fill="x", padx=20, pady=(5, 10))
            return e

        self.p_name = field("Project Name *", "e.g., Ayala Alabang Phase 2")
        self.p_desc = field("Project Description", "Brief scope of work...")
        self.p_head = field("Project Head / Manager *", "e.g., Engr. Juan Santos")
        self.p_client = field("Client / Company *", "e.g., Makati Dev Corp")
        self.p_location = field("Site Location", "e.g., Block 4, Alabang")

        # ── Assigned Workers (multi-entry with + Add button) ──
        ctk.CTkLabel(form_card, text="Assigned Workers",
                     font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)

        worker_input_row = ctk.CTkFrame(form_card, fg_color="transparent")
        worker_input_row.pack(fill="x", padx=20, pady=(5, 5))

        self.worker_single_entry = ctk.CTkEntry(worker_input_row,
                                                 placeholder_text="Employee ID or name...",
                                                 )
        self.worker_single_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.worker_single_entry.bind("<Return>", lambda e: self._add_worker_from_entry())

        ctk.CTkButton(worker_input_row, text="+ Add", width=55, height=32,
                      fg_color="#1E4528", hover_color="#14301C",
                      command=self._add_worker_from_entry).pack(side="left", padx=(0, 5))
        ctk.CTkButton(worker_input_row, text="📷 Scan", width=65, height=32,
                      fg_color="#3498DB", hover_color="#2980B9",
                      command=self.scan_worker).pack(side="left")

        # Worker tag display area
        self.worker_tags_frame = ctk.CTkScrollableFrame(form_card, fg_color="#F9FAFB",
                                                         corner_radius=6, height=80)
        self.worker_tags_frame.pack(fill="x", padx=20, pady=(0, 12))
        self.workers_list = []  # list of worker strings
        self._refresh_worker_tags()

        # ── Inventory Catalog ──
        ctk.CTkLabel(form_card, text="Tools & Equipment Needed *",
                     font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        ctk.CTkButton(form_card, text="🔍 Browse Inventory Catalog",
                      fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D",
                      font=("Inter", 12, "bold"), command=self.open_tool_picker,
                      ).pack(fill="x", padx=20, pady=(5, 10))

        cart_bg = ctk.CTkFrame(form_card, fg_color="#F9FAFB", corner_radius=8)
        cart_bg.pack(fill="x", padx=20, pady=(0, 15))
        self.cart_scroll = ctk.CTkScrollableFrame(cart_bg, fg_color="white", height=120)
        self.cart_scroll.pack(fill="x", padx=10, pady=10)
        self.refresh_req_cart()

        # ── Calendar Date Pickers ──
        row_dates = ctk.CTkFrame(form_card, fg_color="transparent")
        row_dates.pack(fill="x", padx=20, pady=(5, 10))
        row_dates.grid_columnconfigure(0, weight=1)
        row_dates.grid_columnconfigure(1, weight=1)

        start_f = ctk.CTkFrame(row_dates, fg_color="transparent")
        start_f.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(start_f, text="Start Date", font=("Inter", 11, "bold"),
                     text_color="#1A1A1A").pack(anchor="w")
        self.p_start = DateEntry(start_f, width=12, background='#1E4528',
                                 foreground='white', borderwidth=2,
                                 date_pattern='yyyy-mm-dd')
        self.p_start.pack(fill="x", pady=(5, 0))

        end_f = ctk.CTkFrame(row_dates, fg_color="transparent")
        end_f.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(end_f, text="End Date", font=("Inter", 11, "bold"),
                     text_color="#1A1A1A").pack(anchor="w")
        self.p_end = DateEntry(end_f, width=12, background='#1E4528',
                               foreground='white', borderwidth=2,
                               date_pattern='yyyy-mm-dd')
        self.p_end.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(form_card, text="Submit for Approval", height=40,
                      fg_color="#1E4528", hover_color="#14301C",
                      font=("Inter", 13, "bold"), command=self.save_project,
                      ).pack(fill="x", padx=20, pady=(20, 20))

    # ── Worker tag helpers ──
    def _add_worker_from_entry(self):
        val = self.worker_single_entry.get().strip()
        if val and val not in self.workers_list:
            self.workers_list.append(val)
            self._refresh_worker_tags()
        self.worker_single_entry.delete(0, 'end')

    def _refresh_worker_tags(self):
        for w in self.worker_tags_frame.winfo_children():
            w.destroy()
        if not self.workers_list:
            ctk.CTkLabel(self.worker_tags_frame, text="No workers added yet.",
                         text_color="gray", font=("Inter", 11)).pack(pady=8)
            return
        for idx, worker in enumerate(self.workers_list):
            tag_row = ctk.CTkFrame(self.worker_tags_frame, fg_color="white", corner_radius=5, height=28)
            tag_row.pack(fill="x", pady=2, padx=5)
            tag_row.pack_propagate(False)
            ctk.CTkLabel(tag_row, text=f"👷 {worker}", font=("Inter", 11),
                         text_color="#1E4528").pack(side="left", padx=8)
            ctk.CTkButton(tag_row, text="✕", width=22, height=22,
                          fg_color="#FFEAEA", text_color="#D8000C", hover_color="#FFC0C0",
                          command=lambda i=idx: self._remove_worker(i)).pack(side="right", padx=5)

    def _remove_worker(self, idx):
        if 0 <= idx < len(self.workers_list):
            self.workers_list.pop(idx)
            self._refresh_worker_tags()

    def open_tool_picker(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Inventory Requisition Catalog")
        modal.geometry("720x560")
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()

        # CENTER THE MODAL
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (720 // 2)
        y = (modal.winfo_screenheight() // 2) - (560 // 2)
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text="Select Items for Project Requisition",
                     font=("Inter", 18, "bold"), text_color="black").pack(pady=(20, 5))
        ctk.CTkLabel(modal, text="Search by Name or PID, then set quantity and click + Add.",
                     font=("Inter", 11), text_color="gray").pack(pady=(0, 10))

        # ── Search row: Name/PID field + PID-only field + buttons ──
        search_frame = ctk.CTkFrame(modal, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 5))

        ctk.CTkLabel(search_frame, text="Name:", font=("Inter", 11), text_color="gray").pack(side="left")
        search_name = ctk.CTkEntry(search_frame, placeholder_text="Item name...", width=180)
        search_name.pack(side="left", padx=(5, 10))

        ctk.CTkLabel(search_frame, text="PID:", font=("Inter", 11), text_color="gray").pack(side="left")
        search_pid = ctk.CTkEntry(search_frame, placeholder_text="Product ID...", width=100)
        search_pid.pack(side="left", padx=(5, 10))

        def do_search():
            load_catalog(name_q=search_name.get().strip(), pid_q=search_pid.get().strip())

        def do_reset():
            search_name.delete(0, 'end')
            search_pid.delete(0, 'end')
            load_catalog()

        ctk.CTkButton(search_frame, text="Search", width=80, fg_color="#1E4528", hover_color="#14301C",
                      font=("Inter", 11, "bold"), command=do_search).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="↻ Reset", width=80, fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC",
                      command=do_reset).pack(side="left", padx=5)

        # Enter on search bar also triggers search
        search_name.bind("<Return>", lambda e: do_search())
        search_pid.bind("<Return>", lambda e: do_search())

        # ── Table header ──
        hdr = ctk.CTkFrame(modal, fg_color="#1E4528", height=35, corner_radius=5)
        hdr.pack(fill="x", padx=(20, 36))
        hdr.pack_propagate(False)
        weights = [1, 1, 2, 1, 1, 1, 1]
        cols = ["PID", "Type", "Item Name", "UoM", "Avail/Tot", "Req Qty", "Action"]
        for col, (w, text) in enumerate(zip(weights, cols)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=text, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=5, pady=5, sticky="w")

        list_scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        list_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        def load_catalog(name_q="", pid_q=""):
            for w in list_scroll.winfo_children():
                w.destroy()
            conn = get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor(dictionary=True)
                query = """
                    SELECT t.tool_id, t.name, IFNULL(t.item_type,'Equipment') as type,
                           IFNULL(t.unit_of_measure,'pcs') as uom,
                           IFNULL(i.quantity_available, 0) as avail,
                           IFNULL(i.quantity_total, 0) as total
                    FROM tool t JOIN inventory i ON t.tool_id = i.tool_id
                    WHERE t.is_archived = 0
                """
                params = []
                if name_q and pid_q:
                    query += " AND (t.name LIKE %s AND t.tool_id LIKE %s)"
                    params = [f"%{name_q}%", f"%{pid_q}%"]
                elif name_q:
                    query += " AND t.name LIKE %s"
                    params = [f"%{name_q}%"]
                elif pid_q:
                    query += " AND t.tool_id LIKE %s"
                    params = [f"%{pid_q}%"]

                cursor.execute(query, params)

                for i, row in enumerate(cursor.fetchall()):
                    rf = ctk.CTkFrame(list_scroll,
                                      fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
                    rf.pack(fill="x", pady=2)
                    rf.pack_propagate(False)
                    for col, w in enumerate(weights):
                        rf.grid_columnconfigure(col, weight=w)

                    ctk.CTkLabel(rf, text=str(row['tool_id']),
                                 font=("Inter", 10), text_color="gray").grid(
                        row=0, column=0, padx=5, pady=8, sticky="w")
                    type_color = "#D35400" if row['type'] == "Consumable" else "#1A1A1A"
                    ctk.CTkLabel(rf, text=row['type'],
                                 font=("Inter", 10, "bold"), text_color=type_color).grid(
                        row=0, column=1, padx=5, pady=8, sticky="w")
                    ctk.CTkLabel(rf, text=row['name'],
                                 font=("Inter", 11, "bold"), text_color="black").grid(
                        row=0, column=2, padx=5, pady=8, sticky="w")
                    ctk.CTkLabel(rf, text=row['uom'],
                                 font=("Inter", 10), text_color="gray").grid(
                        row=0, column=3, padx=5, pady=8, sticky="w")

                    avail = f"{row['avail']:g}" if row['avail'] else "0"
                    tot = f"{row['total']:g}" if row['total'] else "0"
                    stock_color = "#D8000C" if float(row['avail']) <= 0 else "#2ECC71"
                    ctk.CTkLabel(rf, text=f"{avail}/{tot}",
                                 font=("Inter", 11, "bold"), text_color=stock_color).grid(
                        row=0, column=4, padx=5, pady=8, sticky="w")

                    qty_entry = ctk.CTkEntry(rf, width=55, height=26)
                    qty_entry.grid(row=0, column=5, padx=5, pady=8, sticky="w")

                    ctk.CTkButton(rf, text="+ Add", width=55, height=26,
                                  fg_color="#3498DB", hover_color="#2980B9",
                                  command=lambda r=row, q_e=qty_entry: self.add_from_catalog(r, q_e, modal),
                                  ).grid(row=0, column=6, padx=5, pady=8, sticky="w")

                if not list_scroll.winfo_children():
                    ctk.CTkLabel(list_scroll, text="No items found. Try a different search.",
                                 text_color="gray").pack(pady=20)
            except Exception as e:
                ctk.CTkLabel(list_scroll, text=f"Error: {e}", text_color="red").pack(pady=10)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        load_catalog()

    def add_from_catalog(self, row_data, qty_entry, modal):
        try:
            req_qty = float(qty_entry.get())
        except ValueError:
            return messagebox.showwarning("Invalid", "Please enter a valid number.", parent=modal)

        if req_qty <= 0:
            return

        if req_qty > float(row_data['total']):
            return messagebox.showerror(
                "Denied",
                f"Cannot request {req_qty}. The company only owns {row_data['total']:g} {row_data['uom']} total.",
                parent=modal
            )

        needs_retrieval = False
        if req_qty > float(row_data['avail']):
            warn_msg = (
                f"⚠️ TIMELINE CONFLICT RISK\n\n"
                f"You requested {req_qty}, but only {row_data['avail']:g} are in the warehouse.\n\n"
                f"Missing items are deployed elsewhere. If not returned before your Start Date, "
                f"the project may be delayed.\n\nAdd anyway?"
            )
            if not messagebox.askyesno("Stock Conflict", warn_msg, parent=modal):
                return
            needs_retrieval = True

        for item in self.req_cart:
            if item['tool_id'] == row_data['tool_id']:
                item['qty'] += req_qty
                item['needs_retrieval'] = item['needs_retrieval'] or needs_retrieval
                self.refresh_req_cart()
                qty_entry.delete(0, 'end')
                return

        self.req_cart.append({
            'tool_id': row_data['tool_id'],
            'name': row_data['name'],
            'uom': row_data['uom'],
            'qty': req_qty,
            'needs_retrieval': needs_retrieval
        })
        self.refresh_req_cart()
        qty_entry.delete(0, 'end')

    def refresh_req_cart(self):
        for w in self.cart_scroll.winfo_children():
            w.destroy()
        if not self.req_cart:
            ctk.CTkLabel(self.cart_scroll, text="No items selected.",
                         text_color="gray", font=("Inter", 11)).pack(pady=20)
            return
        for i, item in enumerate(self.req_cart):
            row = ctk.CTkFrame(self.cart_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            warning_icon = "⚠️ " if item.get('needs_retrieval') else "✓ "
            text_col = "#D35400" if item.get('needs_retrieval') else "black"
            info = f"{warning_icon}{item['name']} ({item['qty']:g} {item['uom']})"
            ctk.CTkLabel(row, text=info, font=("Inter", 11, "bold"), text_color=text_col).pack(side="left", padx=5)
            ctk.CTkButton(row, text="✕", width=20, height=20, fg_color="#FFEAEA",
                          text_color="#D8000C", hover_color="#FFC0C0",
                          command=lambda idx=i: [self.req_cart.pop(idx), self.refresh_req_cart()]).pack(side="right")

    def scan_worker(self):
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        except Exception:
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return messagebox.showerror("Camera Error", "No webcam detected.",
                                        parent=self.winfo_toplevel())

        detected_data = None
        cv2.namedWindow('Scan Worker ID', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Scan Worker ID', cv2.WND_PROP_TOPMOST, 1)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.putText(frame, "Scan Employee ID (Press 'Q' to Cancel)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            for barcode in decode(frame, symbols=[ZBarSymbol.QRCODE]):
                detected_data = barcode.data.decode('utf-8').strip()
                break
            cv2.imshow('Scan Worker ID', frame)
            if detected_data or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if detected_data:
            if detected_data not in self.workers_list:
                self.workers_list.append(detected_data)
                self._refresh_worker_tags()

    def save_project(self):
        name = self.p_name.get().strip()
        client = self.p_client.get().strip()
        project_head = self.p_head.get().strip()
        workers_str = ", ".join(self.workers_list) if self.workers_list else ""

        if not name or not client:
            messagebox.showerror("Error", "Project Name and Client are required.",
                                 parent=self.winfo_toplevel())
            return
        if not self.req_cart:
            messagebox.showerror("Error", "Please add at least one tool requirement.",
                                 parent=self.winfo_toplevel())
            return

        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (name, description, project_head, client, location,
                                      workers_assigned, start_date, end_date, manager_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (name, self.p_desc.get(), project_head, client,
                  self.p_location.get(), workers_str,
                  self.p_start.get(), self.p_end.get(),
                  self.user_info['user_id']))

            project_id = cursor.lastrowid

            for item in self.req_cart:
                req_status = 'Warning' if item.get('needs_retrieval') else 'Clear'
                cursor.execute("""
                    INSERT INTO project_requirements (project_id, tool_id, quantity, status)
                    VALUES (%s, %s, %s, %s)
                """, (project_id, item['tool_id'], item['qty'], req_status))

            conn.commit()

            uid = self.user_info.get("user_id")
            if uid:
                log_action(uid, "Submitted", "Projects",
                           f"Submitted project '{name}' (ID: {project_id}) for client '{client}'. "
                           f"{len(self.req_cart)} tool requirement(s). Head: {project_head}.")

            messagebox.showinfo("Success", "Project submitted! Waiting for Admin Approval.",
                                parent=self.winfo_toplevel())

            self.p_name.delete(0, 'end')
            self.p_desc.delete(0, 'end')
            self.p_head.delete(0, 'end')
            self.p_client.delete(0, 'end')
            self.p_location.delete(0, 'end')
            self.workers_list.clear()
            self._refresh_worker_tags()
            self.req_cart.clear()
            self.refresh_req_cart()
            self.load_projects()

        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def build_table_panel(self):
        table_card = ctk.CTkFrame(self.inner, fg_color="white", corner_radius=10)
        table_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(table_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(top, text="Project Deployment Plans",
                     font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")

        hdr = ctk.CTkFrame(table_card, fg_color="#1E4528", corner_radius=5, height=38)
        hdr.pack(fill="x", padx=(20, 36))
        hdr.pack_propagate(False)

        headers = ["ID", "Project Name", "Client", "Project Head", "Status", "Actions"]
        weights = [1, 3, 2, 2, 1, 1]

        for col, (h, w) in enumerate(zip(headers, weights)):
            hdr.grid_columnconfigure(col, weight=w)
            ctk.CTkLabel(hdr, text=h, font=("Inter", 11, "bold"),
                         text_color="white").grid(row=0, column=col, padx=10, pady=8, sticky="w")

        self.project_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.project_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.load_projects()

    def load_projects(self):
        for w in self.project_scroll.winfo_children():
            w.destroy()
        conn = get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, a.full_name as admin_approver
                FROM projects p
                LEFT JOIN user a ON p.approved_by = a.user_id
                ORDER BY p.project_id DESC
            """)
            for i, row in enumerate(cursor.fetchall()):
                rf = ctk.CTkFrame(self.project_scroll,
                                  fg_color="#F9FAFB" if i % 2 == 0 else "white", height=45)
                rf.pack(fill="x", pady=2)
                rf.pack_propagate(False)

                vals = [
                    str(row["project_id"]), row["name"], row["client"],
                    row.get("project_head") or "—", row["status"]
                ]
                weights = [1, 3, 2, 2, 1]

                for col, (val, w) in enumerate(zip(vals, weights)):
                    rf.grid_columnconfigure(col, weight=w)
                    txt_color = "#D35400" if col == 4 and val == "Pending" else (
                        "#2ECC71" if col == 4 and val == "Approved" else "#1A1A1A")
                    ctk.CTkLabel(rf, text=val,
                                 font=("Inter", 11, "bold" if col == 4 else "normal"),
                                 text_color=txt_color).grid(row=0, column=col, padx=10, pady=12, sticky="w")

                rf.grid_columnconfigure(5, weight=1)
                btn_color = "#3498DB" if row['status'] == 'Pending' else "#BDC3C7"
                btn_text = "Review" if row['status'] == 'Pending' else "View"
                ctk.CTkButton(rf, text=btn_text, width=65, height=28,
                              fg_color=btn_color, hover_color="#2980B9",
                              font=("Inter", 11, "bold"),
                              command=lambda r=row: self.open_project_modal(r)).grid(
                    row=0, column=5, padx=10, pady=10, sticky="w")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def open_project_modal(self, row):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Project Overview: {row['name']}")
        modal.geometry("580x720")
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()

        # CENTER
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (580 // 2)
        y = (modal.winfo_screenheight() // 2) - (720 // 2)
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=row['name'], font=("Inter", 18, "bold"), text_color="black").pack(pady=(20, 3))
        status_color = "#D35400" if row['status'] == "Pending" else "#2ECC71"
        ctk.CTkLabel(modal, text=f"Status: {row['status']}",
                     font=("Inter", 12, "bold"), text_color=status_color).pack(pady=(0, 5))

        scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        details_frame = ctk.CTkFrame(scroll, fg_color="#F9FAFB", corner_radius=8)
        details_frame.pack(fill="x", pady=(0, 10))

        def add_detail(lbl, val):
            row_f = ctk.CTkFrame(details_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=15, pady=(5, 0))
            ctk.CTkLabel(row_f, text=lbl, font=("Inter", 11, "bold"),
                         text_color="#1E4528", width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row_f, text=val or "None specified", font=("Inter", 11),
                         text_color="black", wraplength=360, justify="left").pack(side="left")

        add_detail("Client:", row['client'])
        add_detail("Site Location:", row['location'])
        add_detail("Description:", row.get('description') or "—")
        add_detail("Project Head:", row.get('project_head') or "—")
        add_detail("Assigned Workers:", row.get('workers_assigned') or "None assigned")
        add_detail("Schedule:",
                   f"Start: {row['start_date']}   →   End: {row['end_date']}")

        ctk.CTkFrame(details_frame, height=8, fg_color="transparent").pack()

        # Tools Requisition
        ctk.CTkLabel(scroll, text="Tools & Equipment Requisition",
                     font=("Inter", 12, "bold"), text_color="#1E4528").pack(anchor="w", pady=(8, 3))
        tools_scroll = ctk.CTkScrollableFrame(scroll, fg_color="white", corner_radius=8, height=160)
        tools_scroll.pack(fill="x", pady=(0, 10))

        reqs = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.name, t.item_type, t.unit_of_measure, pr.quantity, pr.status
                FROM project_requirements pr
                JOIN tool t ON pr.tool_id = t.tool_id
                WHERE pr.project_id = %s
            """, (row['project_id'],))
            reqs = cursor.fetchall()
            cursor.close()
            conn.close()

        if reqs:
            for req in reqs:
                warning_icon = "⚠️ " if req['status'] == 'Warning' else "✓ "
                text_col = "#D35400" if req['status'] == 'Warning' else "#1A1A1A"
                row_str = (f"{warning_icon}{req['name']}  |  "
                           f"{req['quantity']:g} {req['unit_of_measure']} ({req['item_type']})")
                req_row = ctk.CTkFrame(tools_scroll, fg_color="transparent", height=30)
                req_row.pack(fill="x", pady=1)
                ctk.CTkLabel(req_row, text=row_str,
                             font=("Inter", 11, "bold" if req['status'] == 'Warning' else "normal"),
                             text_color=text_col).pack(anchor="w", padx=8)
        else:
            ctk.CTkLabel(tools_scroll, text="No tools listed.", text_color="gray").pack(pady=10)

        if row['status'] == 'Approved' and row.get('admin_approver'):
            ctk.CTkLabel(scroll,
                         text=f"✅ Approved by: {row['admin_approver']}",
                         font=("Inter", 11, "bold"), text_color="#2ECC71").pack(anchor="w", pady=(0, 5))

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=20, pady=15)

        if row['status'] == 'Pending' and self.is_admin:
            def approve_project():
                has_warnings = any(r['status'] == 'Warning' for r in reqs)
                confirm_msg = "Approve this project? Tools can now be deployed for this site."
                if has_warnings:
                    confirm_msg = (
                        "⚠️ WARNING: Some tools are currently deployed elsewhere.\n"
                        "Ensure they are retrieved before this project's start date.\n\n"
                        "Approve anyway?"
                    )
                if messagebox.askyesno("Confirm Approval", confirm_msg, parent=modal):
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE projects SET status='Approved', approved_by=%s WHERE project_id=%s",
                            (self.user_info['user_id'], row['project_id'])
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()

                        uid = self.user_info.get("user_id")
                        if uid:
                            log_action(uid, "Approved", "Projects",
                                       f"Approved project '{row['name']}' (ID: {row['project_id']})")

                        modal.destroy()
                        self.load_projects()
                        messagebox.showinfo("Approved", "Project has been officially approved.",
                                            parent=self.winfo_toplevel())

            ctk.CTkButton(btn_frame, text="✓ Approve Project",
                          fg_color="#2ECC71", hover_color="#27AE60",
                          text_color="black", font=("Inter", 12, "bold"),
                          command=approve_project).pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="Close", fg_color="#E0E0E0",
                      text_color="black", hover_color="#CCCCCC", width=100,
                      command=modal.destroy).pack(side="right")