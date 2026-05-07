import customtkinter as ctk
from tkinter import messagebox
from database import get_connection

class InventoryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_conn = get_connection() # GETS ITS OWN CONNECTION SAFELY

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Dynamic State Variables
        self.categories = ["Select category", "Tools", "Measuring", "Power Tools", "+ Add New Category"]
        self.suppliers = ["Select supplier", "ACME", "Priya", "Global Tooling", "+ Add New Supplier"]

        self.build_left_form()
        self.build_right_table()

    def build_left_form(self):
        form_frame = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        ctk.CTkLabel(form_frame, text="Add New Tool", font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(form_frame, text="Fill in the details below to add a new tool to the inventory.", font=("Inter", 11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 20))

        # Dynamic Category Menu
        ctk.CTkLabel(form_frame, text="Category", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.cat_menu = ctk.CTkOptionMenu(form_frame, values=self.categories, fg_color="#F9FAFB", text_color="black", button_color="#E0E0E0", command=self.handle_category_change)
        self.cat_menu.pack(fill="x", padx=20, pady=(5, 10))

        # Dynamic Supplier Menu
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

        # ACTION GUARDS & UNIFORM LAYOUT
        btn_row_1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_row_1.pack(fill="x", padx=20, pady=(10, 5))
        btn_row_1.grid_columnconfigure((0, 1), weight=1)

        # Uniform width, expanding equally
        # Remove Update/Archive/Clear from here. Only keep Add and Clear Form.
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
        
        # Updated Filters matching requirements
        self.filter_menu = ctk.CTkOptionMenu(search_frame, values=["By: Name", "By: PID", "By: Category", "By: Date Acquired", "By: Date Last Checked"], width=160, fg_color="#F9FAFB", text_color="black")
        self.filter_menu.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search inventory...", width=250)
        self.search_entry.pack(side="left")
        # Bind the Enter key for rapid barcode scanning
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.search_btn = ctk.CTkButton(search_frame, text="Q", width=40, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 14, "bold"), command=self.perform_search)
        self.search_btn.pack(side="left", padx=10)

        header_frame = ctk.CTkFrame(table_frame, fg_color="#1E4528", corner_radius=5, height=40)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)

        headers = ["PID", "Category", "Supplier", "Name", "Price", "Qty", "Status"]
        weights = [1, 2, 2, 3, 1, 1, 1]

        for col, (text, weight) in enumerate(zip(headers, weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        dummy_data = [
            ("001", "Tools", "ACME", "3/8 Drill Bit", "120.00", "30", "Active"),
            ("002", "Measuring", "Priya", "Caliper 150mm", "850.00", "12", "Active"),
            ("003", "Tools", "Priya", "Hammer 1kg", "200.00", "6", "Inactive")
        ]

        for i, row_data in enumerate(dummy_data):
            row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)
            row_frame.bind("<Button-1>", lambda e, data=row_data: self.open_tool_modal(data))

            for col, (text, weight) in enumerate(zip(row_data, weights)):
                row_frame.grid_columnconfigure(col, weight=weight)
                lbl = ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color="#1A1A1A")
                lbl.grid(row=0, column=col, padx=10, pady=10, sticky="w")
                # Bind the label inside the row as well
                lbl.bind("<Button-1>", lambda e, data=row_data: self.open_tool_modal(data))

    def open_tool_modal(self, data):
        modal = ctk.CTkToplevel(self)
        modal.title(f"Manage Tool: {data[0]}")
        modal.geometry("450x500")
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()
        
        # Center Modal
        modal.update_idletasks()
        x = int((modal.winfo_screenwidth() / 2) - (450 / 2))
        y = int((modal.winfo_screenheight() / 2) - (500 / 2))
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"Product Details: {data[3]}", font=("Inter", 16, "bold"), text_color="black").pack(pady=20)
        
        # Form fields pre-filled with `data` go here
        
        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btn_row, text="Update", fg_color="#F1C40F", text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Archive", fg_color="#D3B8A7", text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Close", fg_color="#E0E0E0", text_color="black", command=modal.destroy).pack(side="right", padx=5)

    # Dynamic Interceptors
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
   
    def perform_search(self):
        query = self.search_entry.get().strip()
        filter_type = self.filter_menu.get()
        # In a full DB implementation, this would trigger:
        # SELECT * FROM Inventory WHERE {mapped_filter} LIKE '%{query}%'
        messagebox.showinfo("Search Triggered", f"Executing database query...\nSearching for: '{query}'\nFilter applied: '{filter_type}'")
        
    def confirm_action(self, action):
        if messagebox.askyesno(f"Confirm {action}", f"Are you sure you want to {action.lower()} this tool record?"):
            messagebox.showinfo("Success", f"Tool {action.lower()} operation completed successfully.")
    
    def validate_and_save(self):
        name = self.name_entry.get().strip()
        loc = self.loc_entry.get().strip()
        
        if not name:
            messagebox.showerror("Validation Error", "Product Name cannot be empty.", parent=self.winfo_toplevel())
            return

        # Force correct data types
        try:
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Type Error", "Price must be a valid number (e.g., 120.50).", parent=self.winfo_toplevel())
            return
            
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Type Error", "Quantity must be a whole number.", parent=self.winfo_toplevel())
            return

        messagebox.showinfo("Success", f"Tool added successfully.\nPrice: {price} | Qty: {qty} | Loc: {loc}", parent=self.winfo_toplevel())

    def clear_form(self):
        """Clears all input fields in the Add Tool form."""
        self.cat_menu.set("Select category")
        self.sup_menu.set("Select supplier")
        self.name_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.qty_entry.delete(0, 'end')
        self.loc_entry.delete(0, 'end')
        self.status_menu.set("Active")            