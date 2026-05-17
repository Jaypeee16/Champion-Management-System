import customtkinter as ctk
from tkinter import messagebox
from database import get_connection
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class BorrowingView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent", orientation="horizontal")
        
        self.grid_columnconfigure(0, weight=1, minsize=1000) 
        self.grid_rowconfigure(2, weight=1)

        self.active_borrow_user_id = None
        self.active_borrow_user_name = None
        self.borrow_cart = [] 
        
        self.active_return_user_id = None
        self.active_return_tool_id = None
        self.max_returnable = 0

        self.build_forms_section()
        self.build_history_table()
        self.load_transaction_history()

    def build_forms_section(self):
        forms_container = ctk.CTkFrame(self, fg_color="transparent")
        forms_container.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        forms_container.grid_columnconfigure(0, weight=1, minsize=450)
        forms_container.grid_columnconfigure(1, weight=1, minsize=450)

        # ==========================================
        # LEFT PANEL: THE BORROWING CART
        # ==========================================
        borrow_card = ctk.CTkFrame(forms_container, fg_color="white", corner_radius=10)
        borrow_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(borrow_card, text="📤 Multi-Tool Checkout", font=("Inter", 16, "bold"), text_color="#1E4528").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(borrow_card, text="Scan Employee ID, then scan tools to add/increment them in the cart.", font=("Inter", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        # 1. Borrower Section
        ctk.CTkLabel(borrow_card, text="1. Borrower ID (Employee ID)", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        b_emp_row = ctk.CTkFrame(borrow_card, fg_color="transparent")
        b_emp_row.pack(fill="x", padx=20, pady=(5, 5))
        self.b_emp_id = ctk.CTkEntry(b_emp_row, placeholder_text="Scan ID & Press Enter...")
        self.b_emp_id.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.b_emp_id.bind("<Return>", lambda e: self.verify_borrower())
        ctk.CTkButton(b_emp_row, text="📷 Scan", width=60, fg_color="#3498DB", hover_color="#2980B9", command=lambda: self.open_scanner(self.b_emp_id, self.verify_borrower)).pack(side="left")
        
        self.b_user_name = ctk.CTkLabel(borrow_card, text="Name: Pending Scan...", font=("Inter", 12), text_color="gray")
        self.b_user_name.pack(anchor="w", padx=20, pady=(0, 15))

        # 2. Add To Cart Scanner
        ctk.CTkLabel(borrow_card, text="2. Add Tools to Cart (Scan Tag ID)", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        b_tag_row = ctk.CTkFrame(borrow_card, fg_color="transparent")
        b_tag_row.pack(fill="x", padx=20, pady=(5, 5))
        self.b_tag_id = ctk.CTkEntry(b_tag_row, placeholder_text="Scan Tool Tag & Press Enter...")
        self.b_tag_id.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.b_tag_id.bind("<Return>", lambda e: self.add_tool_to_cart())
        ctk.CTkButton(b_tag_row, text="📷 Scan", width=60, fg_color="#3498DB", hover_color="#2980B9", command=lambda: self.open_scanner(self.b_tag_id, self.add_tool_to_cart)).pack(side="left")

        self.cart_frame = ctk.CTkScrollableFrame(borrow_card, fg_color="#F9FAFB", height=120, corner_radius=5)
        self.cart_frame.pack(fill="x", padx=20, pady=(10, 15))
        self.refresh_cart_ui() 

        # 3. Purpose & Confirm
        ctk.CTkLabel(borrow_card, text="3. Purpose / Project", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.b_purpose = ctk.CTkEntry(borrow_card, placeholder_text="e.g., Maintenance Room B")
        self.b_purpose.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkButton(borrow_card, text="Confirm Borrow & Print Receipt", height=40, fg_color="#1E4528", hover_color="#14301C", font=("Inter", 13, "bold"), command=self.execute_borrow).pack(fill="x", padx=20, pady=(0, 20))


        # ==========================================
        # RIGHT PANEL: THE DUAL-AUTH RETURN DESK
        # ==========================================
        return_card = ctk.CTkFrame(forms_container, fg_color="white", corner_radius=10)
        return_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(return_card, text="📥 Return Tool (Secure Audit)", font=("Inter", 16, "bold"), text_color="#F1C40F").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(return_card, text="Scan Employee ID and Tool Tag (or enter Receipt TRN).", font=("Inter", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        # 1. Employee Auth for Return
        ctk.CTkLabel(return_card, text="1. Employee ID (Who is returning?)", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        r_emp_row = ctk.CTkFrame(return_card, fg_color="transparent")
        r_emp_row.pack(fill="x", padx=20, pady=(5, 5))
        self.r_emp_id = ctk.CTkEntry(r_emp_row, placeholder_text="Scan ID & Press Enter...")
        self.r_emp_id.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.r_emp_id.bind("<Return>", lambda e: self.verify_return_employee())
        ctk.CTkButton(r_emp_row, text="📷 Scan", width=60, fg_color="#3498DB", hover_color="#2980B9", command=lambda: self.open_scanner(self.r_emp_id, self.verify_return_employee)).pack(side="left")

        # UI FIX: Added the Verified Name Label to the Return Panel!
        self.r_user_name = ctk.CTkLabel(return_card, text="Name: Pending Scan...", font=("Inter", 12), text_color="gray")
        self.r_user_name.pack(anchor="w", padx=20, pady=(0, 15))

        # 2. Tool Return Scanner (NOW SUPPORTS TRN NUMBER)
        ctk.CTkLabel(return_card, text="2. Tag ID or Receipt TRN (e.g., TRN-42)", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        r_tag_row = ctk.CTkFrame(return_card, fg_color="transparent")
        r_tag_row.pack(fill="x", padx=20, pady=(5, 5))
        self.r_tag_id = ctk.CTkEntry(r_tag_row, placeholder_text="Scan Tag or enter TRN...")
        self.r_tag_id.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.r_tag_id.bind("<Return>", lambda e: self.verify_tool_for_return())
        ctk.CTkButton(r_tag_row, text="📷 Scan", width=60, fg_color="#3498DB", hover_color="#2980B9", command=lambda: self.open_scanner(self.r_tag_id, self.verify_tool_for_return)).pack(side="left")

        self.r_record_info = ctk.CTkLabel(return_card, text="Record: Pending Scan...", font=("Inter", 12), text_color="gray", justify="left")
        self.r_record_info.pack(anchor="w", padx=20, pady=(0, 15))

        # 3. Condition Audit & Qty
        cond_qty_row = ctk.CTkFrame(return_card, fg_color="transparent")
        cond_qty_row.pack(fill="x", padx=20, pady=(5, 20))
        cond_qty_row.grid_columnconfigure(0, weight=2)
        cond_qty_row.grid_columnconfigure(1, weight=1)

        c_frame = ctk.CTkFrame(cond_qty_row, fg_color="transparent")
        c_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(c_frame, text="3. Return Condition", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w")
        self.r_condition = ctk.CTkOptionMenu(c_frame, values=["Good", "Needs Repair", "Damaged", "Lost"], fg_color="#F9FAFB", text_color="black")
        self.r_condition.pack(fill="x", pady=(5, 0))

        q_frame = ctk.CTkFrame(cond_qty_row, fg_color="transparent")
        q_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(q_frame, text="Qty", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w")
        self.r_qty = ctk.CTkEntry(q_frame, placeholder_text="1")
        self.r_qty.pack(fill="x", pady=(5, 0))
        self.r_qty.insert(0, "1")

        ctk.CTkButton(return_card, text="Confirm Return & Restock", height=40, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 13, "bold"), command=self.execute_return).pack(fill="x", padx=20, pady=(0, 20))


    def build_history_table(self):
        history_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        history_card.grid(row=1, column=0, sticky="nsew")
        
        top_bar = ctk.CTkFrame(history_card, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(top_bar, text="Transaction History", font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(side="left")
        
        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search Name or Tag...", width=200)
        self.search_entry.pack(side="right", padx=(10, 0))
        self.search_entry.bind("<Return>", lambda e: self.load_transaction_history())
        ctk.CTkButton(top_bar, text="Search", width=60, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=self.load_transaction_history).pack(side="right")

        header_frame = ctk.CTkFrame(history_card, fg_color="#1E4528", corner_radius=5, height=35)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)

        self.headers = ["Type", "Tool Name", "Tag ID", "Qty", "Borrower", "Date & Time", "Status"]
        self.weights = [1, 2, 2, 1, 2, 2, 1]

        for col, (text, weight) in enumerate(zip(self.headers, self.weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 11, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(history_card, fg_color="transparent", height=400)
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 15))


    # ==========================================
    # LOGIC: TURBO WEBCAM SCANNER
    # ==========================================
    def open_scanner(self, target_entry, trigger_method):
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
        except:
            cap = cv2.VideoCapture(0) 
            
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "No webcam detected.", parent=self.winfo_toplevel())
            return

        detected_data = None
        
        cv2.namedWindow('Champion Scanner - Turbo Mode', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Champion Scanner - Turbo Mode', cv2.WND_PROP_TOPMOST, 1)
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            height, width, _ = frame.shape
            top_left = (int(width*0.25), int(height*0.3))
            bottom_right = (int(width*0.75), int(height*0.7))
            
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, "Align QR Code inside box", (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'Q' to Cancel", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            detected_codes = decode(frame, symbols=[ZBarSymbol.QRCODE])
            for barcode in detected_codes:
                raw_data = barcode.data.decode('utf-8')
                if "Tag ID:" in raw_data:
                    first_line = raw_data.split('\n')[0]
                    detected_data = first_line.replace("Tag ID:", "").strip()
                else:
                    detected_data = raw_data.strip()
                break 
                
            cv2.imshow('Champion Scanner - Turbo Mode', frame)
            
            if detected_data or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
        if detected_data:
            target_entry.delete(0, 'end')
            target_entry.insert(0, detected_data)
            trigger_method()


    # ==========================================
    # LOGIC: BORROWING & CART VERIFICATION
    # ==========================================
    def verify_borrower(self):
        emp_id = self.b_emp_id.get().strip()
        if not emp_id: return
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, full_name, role FROM user WHERE employee_id = %s", (emp_id,))
            user = cursor.fetchone()
            
            if user:
                self.active_borrow_user_id = user['user_id']
                self.active_borrow_user_name = user['full_name']
                self.b_user_name.configure(text=f"✓ Verified: {user['full_name']} ({user['role']})", text_color="#2ECC71")
                self.b_tag_id.focus() 
            else:
                self.active_borrow_user_id = None
                self.active_borrow_user_name = None
                self.b_user_name.configure(text="❌ Employee ID not found.", text_color="#D8000C")
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def add_tool_to_cart(self):
        tag_id = self.b_tag_id.get().strip()
        if not tag_id: return
        
        for item in self.borrow_cart:
            if item['tag'] == tag_id:
                if item['qty_borrowed'] < item['max_qty']:
                    item['qty_borrowed'] += 1
                    self.refresh_cart_ui()
                    self.b_tag_id.delete(0, 'end')
                    return
                else:
                    messagebox.showwarning("Out of Stock", f"Only {item['max_qty']} of this item available in inventory.", parent=self.winfo_toplevel())
                    self.b_tag_id.delete(0, 'end')
                    return

        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT t.tool_id, t.name, t.condition, IFNULL(i.quantity_available, 0) as qty 
                FROM tool t 
                LEFT JOIN inventory i ON t.tool_id = i.tool_id 
                WHERE t.tag_id = %s AND t.is_archived = 0
            """
            cursor.execute(query, (tag_id,))
            tool = cursor.fetchone()
            
            if tool:
                if tool['qty'] > 0:
                    self.borrow_cart.append({
                        "id": tool['tool_id'],
                        "name": tool['name'],
                        "cond": tool['condition'],
                        "tag": tag_id,
                        "qty_borrowed": 1,
                        "max_qty": tool['qty']
                    })
                    self.refresh_cart_ui()
                    self.b_tag_id.delete(0, 'end') 
                else:
                    messagebox.showerror("Out of Stock", f"'{tool['name']}' is out of stock!", parent=self.winfo_toplevel())
            else:
                messagebox.showerror("Not Found", "Invalid or Unassigned Tag ID.", parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def update_cart_qty(self, index, change):
        item = self.borrow_cart[index]
        new_qty = item['qty_borrowed'] + change
        
        if new_qty > item['max_qty']:
            messagebox.showwarning("Out of Stock", f"Only {item['max_qty']} available.", parent=self.winfo_toplevel())
        elif new_qty <= 0:
            self.remove_from_cart(index)
        else:
            item['qty_borrowed'] = new_qty
            self.refresh_cart_ui()

    def refresh_cart_ui(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        if len(self.borrow_cart) == 0:
            ctk.CTkLabel(self.cart_frame, text="Cart is empty. Scan tools to add.", text_color="gray").pack(pady=10)
            return

        for i, item in enumerate(self.borrow_cart):
            row = ctk.CTkFrame(self.cart_frame, fg_color="white", corner_radius=5, height=35)
            row.pack(fill="x", pady=2, padx=5)
            row.pack_propagate(False)
            
            display_text = f"✓ {item['name']}  |  Tag: {item['tag']}"
            ctk.CTkLabel(row, text=display_text, font=("Inter", 12, "bold"), text_color="#1E4528").pack(side="left", padx=10, pady=5)
            
            ctk.CTkButton(row, text="✕", width=25, height=25, fg_color="#FFEAEA", text_color="#D8000C", hover_color="#FFC0C0", command=lambda idx=i: self.remove_from_cart(idx)).pack(side="right", padx=(5, 10))
            ctk.CTkButton(row, text="+", width=25, height=25, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=lambda idx=i: self.update_cart_qty(idx, 1)).pack(side="right", padx=2)
            ctk.CTkLabel(row, text=f"Qty: {item['qty_borrowed']}", font=("Inter", 11, "bold"), text_color="black").pack(side="right", padx=8)
            ctk.CTkButton(row, text="-", width=25, height=25, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=lambda idx=i: self.update_cart_qty(idx, -1)).pack(side="right", padx=2)

    def remove_from_cart(self, index):
        self.borrow_cart.pop(index)
        self.refresh_cart_ui()

    def execute_borrow(self):
        if not self.active_borrow_user_id:
            messagebox.showerror("Error", "Please scan and verify an Employee ID first.", parent=self.winfo_toplevel())
            return
        
        if len(self.borrow_cart) == 0:
            messagebox.showerror("Error", "The cart is empty! Scan at least one tool.", parent=self.winfo_toplevel())
            return
            
        purpose = self.b_purpose.get().strip() or "General Use"
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            transaction_ids = []
            receipt_tool_list = []
            
            for item in self.borrow_cart:
                cursor.execute("UPDATE inventory SET quantity_available = quantity_available - %s WHERE tool_id = %s", (item['qty_borrowed'], item['id']))
                
                for _ in range(item['qty_borrowed']):
                    cursor.execute("""
                        INSERT INTO transaction (user_id, tool_id, type, borrow_date, purpose, status, condition_at_borrow) 
                        VALUES (%s, %s, 'Borrow', NOW(), %s, 'Active', %s)
                    """, (self.active_borrow_user_id, item['id'], purpose, item['cond']))
                    transaction_ids.append(str(cursor.lastrowid))
                
                receipt_tool_list.append(f"{item['name']} (Qty: {item['qty_borrowed']})")
            
            conn.commit()
            
            total_items = sum(item['qty_borrowed'] for item in self.borrow_cart)
            messagebox.showinfo("Success", f"{total_items} items checked out successfully! Generating receipt...", parent=self.winfo_toplevel())
            
            master_trans_id = f"{transaction_ids[0]}-{transaction_ids[-1]}" if len(transaction_ids) > 1 else transaction_ids[0]
            self.print_master_receipt(master_trans_id, self.active_borrow_user_name, receipt_tool_list, purpose)
            
            self.b_emp_id.delete(0, 'end')
            self.b_purpose.delete(0, 'end')
            self.b_user_name.configure(text="Name: Pending Scan...", text_color="gray")
            self.active_borrow_user_id = None
            self.borrow_cart.clear()
            self.refresh_cart_ui()
            
            self.load_transaction_history()
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def print_master_receipt(self, trans_id_range, b_name, tool_names, purpose):
        try:
            canvas_height = 400 + (len(tool_names) * 30)
            canvas = Image.new('RGB', (600, canvas_height), 'white')
            draw = ImageDraw.Draw(canvas)
            
            try:
                font_title = ImageFont.truetype("arialbd.ttf", 24)
                font_body = ImageFont.truetype("arial.ttf", 20)
                font_bold = ImageFont.truetype("arialbd.ttf", 20)
            except IOError:
                font_title = font_body = font_bold = ImageFont.load_default()
                
            current_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
            
            draw.text((20, 20), "CHAMPION FINE TOOLING", fill="#1E4528", font=font_title)
            draw.text((20, 60), "MASTER CHECKOUT RECEIPT", fill="black", font=font_title)
            draw.line((20, 100, 580, 100), fill="black", width=2)
            
            draw.text((20, 120), f"Transaction ID(s): TRN-[{trans_id_range}]", fill="black", font=font_body)
            draw.text((20, 160), f"Date & Time: {current_time}", fill="black", font=font_body)
            draw.text((20, 200), f"Borrower: {b_name}", fill="black", font=font_body)
            draw.text((20, 240), f"Project/Purpose: {purpose}", fill="black", font=font_body)
            
            draw.text((20, 290), "Items Issued:", fill="black", font=font_bold)
            
            y_offset = 320
            for name in tool_names:
                draw.text((40, y_offset), f"• {name}", fill="black", font=font_body)
                y_offset += 30
                
            draw.line((20, y_offset + 30, 580, y_offset + 30), fill="black", width=1)
            draw.text((20, y_offset + 50), "Authorized Admin Signature: ___________________", fill="black", font=font_body)

            import tempfile
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"Receipt_TRN_Multi.pdf")
            canvas.save(file_path, "PDF", resolution=100.0)
            os.startfile(file_path, "print")
            
        except Exception as e:
            messagebox.showwarning("Print Warning", f"Transaction saved, but receipt failed to print:\n{e}", parent=self.winfo_toplevel())


    # ==========================================
    # LOGIC: DUAL-AUTH & RECEIPT RETURN PROCEDURE
    # ==========================================
    def verify_return_employee(self):
        emp_id = self.r_emp_id.get().strip()
        if not emp_id: return
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, full_name, role FROM user WHERE employee_id = %s", (emp_id,))
            user = cursor.fetchone()
            
            if user:
                self.active_return_user_id = user['user_id']
                # FIX: Show the verified Employee name directly on the return panel!
                self.r_user_name.configure(text=f"✓ Verified: {user['full_name']} ({user['role']})", text_color="#2ECC71")
                self.r_tag_id.focus() 
            else:
                self.active_return_user_id = None
                self.r_user_name.configure(text="❌ Employee ID not found.", text_color="#D8000C")
        except Exception as e:
            pass
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def verify_tool_for_return(self):
        if not self.active_return_user_id:
            messagebox.showwarning("Authentication Required", "Please scan Employee ID first before returning a tool.", parent=self.winfo_toplevel())
            self.r_tag_id.delete(0, 'end')
            return

        tag_input = self.r_tag_id.get().strip()
        if not tag_input: return
        
        # THE FIX: Allow Admin to type the "TRN" from the receipt instead of scanning the Tag!
        search_val = tag_input
        if tag_input.upper().startswith("TRN-"):
            search_val = tag_input.upper().replace("TRN-", "").split("-")[0] # Extracts '28' from 'TRN-28-35'

        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Step 1: Find the actual tool_id based on either the TRN or the Tag
            if search_val.isdigit():
                cursor.execute("SELECT tool_id FROM transaction WHERE transaction_id = %s AND user_id = %s AND status = 'Active'", (search_val, self.active_return_user_id))
            else:
                cursor.execute("SELECT tool_id FROM tool WHERE tag_id = %s", (search_val,))
                
            target_tool = cursor.fetchone()
            
            if not target_tool:
                self.r_record_info.configure(text="❌ No active records found for this Tag/TRN combo.", text_color="#D8000C")
                return

            # Step 2: Count all active items of that tool currently borrowed by this user
            query = """
                SELECT t.tool_id, t.name, COUNT(tr.transaction_id) as active_borrows
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                WHERE tr.tool_id = %s AND tr.status = 'Active' AND tr.user_id = %s
                GROUP BY t.tool_id, t.name
            """
            cursor.execute(query, (target_tool['tool_id'], self.active_return_user_id))
            record = cursor.fetchone()
            
            if record:
                self.active_return_tool_id = record['tool_id']
                self.max_returnable = record['active_borrows']
                self.r_record_info.configure(text=f"✓ Tool Identified: {record['name']}\nCurrently Borrowed Out: {record['active_borrows']}", text_color="#2ECC71")
                
                self.r_qty.delete(0, 'end')
                self.r_qty.insert(0, "1")
            else:
                self.active_return_tool_id = None
                self.max_returnable = 0
                self.r_record_info.configure(text="❌ No active records found.", text_color="#D8000C")
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def execute_return(self):
        if not self.active_return_tool_id or not self.active_return_user_id:
            messagebox.showerror("Error", "Please scan and verify both Employee ID and Tag ID/TRN.", parent=self.winfo_toplevel())
            return
            
        try:
            return_qty = int(self.r_qty.get().strip())
            if return_qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive whole number.", parent=self.winfo_toplevel())
            return
            
        if return_qty > self.max_returnable:
            messagebox.showerror("Error", f"Cannot return {return_qty}. You only have {self.max_returnable} of these checked out.", parent=self.winfo_toplevel())
            return

        new_cond = self.r_condition.get()
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT transaction_id FROM transaction WHERE tool_id = %s AND status = 'Active' AND user_id = %s ORDER BY borrow_date ASC LIMIT %s", (self.active_return_tool_id, self.active_return_user_id, return_qty))
            transactions_to_close = cursor.fetchall()
            
            for trans in transactions_to_close:
                cursor.execute("""
                    UPDATE transaction 
                    SET status = 'Returned', return_date = NOW(), type = 'Return', condition_at_return = %s 
                    WHERE transaction_id = %s
                """, (new_cond, trans['transaction_id']))
            
            cursor.execute("UPDATE inventory SET quantity_available = quantity_available + %s WHERE tool_id = %s", (return_qty, self.active_return_tool_id))
            cursor.execute("UPDATE tool SET `condition` = %s WHERE tool_id = %s", (new_cond, self.active_return_tool_id))
            
            conn.commit()
            messagebox.showinfo("Success", f"Successfully returned {return_qty} item(s) and restocked inventory!", parent=self.winfo_toplevel())
            
            self.r_emp_id.delete(0, 'end')
            self.r_tag_id.delete(0, 'end')
            self.r_user_name.configure(text="Name: Pending Scan...", text_color="gray")
            self.r_record_info.configure(text="Record: Pending Scan...", text_color="gray")
            self.r_condition.set("Good")
            self.r_qty.delete(0, 'end')
            self.r_qty.insert(0, "1")
            self.active_return_tool_id = None
            self.active_return_user_id = None
            self.max_returnable = 0
            
            self.load_transaction_history()
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # ==========================================
    # LOGIC: CRASH-PROOF GROUPED HISTORY TABLE
    # ==========================================
    def load_transaction_history(self):
        for widget in self.data_scroll.winfo_children():
            widget.destroy()

        search_q = self.search_entry.get().strip()
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            
            # THE FIX: This SQL Query is now 100% compliant with Cloud Database ONLY_FULL_GROUP_BY strict modes.
            # It will successfully combine items into one row and display the Qty!
            query = """
                SELECT tr.type, t.name as tool_name, t.tag_id, COUNT(tr.transaction_id) as grouped_qty,
                       u.full_name, tr.status,
                       DATE_FORMAT(DATE_ADD(MAX(tr.borrow_date), INTERVAL 8 HOUR), '%b %d, %Y %h:%i %p') as b_date
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                JOIN user u ON tr.user_id = u.user_id
            """
            
            if search_q:
                query += " WHERE u.full_name LIKE %s OR t.tag_id LIKE %s OR t.name LIKE %s"
                query += " GROUP BY tr.type, t.name, t.tag_id, u.full_name, tr.status, DATE_FORMAT(tr.borrow_date, '%Y-%m-%d %H:%i') ORDER BY MAX(tr.borrow_date) DESC LIMIT 50"
                cursor.execute(query, (f"%{search_q}%", f"%{search_q}%", f"%{search_q}%"))
            else:
                query += " GROUP BY tr.type, t.name, t.tag_id, u.full_name, tr.status, DATE_FORMAT(tr.borrow_date, '%Y-%m-%d %H:%i') ORDER BY MAX(tr.borrow_date) DESC LIMIT 50"
                cursor.execute(query)
                
            results = cursor.fetchall()
            
            if not results:
                ctk.CTkLabel(self.data_scroll, text="No transactions found.", text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(results):
                display_data = [
                    row['type'],
                    row['tool_name'],
                    row['tag_id'] if row['tag_id'] else "Unassigned",
                    str(row['grouped_qty']),
                    row['full_name'],
                    row['b_date'],
                    row['status']
                ]
                
                row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.pack_propagate(False)
                
                for col, (text, weight) in enumerate(zip(display_data, self.weights)):
                    row_frame.grid_columnconfigure(col, weight=weight)
                    
                    txt_color = "#1A1A1A"
                    if col == 6: # Status column
                        txt_color = "#D8000C" if text == "Active" else "#2ECC71"
                        
                    ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color=txt_color).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        except Exception as e:
            # Replaced "pass" with a visual error so it never fails silently again!
            ctk.CTkLabel(self.data_scroll, text=f"Data Load Error: {e}", text_color="red").pack(pady=20)
        finally:
            if conn.is_connected(): cursor.close(); conn.close()