import customtkinter as ctk
from tkinter import messagebox
from database import get_connection

class InventoryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.scroll_wrapper = ctk.CTkScrollableFrame(self, fg_color="transparent", orientation="horizontal")
        self.scroll_wrapper.pack(fill="both", expand=True)

        self.categories = ["Select category", "Tools", "Measuring", "Power Tools", "+ Add New Category"]
        self.suppliers = ["Select supplier", "ACME", "Priya", "Global Tooling", "+ Add New Supplier"]
        self.tool_hash_table = {}

        self.build_left_form()
        self.build_right_table()
        self.load_inventory_data()
        self.refresh_dropdowns()

    def build_left_form(self):
        form_frame = ctk.CTkScrollableFrame(self.scroll_wrapper, fg_color="white", corner_radius=10, width=320)
        form_frame.pack(side="left", fill="y", padx=(0, 10), pady=0)

        ctk.CTkLabel(form_frame, text="Add New Tool", font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(form_frame, text="Fill in the details below to add a new tool to the inventory.", font=("Inter", 11), text_color="gray", wraplength=220, justify="left").pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(form_frame, text="Category", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.cat_menu = ctk.CTkOptionMenu(form_frame, values=self.categories, fg_color="#F9FAFB", text_color="black", button_color="#E0E0E0", command=self.handle_category_change)
        self.cat_menu.pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(form_frame, text="Supplier", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.sup_menu = ctk.CTkOptionMenu(form_frame, values=self.suppliers, fg_color="#F9FAFB", text_color="black", button_color="#E0E0E0", command=self.handle_supplier_change)
        self.sup_menu.pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(form_frame, text="Product Name", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 3/8 Drill Bit")
        self.name_entry.pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(form_frame, text="Description (Optional)", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.desc_entry = ctk.CTkEntry(form_frame, placeholder_text="Brief description")
        self.desc_entry.pack(fill="x", padx=20, pady=(5, 10))

        row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=20, pady=(5, 10))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        p_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        p_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(p_frame, text="Price (Optional)", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w")
        self.price_entry = ctk.CTkEntry(p_frame, placeholder_text="0.00")
        self.price_entry.pack(fill="x", pady=(5, 0))

        q_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        q_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(q_frame, text="Quantity", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w")
        self.qty_entry = ctk.CTkEntry(q_frame, placeholder_text="0")
        self.qty_entry.pack(fill="x", pady=(5, 0))

        ctk.CTkLabel(form_frame, text="Storage Location (Optional)", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.loc_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Shelf A1, Cabinet B3")
        self.loc_entry.pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(form_frame, text="Status", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.status_menu = ctk.CTkOptionMenu(form_frame, values=["Good", "Needs Repair", "Damaged", "Lost"], fg_color="#F9FAFB", text_color="black", button_color="#E0E0E0")
        self.status_menu.pack(fill="x", padx=20, pady=(5, 15))

        btn_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(10, 20))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Add Tool", fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=self.validate_and_save).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(btn_row, text="Clear Form", fg_color="white", text_color="black", border_width=1, border_color="#E0E0E0", hover_color="#F0F0F0", font=("Inter", 12, "bold"), command=self.clear_form).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def build_right_table(self):
        table_frame = ctk.CTkFrame(self.scroll_wrapper, fg_color="white", corner_radius=10, width=900)
        table_frame.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=0)

        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        self.filter_menu = ctk.CTkOptionMenu(search_frame, values=["All Fields (Universal)", "By: PID", "By: Name", "By: Status", "By: Category"], width=170, fg_color="#F9FAFB", text_color="black")
        self.filter_menu.pack(side="left", padx=(0, 10))

        self.sort_menu = ctk.CTkOptionMenu(search_frame, values=["Newest Added", "Oldest Added", "Name (A-Z)"], width=130, fg_color="#E8F8F5", text_color="#1E4528", button_color="#D5F5E3")
        self.sort_menu.pack(side="left", padx=(0, 10))
        self.sort_menu.configure(command=lambda e: self.perform_search())

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search inventory...", width=250)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_btn = ctk.CTkButton(search_frame, text="Search", width=80, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 12, "bold"), command=self.perform_search)
        self.search_btn.pack(side="left", padx=10)
        
        self.reset_btn = ctk.CTkButton(search_frame, text="↻ Reset", width=70, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", font=("Inter", 12, "bold"), command=self.reset_search)
        self.reset_btn.pack(side="left", padx=(10, 0))

        header_frame = ctk.CTkFrame(table_frame, fg_color="#1E4528", corner_radius=5, height=40)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)

        # UI FIX: Swapped "Description" for "Category" and "Supplier" so it's visible on the main page
        self.headers = ["PID", "Name", "Category", "Supplier", "Price", "Qty Avail.", "Location", "Status"]
        self.weights = [1, 2, 2, 2, 1, 1, 2, 1]

        for col, (text, weight) in enumerate(zip(self.headers, self.weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    def load_inventory_data(self, query="", filter_type="All Fields (Universal)", sort_type="Newest Added"):
        for widget in self.data_scroll.winfo_children(): widget.destroy()
        self.tool_hash_table.clear() 

        conn = get_connection() 
        if not conn: return

        try:
            cursor = conn.cursor(dictionary=True)
            
            # THE BUG FIX: Selecting quantity_available instead of quantity_total!
            base_query = """
                SELECT t.tool_id, t.name, IFNULL(t.description, 'N/A') as description, t.price, 
                       IFNULL(i.quantity_available, 0) as qty_avail, IFNULL(i.quantity_total, 0) as qty_tot, 
                       IFNULL(t.location, 'N/A') as location, t.`condition` as status,
                       IFNULL(t.category, 'Uncategorized') as category, IFNULL(t.supplier, 'N/A') as supplier
                FROM tool t LEFT JOIN inventory i ON t.tool_id = i.tool_id
                WHERE t.is_archived = 0
            """
            
            params = []
            if query:
                if filter_type == "All Fields (Universal)":
                    base_query += """ AND (
                        t.name LIKE %s OR t.tool_id LIKE %s OR t.category LIKE %s OR t.supplier LIKE %s OR 
                        IFNULL(t.description, '') LIKE %s OR CAST(t.price AS CHAR) LIKE %s OR 
                        IFNULL(t.location, '') LIKE %s OR t.`condition` LIKE %s
                    )"""
                    params.extend([f"%{query}%"] * 8)
                elif filter_type == "By: PID":
                    base_query += " AND t.tool_id LIKE %s"
                    params.append(f"%{query}%")
                elif filter_type == "By: Name":
                    base_query += " AND t.name LIKE %s"
                    params.append(f"%{query}%")
                elif filter_type == "By: Status":
                    base_query += " AND t.`condition` LIKE %s"
                    params.append(f"%{query}%")
                elif filter_type == "By: Category":
                    base_query += " AND t.category LIKE %s"
                    params.append(f"%{query}%")

            if sort_type == "Newest Added":
                base_query += " ORDER BY t.tool_id DESC"
            elif sort_type == "Oldest Added":
                base_query += " ORDER BY t.tool_id ASC"
            elif sort_type == "Name (A-Z)":
                base_query += " ORDER BY t.name ASC"

            cursor.execute(base_query, tuple(params))
            results = cursor.fetchall()

            if not results:
                ctk.CTkLabel(self.data_scroll, text="No items found matching your search.", text_color="gray").pack(pady=20)
                return

            for i, row in enumerate(results):
                pid = str(row['tool_id'])
                # We save the raw row to the Hash Table so the edit modal can still pull the "quantity_total"
                self.tool_hash_table[pid] = row 
                
                display_data = [pid, row['name'], row['category'], row['supplier'], row['price'], f"{row['qty_avail']} / {row['qty_tot']}", row['location'], row['status']]
                
                row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
                row_frame.pack(fill="x", pady=2)
                row_frame.pack_propagate(False)
                row_frame.bind("<Button-1>", lambda e, lookup_id=pid: self.open_tool_modal(lookup_id))

                for col, (text, weight) in enumerate(zip(display_data, self.weights)):
                    row_frame.grid_columnconfigure(col, weight=weight)
                    lbl = ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color="#1A1A1A")
                    lbl.grid(row=0, column=col, padx=10, pady=10, sticky="w")
                    lbl.bind("<Button-1>", lambda e, lookup_id=pid: self.open_tool_modal(lookup_id))

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {e}", parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def perform_search(self):
        query = self.search_entry.get().strip()
        filter_type = self.filter_menu.get()
        sort_type = self.sort_menu.get()
        self.load_inventory_data(query, filter_type, sort_type)
        
    def reset_search(self):
        self.search_entry.delete(0, 'end')
        self.filter_menu.set("All Fields (Universal)")
        self.sort_menu.set("Newest Added")
        self.load_inventory_data()

    def validate_and_save(self):
        cat = self.cat_menu.get()
        sup = self.sup_menu.get()
        name = self.name_entry.get().strip()
        desc = self.desc_entry.get().strip()
        loc = self.loc_entry.get().strip()
        status = self.status_menu.get() 
        
        if not name or cat == "Select category" or sup == "Select supplier":
            messagebox.showerror("Validation Error", "Category, Supplier, and Product Name are required.", parent=self.winfo_toplevel())
            return

        price_val = self.price_entry.get().strip()
        try:
            price = float(price_val) if price_val else 0.00
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Type Error", "Price must be a number (or left blank), and Quantity must be a whole number.", parent=self.winfo_toplevel())
            return

        conn = get_connection() 
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tool (category, supplier, name, description, price, location, `condition`, date_acquired, is_archived) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 0)", 
                           (cat, sup, name, desc, price, loc, status))
            new_tool_id = cursor.lastrowid
            cursor.execute("INSERT INTO inventory (tool_id, quantity_total, quantity_available) VALUES (%s, %s, %s)", (new_tool_id, qty, qty))
            conn.commit()
            messagebox.showinfo("Success", "Tool securely added to the database.", parent=self.winfo_toplevel())
            self.clear_form()
            self.load_inventory_data()
            self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save tool: {e}", parent=self.winfo_toplevel())
        finally:
            if conn.is_connected(): cursor.close(); conn.close()

    def open_tool_modal(self, lookup_id):
        data = self.tool_hash_table.get(lookup_id)
        if not data: return
        
        modal = ctk.CTkToplevel(self)
        modal.title(f"Manage Tool: {lookup_id}")
        modal.geometry("450x650") 
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()

        modal.update_idletasks()
        x = int((modal.winfo_screenwidth() / 2) - (450 / 2))
        y = int((modal.winfo_screenheight() / 2) - (650 / 2))
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"Product Details: {data['name']}", font=("Inter", 16, "bold"), text_color="black").pack(pady=20)
        
        form_frame = ctk.CTkFrame(modal, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30)
        
        def create_modal_row(parent, label, value):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            ctk.CTkLabel(frame, text=label, width=80, anchor="w", font=("Inter", 12, "bold"), text_color="gray").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            entry.insert(0, value)
            return entry

        cat_entry = create_modal_row(form_frame, "Category", data['category'])
        sup_entry = create_modal_row(form_frame, "Supplier", data['supplier'])
        name_entry = create_modal_row(form_frame, "Name", data['name'])
        price_entry = create_modal_row(form_frame, "Price", data['price'])
        
        # When editing, we edit the Total max capacity
        qty_entry = create_modal_row(form_frame, "Max Qty", data['qty_tot'])
        
        loc_entry = create_modal_row(form_frame, "Location", data['location'])
        desc_entry = create_modal_row(form_frame, "Descript.", data['description'])
        
        status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(status_frame, text="Condition", width=80, anchor="w", font=("Inter", 12, "bold"), text_color="gray").pack(side="left")
        status_menu = ctk.CTkOptionMenu(status_frame, values=["Good", "Needs Repair", "Damaged", "Lost"], fg_color="#F9FAFB", text_color="black")
        status_menu.pack(side="left", fill="x", expand=True)
        status_menu.set(data['status'])

        def execute_update():
            price_val = price_entry.get().strip()
            try:
                new_price = float(price_val) if price_val else 0.00
                new_qty = int(qty_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Price must be a number (or left blank) and Quantity must be a whole number.", parent=modal)
                return
                
            if messagebox.askyesno("Confirm Update", "Save these changes to the database?", parent=modal):
                conn = get_connection()
                if not conn: return
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tool SET category=%s, supplier=%s, name=%s, price=%s, location=%s, description=%s, `condition`=%s WHERE tool_id=%s",
                                   (cat_entry.get(), sup_entry.get(), name_entry.get(), new_price, loc_entry.get(), desc_entry.get(), status_menu.get(), lookup_id))
                    
                    # Update inventory safely. We adjust total, and available jumps proportionally.
                    qty_difference = new_qty - int(data['qty_tot'])
                    cursor.execute("UPDATE inventory SET quantity_total=%s, quantity_available=quantity_available + %s WHERE tool_id=%s", 
                                   (new_qty, qty_difference, lookup_id))
                                   
                    conn.commit()
                    messagebox.showinfo("Success", "Tool updated successfully.", parent=modal)
                    modal.destroy()
                    self.load_inventory_data() 
                except Exception as e:
                    messagebox.showerror("Database Error", str(e), parent=modal)
                finally:
                    if conn.is_connected(): cursor.close(); conn.close()

        def execute_archive():
            if messagebox.askyesno("Confirm Archive", "Are you sure you want to Archive this tool? It will be hidden from the active inventory.", parent=modal):
                conn = get_connection() 
                if not conn: return
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tool SET is_archived=1, archived_at=NOW() WHERE tool_id=%s", (lookup_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Tool archived.", parent=modal)
                    modal.destroy()
                    self.load_inventory_data() 
                except Exception as e:
                    messagebox.showerror("Database Error", str(e), parent=modal)
                finally:
                    if conn.is_connected(): cursor.close(); conn.close()

        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btn_row, text="Update", fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", command=execute_update).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Archive", fg_color="#D3B8A7", text_color="black", hover_color="#BFA595", command=execute_archive).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Close", fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=modal.destroy).pack(side="right", padx=5)

    def handle_category_change(self, choice):
        if choice == "+ Add New Category":
            dialog = ctk.CTkInputDialog(text="Enter new category name:", title="Add Category")
            new_val = dialog.get_input()
            if new_val and new_val.strip():
                self.categories.insert(-1, new_val.strip()) 
                self.cat_menu.configure(values=self.categories)
                self.cat_menu.set(new_val.strip())
            else:
                self.cat_menu.set("Select category")

    def handle_supplier_change(self, choice):
        if choice == "+ Add New Supplier":
            dialog = ctk.CTkInputDialog(text="Enter new supplier name:", title="Add Supplier")
            new_val = dialog.get_input()
            if new_val and new_val.strip():
                self.suppliers.insert(-1, new_val.strip()) 
                self.sup_menu.configure(values=self.suppliers)
                self.sup_menu.set(new_val.strip())
            else:
                self.sup_menu.set("Select supplier")

    def clear_form(self):
        self.cat_menu.set("Select category")
        self.sup_menu.set("Select supplier")
        self.name_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.qty_entry.delete(0, 'end')
        self.loc_entry.delete(0, 'end')
        self.status_menu.set("Good")
    
    def refresh_dropdowns(self):
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM tool WHERE category IS NOT NULL AND category != ''")
            db_cats = [row[0] for row in cursor.fetchall()]
            new_cats = ["Select category", "Tools", "Measuring", "Power Tools"] + [c for c in db_cats if c not in ["Tools", "Measuring", "Power Tools"]] + ["+ Add New Category"]
            self.cat_menu.configure(values=new_cats)
            self.categories = new_cats

            cursor.execute("SELECT DISTINCT supplier FROM tool WHERE supplier IS NOT NULL AND supplier != ''")
            db_sups = [row[0] for row in cursor.fetchall()]
            new_sups = ["Select supplier", "ACME", "Priya", "Global Tooling"] + [s for s in db_sups if s not in ["ACME", "Priya", "Global Tooling"]] + ["+ Add New Supplier"]
            self.sup_menu.configure(values=new_sups)
            self.suppliers = new_sups
        except Exception as e:
            pass
        finally:
            if conn.is_connected(): cursor.close(); conn.close()