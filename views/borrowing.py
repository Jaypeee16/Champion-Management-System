import customtkinter as ctk
from tkinter import messagebox
from database import get_connection

class BorrowingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_conn = get_connection()

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_search_section()
        self.build_forms_section()
        self.build_history_table()

    def build_search_section(self):
        search_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        search_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(search_card, text="Search Transactions", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(15, 5))
        
        controls = ctk.CTkFrame(search_card, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(0, 15))

        # Replicating the top search bar filters from Figma
        self.trans_search = ctk.CTkEntry(controls, placeholder_text="Tag ID / Borrower / Trans ID", width=250)
        self.trans_search.pack(side="left", padx=(0, 10))
        self.trans_search.bind("<Return>", lambda e: self.confirm_action("Search"))

        ctk.CTkOptionMenu(controls, values=["All Status", "Borrowed", "Returned", "Overdue"], width=120, fg_color="#F9FAFB", text_color="black").pack(side="left", padx=(0, 10))
        
        ctk.CTkEntry(controls, placeholder_text="mm/dd/yyyy (Start)", width=120).pack(side="left", padx=(0, 10))
        ctk.CTkEntry(controls, placeholder_text="mm/dd/yyyy (End)", width=120).pack(side="left", padx=(0, 10))

        ctk.CTkButton(controls, text="Search", width=80, fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Search")).pack(side="left", padx=(0, 5))
        ctk.CTkButton(controls, text="Clear", width=60, fg_color="transparent", text_color="black", hover_color="#E0E0E0", command=lambda: self.trans_search.delete(0, 'end')).pack(side="left")

    def build_forms_section(self):
        forms_container = ctk.CTkFrame(self, fg_color="transparent")
        forms_container.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        forms_container.grid_columnconfigure(0, weight=1)
        forms_container.grid_columnconfigure(1, weight=1)

        # LEFT: Borrower Information
        borrower_card = ctk.CTkFrame(forms_container, fg_color="white", corner_radius=10)
        borrower_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(borrower_card, text="Borrower Information", font=("Inter", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(borrower_card, text="Employee ID", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.emp_id = ctk.CTkEntry(borrower_card, placeholder_text="Scan or enter manually")
        self.emp_id.pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(borrower_card, text="Name", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        ctk.CTkEntry(borrower_card, placeholder_text="Auto-fill", state="disabled", fg_color="#F9FAFB").pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(borrower_card, text="Department", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        ctk.CTkEntry(borrower_card, placeholder_text="Auto-fill", state="disabled", fg_color="#F9FAFB").pack(fill="x", padx=20, pady=(5, 15))

        # RIGHT: Tool Information
        tool_card = ctk.CTkFrame(forms_container, fg_color="white", corner_radius=10)
        tool_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(tool_card, text="Tool Information", font=("Inter", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(tool_card, text="Tool Tag ID", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        scan_row = ctk.CTkFrame(tool_card, fg_color="transparent")
        scan_row.pack(fill="x", padx=20, pady=(5, 10))
        self.tool_id = ctk.CTkEntry(scan_row, placeholder_text="Scan QR code")
        self.tool_id.pack(side="left", expand=True, fill="x")
        ctk.CTkButton(scan_row, text="QR", width=40, fg_color="#F1C40F", text_color="black").pack(side="left", padx=(5, 0))

        ctk.CTkLabel(tool_card, text="Tool Name", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        ctk.CTkEntry(tool_card, placeholder_text="Auto-fill", state="disabled", fg_color="#F9FAFB").pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(tool_card, text="Condition", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(tool_card, values=["Good", "Needs Repair", "Damaged"], fg_color="#F9FAFB", text_color="black").pack(fill="x", padx=20, pady=(5, 10))

        ctk.CTkLabel(tool_card, text="Expected Return Date", font=("Inter", 11, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        ctk.CTkEntry(tool_card, placeholder_text="mm/dd/yyyy").pack(fill="x", padx=20, pady=(5, 15))

        # ACTION BUTTONS
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkButton(btn_container, text="Borrow", fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Borrow Tool")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_container, text="Return", fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Return Tool")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_container, text="Cancel", fg_color="white", text_color="black", hover_color="#E0E0E0", command=lambda: self.confirm_action("Cancel Transaction")).pack(side="left")

    def build_history_table(self):
        history_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        history_card.grid(row=3, column=0, sticky="nsew")
        
        ctk.CTkLabel(history_card, text="Transaction History", font=("Inter", 12, "bold"), text_color="gray").pack(anchor="w", padx=20, pady=(15, 5))

        header_frame = ctk.CTkFrame(history_card, fg_color="#1E4528", corner_radius=5, height=35)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)

        headers = ["Trans ID", "Tool Tag", "Tool Name", "Borrower", "Borrow Date", "Return Date", "Status"]
        weights = [1, 1, 2, 2, 1, 1, 1]

        for col, (text, weight) in enumerate(zip(headers, weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 11, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=5, sticky="w")

        data_scroll = ctk.CTkScrollableFrame(history_card, fg_color="transparent")
        data_scroll.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        dummy_data = [
            ("T001", "TAG-101", "3/8 Drill Bit", "J. Santos", "2026-05-10", "2026-05-14", "Returned"),
            ("T002", "TAG-102", "Hammer 1kg", "M. Cruz", "2026-05-12", "-", "Borrowed")
        ]

        for i, row_data in enumerate(dummy_data):
            row_frame = ctk.CTkFrame(data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=35)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)
            for col, (text, weight) in enumerate(zip(row_data, weights)):
                row_frame.grid_columnconfigure(col, weight=weight)
                ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color="#1A1A1A").grid(row=0, column=col, padx=10, pady=5, sticky="w")

    def confirm_action(self, action):
        # Using parent=self ensures the messagebox pops up dead-center over the app!
        if messagebox.askyesno(f"Confirm {action}", f"Are you sure you want to execute: {action}?", parent=self):
            messagebox.showinfo("Success", f"{action} processed and logged successfully.", parent=self)