import customtkinter as ctk
from tkinter import messagebox
from database import get_connection

class BorrowingView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        # Using horizontal orientation to prevent squishing on small screens
        super().__init__(parent, fg_color="transparent", orientation="horizontal")
        
        self.grid_columnconfigure(0, weight=1, minsize=1000) 
        self.grid_rowconfigure(2, weight=1)

        # Temporary storage for verified scans before committing the transaction
        self.active_borrow_user_id = None
        self.active_borrow_tool_id = None
        self.active_borrow_tool_cond = None
        
        self.active_return_trans_id = None
        self.active_return_tool_id = None

        self.build_forms_section()
        self.build_history_table()
        
        self.load_transaction_history()

    def build_forms_section(self):
        forms_container = ctk.CTkFrame(self, fg_color="transparent")
        forms_container.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        forms_container.grid_columnconfigure(0, weight=1, minsize=450)
        forms_container.grid_columnconfigure(1, weight=1, minsize=450)

        # ==========================================
        # LEFT PANEL: THE BORROWING PROCESS
        # ==========================================
        borrow_card = ctk.CTkFrame(forms_container, fg_color="white", corner_radius=10)
        borrow_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(borrow_card, text="📤 Checkout / Borrow Tool", font=("Inter", 16, "bold"), text_color="#1E4528").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(borrow_card, text="Scan IDs and press Enter to verify before borrowing.", font=("Inter", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        # Borrower Section
        ctk.CTkLabel(borrow_card, text="1. Borrower ID (Employee ID)", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.b_emp_id = ctk.CTkEntry(borrow_card, placeholder_text="Scan ID & Press Enter...")
        self.b_emp_id.pack(fill="x", padx=20, pady=(5, 5))
        self.b_emp_id.bind("<Return>", lambda e: self.verify_borrower())
        
        self.b_user_name = ctk.CTkLabel(borrow_card, text="Name: Pending Scan...", font=("Inter", 12), text_color="gray")
        self.b_user_name.pack(anchor="w", padx=20, pady=(0, 15))

        # Tool Section
        ctk.CTkLabel(borrow_card, text="2. Tool Tag ID", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.b_tag_id = ctk.CTkEntry(borrow_card, placeholder_text="Scan Tag & Press Enter...")
        self.b_tag_id.pack(fill="x", padx=20, pady=(5, 5))
        self.b_tag_id.bind("<Return>", lambda e: self.verify_tool_for_borrow())

        self.b_tool_info = ctk.CTkLabel(borrow_card, text="Tool: Pending Scan...", font=("Inter", 12), text_color="gray")
        self.b_tool_info.pack(anchor="w", padx=20, pady=(0, 15))

        # Details
        ctk.CTkLabel(borrow_card, text="3. Purpose / Project", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.b_purpose = ctk.CTkEntry(borrow_card, placeholder_text="e.g., Maintenance Room B")
        self.b_purpose.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkButton(borrow_card, text="Confirm Borrow", height=40, fg_color="#1E4528", hover_color="#14301C", font=("Inter", 13, "bold"), command=self.execute_borrow).pack(fill="x", padx=20, pady=(0, 20))


        # ==========================================
        # RIGHT PANEL: THE RETURN PROCESS
        # ==========================================
        return_card = ctk.CTkFrame(forms_container, fg_color="white", corner_radius=10)
        return_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(return_card, text="📥 Return Tool", font=("Inter", 16, "bold"), text_color="#F1C40F").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(return_card, text="Scan the returned tool's Tag to pull up the active record.", font=("Inter", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkLabel(return_card, text="1. Tool Tag ID", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.r_tag_id = ctk.CTkEntry(return_card, placeholder_text="Scan Tag & Press Enter...")
        self.r_tag_id.pack(fill="x", padx=20, pady=(5, 5))
        self.r_tag_id.bind("<Return>", lambda e: self.verify_tool_for_return())

        self.r_record_info = ctk.CTkLabel(return_card, text="Record: Pending Scan...", font=("Inter", 12), text_color="gray", justify="left")
        self.r_record_info.pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkLabel(return_card, text="2. Condition Upon Return", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.r_condition = ctk.CTkOptionMenu(return_card, values=["Good", "Needs Repair", "Damaged", "Lost"], fg_color="#F9FAFB", text_color="black")
        self.r_condition.pack(fill="x", padx=20, pady=(5, 20))

        ctk.CTkButton(return_card, text="Confirm Return", height=40, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 13, "bold"), command=self.execute_return).pack(fill="x", padx=20, pady=(0, 20))


    def build_history_table(self):
        history_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        history_card.grid(row=1, column=0, sticky="nsew")
        
        # Search & Filter header inside the history card
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

        self.headers = ["ID", "Type", "Tool Name", "Borrower", "Date & Time", "Status"]
        self.weights = [1, 1, 2, 2, 2, 1]

        for col, (text, weight) in enumerate(zip(self.headers, self.weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 11, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(history_card, fg_color="transparent", height=400)
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 15))

    # ==========================================
    # LOGIC: VERIFICATION PROCEDURES
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
                self.b_user_name.configure(text=f"✓ Verified: {user['full_name']} ({user['role']})", text_color="#2ECC71")
                self.b_tag_id.focus() # Auto-move cursor to next box
            else:
                self.active_borrow_user_id = None
                self.b_user_name.configure(text="❌ Employee ID not found.", text_color="#D8000C")
        except Exception as e:
            print(e)
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def verify_tool_for_borrow(self):
        tag_id = self.b_tag_id.get().strip()
        if not tag_id: return
        
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
                    self.active_borrow_tool_id = tool['tool_id']
                    self.active_borrow_tool_cond = tool['condition']
                    self.b_tool_info.configure(text=f"✓ Available: {tool['name']}\nCond: {tool['condition']} | Stock: {tool['qty']}", text_color="#2ECC71")
                    self.b_purpose.focus()
                else:
                    self.active_borrow_tool_id = None
                    self.b_tool_info.configure(text=f"❌ '{tool['name']}' is out of stock!", text_color="#D8000C")
            else:
                self.active_borrow_tool_id = None
                self.b_tool_info.configure(text="❌ Invalid or Unassigned Tag ID.", text_color="#D8000C")
        except Exception as e:
            print(e)
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def verify_tool_for_return(self):
        tag_id = self.r_tag_id.get().strip()
        if not tag_id: return
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT tr.transaction_id, tr.tool_id, t.name, u.full_name, DATE_FORMAT(DATE_ADD(tr.borrow_date, INTERVAL 8 HOUR), '%b %d, %h:%i %p') as b_date
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                JOIN user u ON tr.user_id = u.user_id
                WHERE t.tag_id = %s AND tr.status = 'Active'
            """
            cursor.execute(query, (tag_id,))
            record = cursor.fetchone()
            
            if record:
                self.active_return_trans_id = record['transaction_id']
                self.active_return_tool_id = record['tool_id']
                self.r_record_info.configure(text=f"✓ Found Active Record:\nTool: {record['name']}\nBorrowed By: {record['full_name']}\nDate: {record['b_date']}", text_color="#2ECC71")
            else:
                self.active_return_trans_id = None
                self.r_record_info.configure(text="❌ No active borrowing record found for this Tag.", text_color="#D8000C")
        except Exception as e:
            print(e)
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    # ==========================================
    # LOGIC: EXECUTE TRANSACTIONS
    # ==========================================
    def execute_borrow(self):
        if not self.active_borrow_user_id or not self.active_borrow_tool_id:
            messagebox.showerror("Error", "Please scan and verify both Employee ID and Tag ID first.", parent=self.winfo_toplevel())
            return
            
        purpose = self.b_purpose.get().strip() or "General Use"
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            
            # 1. Log Transaction
            cursor.execute("""
                INSERT INTO transaction (user_id, tool_id, type, borrow_date, purpose, status, condition_at_borrow) 
                VALUES (%s, %s, 'Borrow', NOW(), %s, 'Active', %s)
            """, (self.active_borrow_user_id, self.active_borrow_tool_id, purpose, self.active_borrow_tool_cond))
            
            # 2. Deduct Inventory
            cursor.execute("UPDATE inventory SET quantity_available = quantity_available - 1 WHERE tool_id = %s", (self.active_borrow_tool_id,))
            
            conn.commit()
            messagebox.showinfo("Success", "Tool checked out successfully!", parent=self.winfo_toplevel())
            
            # Reset Form
            self.b_emp_id.delete(0, 'end')
            self.b_tag_id.delete(0, 'end')
            self.b_purpose.delete(0, 'end')
            self.b_user_name.configure(text="Name: Pending Scan...", text_color="gray")
            self.b_tool_info.configure(text="Tool: Pending Scan...", text_color="gray")
            self.active_borrow_user_id = None
            self.active_borrow_tool_id = None
            
            self.load_transaction_history()
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def execute_return(self):
        if not self.active_return_trans_id:
            messagebox.showerror("Error", "Please scan a valid Tag ID to find the active record.", parent=self.winfo_toplevel())
            return
            
        new_cond = self.r_condition.get()
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            
            # 1. Close Transaction
            cursor.execute("""
                UPDATE transaction 
                SET status = 'Returned', return_date = NOW(), type = 'Return', condition_at_return = %s 
                WHERE transaction_id = %s
            """, (new_cond, self.active_return_trans_id))
            
            # 2. Restock Inventory
            cursor.execute("UPDATE inventory SET quantity_available = quantity_available + 1 WHERE tool_id = %s", (self.active_return_tool_id,))
            
            # 3. Update Tool Condition
            cursor.execute("UPDATE tool SET `condition` = %s WHERE tool_id = %s", (new_cond, self.active_return_tool_id))
            
            conn.commit()
            messagebox.showinfo("Success", "Tool returned and inventory restocked!", parent=self.winfo_toplevel())
            
            # Reset Form
            self.r_tag_id.delete(0, 'end')
            self.r_record_info.configure(text="Record: Pending Scan...", text_color="gray")
            self.r_condition.set("Good")
            self.active_return_trans_id = None
            
            self.load_transaction_history()
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def load_transaction_history(self):
        for widget in self.data_scroll.winfo_children():
            widget.destroy()

        search_q = self.search_entry.get().strip()
        
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Using DATE_ADD interval 8 to convert UTC to Philippine Time
            query = """
                SELECT tr.transaction_id, tr.type, t.name as tool_name, u.full_name, 
                       DATE_FORMAT(DATE_ADD(tr.borrow_date, INTERVAL 8 HOUR), '%b %d, %Y %h:%i %p') as b_date,
                       tr.status
                FROM transaction tr
                JOIN tool t ON tr.tool_id = t.tool_id
                JOIN user u ON tr.user_id = u.user_id
            """
            
            if search_q:
                query += " WHERE u.full_name LIKE %s OR t.tag_id LIKE %s OR t.name LIKE %s"
                query += " ORDER BY tr.borrow_date DESC LIMIT 50"
                cursor.execute(query, (f"%{search_q}%", f"%{search_q}%", f"%{search_q}%"))
            else:
                query += " ORDER BY tr.borrow_date DESC LIMIT 50"
                cursor.execute(query)
                
            results = cursor.fetchall()
            
            if not results:
                ctk.CTkLabel(self.data_scroll, text="No transactions found.", text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(results):
                display_data = [
                    str(row['transaction_id']),
                    row['type'],
                    row['tool_name'],
                    row['full_name'],
                    row['b_date'],
                    row['status']
                ]
                
                row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.pack_propagate(False)
                
                for col, (text, weight) in enumerate(zip(display_data, self.weights)):
                    row_frame.grid_columnconfigure(col, weight=weight)
                    
                    # Highlight Status Colors
                    txt_color = "#1A1A1A"
                    if col == 5:
                        txt_color = "#D8000C" if text == "Active" else "#2ECC71"
                        
                    ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color=txt_color).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        except Exception as e:
            print(f"History Load Error: {e}")
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
