import customtkinter as ctk
from tkinter import messagebox
import qrcode
from PIL import Image
from database import get_connection
import cv2
from pyzbar.pyzbar import decode
import os         # ADD THIS
import tempfile   # ADD THIS

class TaggingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_main_panel()
        self.load_tagging_data()

    def build_main_panel(self):
        main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        main_frame.grid(row=0, column=0, padx=10, pady=0, sticky="nsew")

        # Header
        header_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_row, text="Tag Management Hub", font=("Inter", 20, "bold"), text_color="#1A1A1A").pack(side="left")
        ctk.CTkLabel(header_row, text="Click a tool to assign a tag, or use the scanner to test existing tags.", font=("Inter", 12), text_color="gray").pack(side="left", padx=15, pady=(5,0))

        # Search & Scan Bar
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search Tool Name or Tag ID...", width=300)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        self.filter_menu = ctk.CTkOptionMenu(search_frame, values=["All Tools", "Needs Tag", "Already Tagged"], width=140, fg_color="#F9FAFB", text_color="black")
        self.filter_menu.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", width=80, fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=self.perform_search).pack(side="left")
        ctk.CTkButton(search_frame, text="↻ Reset", width=70, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", font=("Inter", 12, "bold"), command=self.reset_search).pack(side="left", padx=10)

        # NEW INDEPENDENT SCANNER BUTTON
        self.scan_test_btn = ctk.CTkButton(search_frame, text="📷 Scan & Test QR", width=140, fg_color="#3498DB", hover_color="#2980B9", font=("Inter", 12, "bold"), command=self.open_test_scanner)
        self.scan_test_btn.pack(side="right", padx=10)

        # Table Header
        table_header = ctk.CTkFrame(main_frame, fg_color="#1E4528", corner_radius=5, height=40)
        table_header.pack(fill="x", padx=20)
        table_header.pack_propagate(False)

        self.headers = ["Tool ID", "Product Name", "Category", "Supplier", "Assigned Tag ID"]
        self.weights = [1, 3, 2, 2, 2]

        for col, (text, weight) in enumerate(zip(self.headers, self.weights)):
            table_header.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(table_header, text=text, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        # Scrollable Data Area
        self.data_scroll = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        self.data_scroll.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    # --- DATABASE METHODS ---

    def load_tagging_data(self, query="", filter_type="All Tools"):
        for widget in self.data_scroll.winfo_children():
            widget.destroy()

        conn = get_connection()
        if not conn: return

        try:
            cursor = conn.cursor()
            
            base_query = "SELECT tool_id, name, category, supplier, IFNULL(tag_id, 'Unassigned') FROM tool WHERE is_archived = 0"
            params = []

            if filter_type == "Needs Tag":
                base_query += " AND (tag_id IS NULL OR tag_id = '')"
            elif filter_type == "Already Tagged":
                base_query += " AND tag_id IS NOT NULL AND tag_id != ''"

            if query:
                base_query += " AND (name LIKE %s OR tag_id LIKE %s)"
                params.extend([f"%{query}%", f"%{query}%"])

            cursor.execute(base_query, tuple(params))
            results = cursor.fetchall()

            if not results:
                ctk.CTkLabel(self.data_scroll, text="No tools found matching the criteria.", text_color="gray").pack(pady=20)
                return

            for i, row_data in enumerate(results):
                display_data = [str(item) for item in row_data] 
                
                row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=40)
                row_frame.pack(fill="x", pady=2)
                row_frame.pack_propagate(False)
                row_frame.bind("<Button-1>", lambda e, data=display_data: self.open_tag_manager(data))

                for col, (text, weight) in enumerate(zip(display_data, self.weights)):
                    row_frame.grid_columnconfigure(col, weight=weight)
                    
                    txt_color = "#D8000C" if col == 4 and text == "Unassigned" else "#1A1A1A"
                    font_weight = "bold" if col == 4 and text != "Unassigned" else "normal"
                    
                    lbl = ctk.CTkLabel(row_frame, text=text, font=("Inter", 11, font_weight), text_color=txt_color)
                    lbl.grid(row=0, column=col, padx=10, pady=10, sticky="w")
                    lbl.bind("<Button-1>", lambda e, data=display_data: self.open_tag_manager(data))

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load tags: {e}", parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def perform_search(self):
        query = self.search_entry.get().strip()
        filter_type = self.filter_menu.get()
        self.load_tagging_data(query, filter_type)
        
    def reset_search(self):
        self.search_entry.delete(0, 'end')
        self.filter_menu.set("All Tools")
        self.load_tagging_data()


    # --- INDEPENDENT TEST SCANNER LOGIC ---

    def open_test_scanner(self):
        """Opens the webcam specifically to read a QR code and fetch DB details."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "No webcam detected.", parent=self.winfo_toplevel())
            return

        messagebox.showinfo("Scanner Activated", "Point a printed Tag/QR Code at the camera.\nPress 'Q' to cancel.", parent=self.winfo_toplevel())
        
        detected_tag = None
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            detected_codes = decode(frame)
            for barcode in detected_codes:
                detected_tag = barcode.data.decode('utf-8')
                break 
                
            cv2.imshow('Champion Tooling - Test Scanner', frame)
            
            # Close window if tag is found OR user presses 'q'
            if detected_tag or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
        # If we caught a tag, look it up in the database!
        if detected_tag:
            self.fetch_and_display_scanned_tool(detected_tag)

    def fetch_and_display_scanned_tool(self, tag_id):
        """Queries the live database using the scanned license plate (tag_id)"""
        conn = get_connection()
        if not conn: return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT t.name, t.category, t.supplier, t.condition, t.location, IFNULL(i.quantity_available, 0)
                FROM tool t
                LEFT JOIN inventory i ON t.tool_id = i.tool_id
                WHERE t.tag_id = %s
            """
            cursor.execute(query, (tag_id,))
            result = cursor.fetchone()
            
            if result:
                # Format a beautiful read-out of the live data
                info = (
                    f"✓ Tag Recognized: {tag_id}\n"
                    f"{'-'*40}\n"
                    f"Product Name:   {result[0]}\n"
                    f"Category:       {result[1]}\n"
                    f"Supplier:       {result[2]}\n"
                    f"Condition:      {result[3]}\n"
                    f"Storage Loc:    {result[4]}\n"
                    f"Qty Available:  {result[5]}\n"
                )
                messagebox.showinfo("Tool Successfully Identified", info, parent=self.winfo_toplevel())
            else:
                messagebox.showwarning("Unknown Tag", f"The tag '{tag_id}' was scanned, but it is not linked to any active tool in the database.", parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self.winfo_toplevel())
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()


    # --- TAG MANAGER MODAL (ASSIGNMENT) ---

    # --- TAG MANAGER MODAL (ASSIGNMENT) ---

    def open_tag_manager(self, data):
        tool_id = data[0]
        tool_name = data[1]
        tool_category = data[2]
        tool_supplier = data[3]
        current_tag = "" if data[4] == "Unassigned" else data[4]

        modal = ctk.CTkToplevel(self)
        modal.title(f"Tag Manager: {tool_name}")
        modal.geometry("450x550")
        modal.configure(fg_color="white")
        modal.attributes("-topmost", True)
        modal.grab_set()
        
        modal.update_idletasks()
        x = int((modal.winfo_screenwidth() / 2) - (450 / 2))
        y = int((modal.winfo_screenheight() / 2) - (550 / 2))
        modal.geometry(f"+{x}+{y}")

        ctk.CTkLabel(modal, text=f"Manage Tag: {tool_name}", font=("Inter", 16, "bold"), text_color="black").pack(pady=(20, 5))
        ctk.CTkLabel(modal, text=f"System ID: {tool_id}", font=("Inter", 12), text_color="gray").pack(pady=(0, 20))

        form_frame = ctk.CTkFrame(modal, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30)

        ctk.CTkLabel(form_frame, text="Assigned Tag ID / Barcode", font=("Inter", 12, "bold"), text_color="#1A1A1A").pack(anchor="w")
        
        tag_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        tag_row.pack(fill="x", pady=(5, 10))
        
        tag_entry = ctk.CTkEntry(tag_row, placeholder_text="Scan or enter Tag ID", height=35)
        tag_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))
        if current_tag:
            tag_entry.insert(0, current_tag)

        # 1. THE TRIGGER FIX: Explicitly call update_preview() here!
        def generate_smart_tag():
            tag_entry.delete(0, 'end')
            
            cat_prefix = str(tool_category)[:3].upper() if tool_category and tool_category != "None" else "GEN"
            sup_prefix = str(tool_supplier)[:3].upper() if tool_supplier and tool_supplier != "None" else "UNK"
            
            smart_tag = f"TAG-{str(tool_id).zfill(3)}-{cat_prefix}-{sup_prefix}"
            tag_entry.insert(0, smart_tag)
            update_preview() # Wakes up the preview immediately after auto-generating!

        ctk.CTkButton(tag_row, text="↻ Auto-Gen", width=80, height=35, fg_color="#F1C40F", text_color="black", hover_color="#D4AC0D", font=("Inter", 11, "bold"), command=generate_smart_tag).pack(side="left", padx=(0, 5))

        # --- SAVE LOGIC ---
        def save_tag():
            new_tag = tag_entry.get().strip()
            if not new_tag:
                messagebox.showerror("Error", "Tag ID cannot be empty.", parent=modal)
                return
                
            conn = get_connection()
            if not conn: return
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT tool_id FROM tool WHERE tag_id = %s AND tool_id != %s", (new_tag, tool_id))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Tag", f"The Tag ID '{new_tag}' is already assigned to another tool!", parent=modal)
                    return

                cursor.execute("UPDATE tool SET tag_id = %s WHERE tool_id = %s", (new_tag, tool_id))
                conn.commit()
                messagebox.showinfo("Success", "Tag successfully linked to tool.", parent=modal)
                self.load_tagging_data()
            except Exception as e:
                messagebox.showerror("Database Error", str(e), parent=modal)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        def clear_tag():
            if messagebox.askyesno("Remove Tag", "Are you sure you want to unlink the tag from this tool?", parent=modal):
                conn = get_connection()
                if not conn: return
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tool SET tag_id = NULL WHERE tool_id = %s", (tool_id,))
                    conn.commit()
                    tag_entry.delete(0, 'end')
                    update_preview() # Clear the preview when unlinked!
                    self.load_tagging_data()
                    messagebox.showinfo("Success", "Tag removed.", parent=modal)
                except Exception as e:
                    pass
                finally:
                    if conn.is_connected(): cursor.close(); conn.close()

        ctk.CTkButton(form_frame, text="Save Tag Link to Database", height=40, fg_color="#1E4528", hover_color="#14301C", font=("Inter", 12, "bold"), command=save_tag).pack(fill="x", pady=(15, 5))
        
        if current_tag:
            ctk.CTkButton(form_frame, text="Unlink Current Tag", height=30, fg_color="white", border_width=1, border_color="#D8000C", text_color="#D8000C", hover_color="#FFD2D2", font=("Inter", 11, "bold"), command=clear_tag).pack(fill="x", pady=5)

        preview_frame = ctk.CTkFrame(form_frame, fg_color="#F9FAFB", corner_radius=10)
        preview_frame.pack(fill="both", expand=True, pady=(20, 0))

        # 2. THE IMAGE STABILITY FIX
        def update_preview():
            # Clear old preview widgets first
            for widget in preview_frame.winfo_children():
                widget.destroy()
                
            current_val = tag_entry.get().strip()
            if not current_val: return # If empty, leave the box blank
            
            # Draw the UI Preview safely with RGB conversion
            qr = qrcode.QRCode(version=1, box_size=5, border=1)
            qr.add_data(current_val)
            qr.make(fit=True)
            img_preview = qr.make_image(fill_color="#1E4528", back_color="#F9FAFB").convert("RGB")
            
            # Attach the image to the frame so Python's Garbage Collector doesn't eat it!
            preview_frame.qr_ctk_img = ctk.CTkImage(light_image=img_preview, size=(120, 120))
                
            ctk.CTkLabel(preview_frame, text="Live QR Preview", font=("Inter", 11, "bold"), text_color="gray").pack(pady=(10, 5))
            ctk.CTkLabel(preview_frame, image=preview_frame.qr_ctk_img, text="").pack(pady=5)
            
            # The Real Print Function
            # The Real Print Function
            # The Real Print Function
            def execute_print():
                try:
                    # 1. Drop the modal shield
                    modal.attributes("-topmost", False)

                    # 2. Make the QR code natively larger (box_size=20)
                    print_qr = qrcode.QRCode(version=1, box_size=20, border=2)
                    print_qr.add_data(current_val)
                    print_qr.make(fit=True)
                    qr_img = print_qr.make_image(fill_color="black", back_color="white").convert("RGB")
                    
                    # 3. Create a standard "Printable Canvas" (1200x1200px) so Windows doesn't panic when stretching it to A4
                    from PIL import Image as PILImage
                    canvas = PILImage.new('RGB', (1200, 1200), 'white')
                    
                    # Mathematically center the QR code on the blank canvas
                    offset_x = (canvas.width - qr_img.width) // 2
                    offset_y = (canvas.height - qr_img.height) // 2
                    canvas.paste(qr_img, (offset_x, offset_y))
                    
                    import tempfile, os, time
                    temp_dir = tempfile.gettempdir()
                    file_path = os.path.join(temp_dir, f"{current_val}.png")
                    
                    # Save the new properly scaled canvas
                    canvas.save(file_path, format="PNG")
                    
                    # 4. Give the hard drive a split second to finish saving and unlock the file
                    time.sleep(0.3)
                    
                    # 5. Trigger the Print window
                    os.startfile(file_path, "print")
                    
                except Exception as e:
                    messagebox.showerror("Print Error", f"Could not communicate with Windows.\nError: {e}", parent=modal)
                    modal.attributes("-topmost", True) # Put the shield back up if it fails

            ctk.CTkButton(preview_frame, text="⎙ Print Label", width=100, height=28, fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", font=("Inter", 11), command=execute_print).pack(pady=(5, 10))

        tag_entry.bind("<KeyRelease>", lambda e: update_preview())
        update_preview() 

        ctk.CTkButton(modal, text="Close", fg_color="#E0E0E0", text_color="black", hover_color="#CCCCCC", command=modal.destroy).pack(side="bottom", pady=20, padx=30, fill="x")
