import customtkinter as ctk
from tkinter import messagebox
import qrcode
from PIL import Image
from database import get_connection
import cv2
from pyzbar.pyzbar import decode

class TaggingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_conn = get_connection() # GETS ITS OWN CONNECTION SAFELY

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.build_left_form()
        self.build_right_table()

    def build_left_form(self):
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")

        ctk.CTkLabel(form_frame, text="Tag Assignment", font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 15))

        # Product Selection
        ctk.CTkLabel(form_frame, text="Product", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.prod_menu = ctk.CTkOptionMenu(form_frame, values=["Select product", "3/8 Drill Bit", "Hammer 1kg", "Caliper 150mm"], fg_color="#F9FAFB", text_color="black")
        self.prod_menu.pack(fill="x", padx=20, pady=(5, 5))
        ctk.CTkLabel(form_frame, text="Select the product to assign a tag", font=("Inter", 10), text_color="gray").pack(anchor="w", padx=20, pady=(0, 15))

        # Tag ID (Scanner Ready)
        ctk.CTkLabel(form_frame, text="Tag ID", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        
        tag_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        tag_row.pack(fill="x", padx=20, pady=(5, 15))
        
        self.tag_entry = ctk.CTkEntry(tag_row, placeholder_text="Scan or enter manually", width=160)
        self.tag_entry.pack(side="left", expand=True, fill="x")
        self.tag_entry.bind("<Return>", self.process_scan)

        # Generate QR Button
        ctk.CTkButton(tag_row, text="QR", width=40, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 12, "bold"), command=self.generate_qr).pack(side="left", padx=(5, 0))
        
        # --- NEW: WEBCAM BUTTON ---
        ctk.CTkButton(tag_row, text="📷", width=40, fg_color="#3498DB", text_color="white", hover_color="#2980B9", font=("Inter", 14), command=self.launch_webcam_scanner).pack(side="left", padx=(5, 0))

        # Condition & Status
        ctk.CTkLabel(form_frame, text="Condition", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.cond_menu = ctk.CTkOptionMenu(form_frame, values=["Good", "Needs Repair", "Damaged"], fg_color="#F9FAFB", text_color="black")
        self.cond_menu.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(form_frame, text="Status", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20)
        self.status_menu = ctk.CTkOptionMenu(form_frame, values=["Active", "Inactive"], fg_color="#F9FAFB", text_color="black")
        self.status_menu.pack(fill="x", padx=20, pady=(5, 20))

        # Action Guards & Buttons
        btn_row_1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_row_1.pack(fill="x", padx=20, pady=(10, 5))
        btn_row_1.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row_1, text="Assign Tag", fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Assign Tag")).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(btn_row_1, text="Update", fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Update Tag")).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        btn_row_2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_row_2.pack(fill="x", padx=20, pady=5)
        btn_row_2.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row_2, text="Archive", fg_color="#D3B8A7", text_color="black", hover_color="#BFA595", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Archive Tag")).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(btn_row_2, text="Clear", fg_color="white", text_color="black", border_width=1, border_color="#E0E0E0", hover_color="#F0F0F0", font=("Inter", 12, "bold"), command=lambda: self.confirm_action("Clear Fields")).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Preview QR Code Button
        ctk.CTkButton(form_frame, text="⎙ Preview QR Code", fg_color="transparent", text_color="#1A1A1A", border_width=1, border_color="#E0E0E0", font=("Inter", 12), command=self.preview_qr).pack(fill="x", padx=20, pady=20)

    def build_right_table(self):
        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        ctk.CTkLabel(table_frame, text="Tag List", font=("Inter", 16, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=20, pady=(20, 5))

        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkEntry(search_frame, placeholder_text="Search Tag ID or Tool Name", width=200).pack(side="left", padx=(0, 10))
        ctk.CTkOptionMenu(search_frame, values=["All Status", "Assigned", "Unassigned"], width=120, fg_color="#F9FAFB", text_color="black").pack(side="left", padx=(0, 10))
        ctk.CTkButton(search_frame, text="Search", width=80, fg_color="#1E4528", font=("Inter", 12, "bold")).pack(side="left")

        # Table Layout
        header_frame = ctk.CTkFrame(table_frame, fg_color="#1E4528", corner_radius=5, height=40)
        header_frame.pack(fill="x", padx=20)
        header_frame.pack_propagate(False)

        headers = ["Tag ID", "Product Name", "Status", "Condition", "Last Borrow"]
        weights = [1, 2, 1, 1, 1]

        for col, (text, weight) in enumerate(zip(headers, weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        dummy_data = [
            ("TAG-101", "3/8 Drill Bit", "Assigned", "Good", "J. Santos"),
            ("TAG-102", "Hammer 1kg", "Assigned", "Good", "M. Cruz"),
            ("TAG-103", "Unassigned", "Unassigned", "Good", "-")
        ]

        for i, row_data in enumerate(dummy_data):
            row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)
            for col, (text, weight) in enumerate(zip(row_data, weights)):
                row_frame.grid_columnconfigure(col, weight=weight)
                ctk.CTkLabel(row_frame, text=text, font=("Inter", 11), text_color="#1A1A1A").grid(row=0, column=col, padx=10, pady=10, sticky="w")

    # --- TAGGING LOGIC ---
    def process_scan(self, event=None):
        scanned_id = self.tag_entry.get().strip()
        if scanned_id:
            messagebox.showinfo("Hardware Scan Detected", f"Barcode/QR Scanner read: {scanned_id}\nQuerying database for tag details...")

    def generate_qr(self):
        # Auto-generates a unique Tag ID if the field is empty
        import uuid
        new_id = f"TAG-{str(uuid.uuid4())[:4].upper()}"
        self.tag_entry.delete(0, 'end')
        self.tag_entry.insert(0, new_id)

    def confirm_action(self, action):
        if messagebox.askyesno(f"Confirm {action}", f"Are you sure you want to proceed with: {action}?"):
            messagebox.showinfo("Success", f"{action} completed successfully.")

    def preview_qr(self):
        tag_id = self.tag_entry.get().strip()
        product = self.prod_menu.get()

        if not tag_id:
            tag_id = "Not assigned"
        if product == "Select product":
            product = "None"

        # Generate actual QR Code image in memory
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(tag_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1E4528", back_color="white") # Branded Green QR Code

        # The Exact Modal Replica
        dialog = ctk.CTkToplevel(self)
        dialog.title("QR CODE PREVIEW")
        dialog.geometry("400x500")
        
        # Center the dialog
        dialog.update_idletasks()
        x = int((dialog.winfo_screenwidth() / 2) - (400 / 2))
        y = int((dialog.winfo_screenheight() / 2) - (500 / 2))
        dialog.geometry(f"+{x}+{y}")
        
        dialog.configure(fg_color="white")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="QR CODE PREVIEW", font=("Inter", 14, "bold"), text_color="#1A1A1A").pack(anchor="w", padx=30, pady=(20, 20))

        qr_ctk_img = ctk.CTkImage(light_image=img, size=(200, 200))
        img_label = ctk.CTkLabel(dialog, image=qr_ctk_img, text="", bg_color="white")
        img_label.pack(pady=10)

        ctk.CTkLabel(dialog, text=f"Tag ID: {tag_id}", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(pady=(10, 5))
        ctk.CTkLabel(dialog, text=f"Product: {product}", font=("Inter", 12), text_color="gray").pack(pady=(0, 20))

        ctk.CTkButton(dialog, text="⎙ Print QR Code", fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 12, "bold"), command=lambda: messagebox.showinfo("Print Spooler", "Sending payload to LAN thermal printer...")).pack(pady=10)
        
        ctk.CTkButton(dialog, text="Cancel", fg_color="white", text_color="black", border_width=1, border_color="#E0E0E0", width=80, command=dialog.destroy).pack(side="bottom", anchor="e", padx=30, pady=20)
    
    # --- WEBCAM SCANNER LOGIC ---
    def launch_webcam_scanner(self):
        # Opens the default camera (0)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "No webcam detected on this system.", parent=self.winfo_toplevel())
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Decode any barcodes or QR codes in the current frame
            detected_codes = decode(frame)
            
            for barcode in detected_codes:
                # Extract the text
                barcode_data = barcode.data.decode('utf-8')
                
                # Draw a green rectangle around it for visual feedback
                pts = barcode.polygon
                if len(pts) == 4:
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

                # Update the Tkinter entry box directly
                self.tag_entry.delete(0, 'end')
                self.tag_entry.insert(0, barcode_data)
                
                # Clean up and close
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("Scan Successful", f"Decoded: {barcode_data}", parent=self.winfo_toplevel())
                
                # Auto-trigger the search/process feature just like the hardware scanner
                self.process_scan()
                return 

            # Show the live feed window
            cv2.imshow('Champion Tooling - Camera Scanner (Press Q to quit)', frame)

            # Allow user to quit manually by pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()