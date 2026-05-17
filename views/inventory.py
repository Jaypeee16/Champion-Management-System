import customtkinter as ctk
from tkinter import messagebox
from database import get_connection

# 1. CHANGE THIS INHERITANCE: Inherit from CTkScrollableFrame instead of CTkFrame
class InventoryView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        # 2. CHANGE THIS INIT: Add orientation="horizontal"
        super().__init__(parent, fg_color="transparent", orientation="horizontal")
        self.db_conn = get_connection() 

        # 3. ADD MINSIZE: This forces the scrollbar to appear instead of squishing text!
        self.grid_columnconfigure(0, weight=1, minsize=320)  # Left form must be at least 320px
        self.grid_columnconfigure(1, weight=3, minsize=750)  # Right table must be at least 750px
        self.grid_rowconfigure(0, weight=1)

        self.categories = ["Select category", "Tools", "Measuring", "Power Tools", "+ Add New Category"]
        self.suppliers = ["Select supplier", "ACME", "Priya", "Global Tooling", "+ Add New Supplier"]

        self.build_left_form()
        self.build_right_table()
        
        self.load_inventory_data()
        self.refresh_dropdowns()

    def build_left_form(self):
        form_frame = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

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
        self.desc_entry = ctk.CTkEntry(form_frame, placeholder_text="Brief description of the tool")
        self.desc_entry.pack(fill="x", padx=20, pady=(5, 10))

        row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=20, pady=(5, 10))
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        p_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        p_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(p_frame, text="Price", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w")
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
        self.status_menu = ctk.CTkOptionMenu(form_frame, values=["Active", "Inactive", "Maintenance"], fg_color="#F9FAFB", text_color="black", button_color="#E0E0E0")
        self.status_menu.pack(fill="x", padx=20, pady=(5, 15))

        btn_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(10, 20))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Add Tool", fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=self.validate_and_save).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(btn_row, text="Clear Form", fg_color="white", text_color="black", border_width=1, border_color="#E0E0E0", hover_color="#F0F0F0", font=("Inter", 12, "bold"), command=self.clear_form).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def build_right_table(self):
        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        self.filter_menu = ctk.CTkOptionMenu(search_frame, values=["By: Name", "By: PID", "By: Category"], width=160, fg_color="#F9FAFB", text_color="black")
        self.filter_menu.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search inventory...", width=250)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_btn = ctk.CTkButton(search_frame, text="Q", width=40, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 14, "bold"), command=self.perform_search)
        self.search_btn.pack(side="left", padx=10)
        
        # FEATURE FIX: Added Reset Search Button
        self.reset_btn = ctk.CTkButton(search_frame, text="↻ Reset", width=70, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", font=("Inter", 12, "bold"), command=self.reset_search)
        self.reset_btn.pack(side="left", padx=(10, 0))

        header_frame = ctk.CTkFrame(table_frame, fg_color="#1E4528", corner_radius=5, height=40)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)

        self.headers = ["PID", "Category", "Supplier", "Name", "Price", "Qty", "Status"]
        self.weights = [1, 2, 2, 3, 1, 1, 1]

        for col, (text, weight) in enumerate(zip(self.headers, self.weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    # --- DATABASE & LOGIC METHODS ---

    def load_inventory_data(self, query="", filter_type="By: Name"):
        for widget in self.data_scroll.winfo_children():
            widget.destroy()

        conn = get_connection() # CLOUD FIX: Always get a fresh connection!
        if not conn: return

        try:
            cursor = conn.cursor()
            
            # Fetching ALL 9 columns, including the new Category, Price, and Location!
            base_query = """
                SELECT t.tool_id, t.category, t.supplier, t.name, t.price, 
                       IFNULL(i.quantity_total, 0), t.condition, t.description, t.location
                FROM tool t
                LEFT JOIN inventory i ON t.tool_id = i.tool_id
                WHERE t.is_archived = 0
            """

            if query:
                col_map = {"By: Name": "t.name", "By: PID": "t.tool_id", "By: Category": "t.category"} 
                db_column = col_map.get(filter_type, "t.name")
                cursor.execute(base_query + f" AND {db_column} LIKE %s", (f"%{query}%",))
            else:
                cursor.execute(base_query)

            results = cursor.fetchall()

            if not results:
                ctk.CTkLabel(self.data_scroll, text="No items found in the database.", text_color="gray").pack(pady=20)
                return

            for i, row_data in enumerate(results):
                display_data = [str(item) for item in row_data] 
                
                row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
                row_frame.pack(fill="x", pady=2)
                row_frame.pack_propagate(False)
                
                # Binds the click event to open the modal and passes all 9 pieces of data
                row_frame.bind("<Button-1>", lambda e, data=display_data: self.open_tool_modal(data))

                # We only loop through the first 7 items for the main table UI
                for col, (text, weight) in enumerate(zip(display_data[:7], self.weights)):
                    row_frame.grid_columnconfigure(col, weight=weight)
                    lbl = ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color="#1A1A1A")
                    lbl.grid(row=0, column=col, padx=10, pady=10, sticky="w")
                    lbl.bind("<Button-1>", lambda e, data=display_data: self.open_tool_modal(data))

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {e}", parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def perform_search(self):
        query = self.search_entry.get().strip()
        filter_type = self.filter_menu.get()
        self.load_inventory_data(query, filter_type)
        
    def reset_search(self):
        self.search_entry.delete(0, 'end')
        self.filter_menu.set("By: Name")
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

        try:
            price = float(self.price_entry.get())
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Type Error", "Price must be a number, and Quantity must be a whole number.", parent=self.winfo_toplevel())
            return

        conn = get_connection() # CLOUD FIX: Fresh Connection
        if not conn: return

        try:
            cursor = conn.cursor()
            
            # Now saving to ALL the columns, including our newly created ones!
            tool_query = "INSERT INTO tool (category, supplier, name, description, price, location, `condition`, date_acquired, is_archived) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), 0)"
            cursor.execute(tool_query, (cat, sup, name, desc, price, loc, status))
            
            new_tool_id = cursor.lastrowid
            
            inv_query = "INSERT INTO inventory (tool_id, quantity_total, quantity_available) VALUES (%s, %s, %s)"
            cursor.execute(inv_query, (new_tool_id, qty, qty))
            
            conn.commit()
            messagebox.showinfo("Success", "Tool securely added to the database.", parent=self.winfo_toplevel())
            
            self.clear_form()
            self.load_inventory_data()
            self.refresh_dropdowns()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save tool: {e}", parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def open_tool_modal(self, data):
        modal = ctk.CTkToplevel(self)
        pid = data[0]
        name = data[3]
        
        modal.title(f"Manage Tool: {pid}")
        modal.geometry("450x650") # Made taller to fit the new fields
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()
        
        modal.update_idletasks()
        x = int((modal.winfo_screenwidth() / 2) - (450 / 2))
        y = int((modal.winfo_screenheight() / 2) - (650 / 2))
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"Product Details: {name}", font=("Inter", 16, "bold"), text_color="black").pack(pady=20)
        
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

        # Data map: 0:PID, 1:Cat, 2:Sup, 3:Name, 4:Price, 5:Qty, 6:Cond, 7:Desc, 8:Loc
        # ALL fields are now editable!
        cat_entry = create_modal_row(form_frame, "Category", data[1])
        sup_entry = create_modal_row(form_frame, "Supplier", data[2])
        name_entry = create_modal_row(form_frame, "Name", data[3])
        price_entry = create_modal_row(form_frame, "Price", data[4])
        qty_entry = create_modal_row(form_frame, "Quantity", data[5])
        loc_entry = create_modal_row(form_frame, "Location", data[8])
        desc_entry = create_modal_row(form_frame, "Descript.", data[7])
        
        status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(status_frame, text="Condition", width=80, anchor="w", font=("Inter", 12, "bold"), text_color="gray").pack(side="left")
        status_menu = ctk.CTkOptionMenu(status_frame, values=["Good", "Needs Repair", "Damaged", "Lost"], fg_color="#F9FAFB", text_color="black")
        status_menu.pack(side="left", fill="x", expand=True)
        status_menu.set(data[6])

        def execute_update():
            try:
                new_price = float(price_entry.get())
                new_qty = int(qty_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Price and Quantity must be numbers.", parent=modal)
                return
                
            if messagebox.askyesno("Confirm Update", "Save these changes to the database?", parent=modal):
                conn = get_connection() # CLOUD FIX: Fresh Connection
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tool SET category=%s, supplier=%s, name=%s, price=%s, location=%s, description=%s, `condition`=%s WHERE tool_id=%s",
                                   (cat_entry.get(), sup_entry.get(), name_entry.get(), new_price, loc_entry.get(), desc_entry.get(), status_menu.get(), pid))
                    
                    cursor.execute("UPDATE inventory SET quantity_total=%s, quantity_available=%s WHERE tool_id=%s", 
                                   (new_qty, new_qty, pid))
                    
                    conn.commit()
                    messagebox.showinfo("Success", "Tool updated successfully.", parent=modal)
                    modal.destroy()
                    self.load_inventory_data() 
                except Exception as e:
                    messagebox.showerror("Database Error", str(e), parent=modal)
                finally:
                    if conn.is_connected():
                        cursor.close()
                        conn.close()

        def execute_archive():
            if messagebox.askyesno("Confirm Archive", "Are you sure you want to Archive this tool? It will be hidden from the active inventory.", parent=modal):
                conn = get_connection() # CLOUD FIX: Fresh Connection
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tool SET is_archived=1, archived_at=NOW() WHERE tool_id=%s", (pid,))
                    conn.commit()
                    messagebox.showinfo("Success", "Tool archived.", parent=modal)
                    modal.destroy()
                    self.load_inventory_data() 
                except Exception as e:
                    messagebox.showerror("Database Error", str(e), parent=modal)
                finally:
                    if conn.is_connected():
                        cursor.close()
                        conn.close()

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
        self.status_menu.set("Active")
    
    def refresh_dropdowns(self):
        """Scans the database for unique categories and suppliers and updates the menus."""
        conn = get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            
            # Fetch unique categories
            cursor.execute("SELECT DISTINCT category FROM tool WHERE category IS NOT NULL AND category != ''")
            db_cats = [row[0] for row in cursor.fetchall()]
            new_cats = ["Select category", "Tools", "Measuring", "Power Tools"] + [c for c in db_cats if c not in ["Tools", "Measuring", "Power Tools"]] + ["+ Add New Category"]
            self.cat_menu.configure(values=new_cats)
            self.categories = new_cats

            # Fetch unique suppliers
            cursor.execute("SELECT DISTINCT supplier FROM tool WHERE supplier IS NOT NULL AND supplier != ''")
            db_sups = [row[0] for row in cursor.fetchall()]
            new_sups = ["Select supplier", "ACME", "Priya", "Global Tooling"] + [s for s in db_sups if s not in ["ACME", "Priya", "Global Tooling"]] + ["+ Add New Supplier"]
            self.sup_menu.configure(values=new_sups)
            self.suppliers = new_sups
            
        except Exception as e:
            print(f"Dropdown refresh failed: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
