import customtkinter as ctk
from database import get_connection

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        
        ctk.CTkLabel(self, text="Inventory Analytics (ABC Analysis)", font=("Inter", 20, "bold"), text_color="#1E4528").pack(anchor="w", padx=30, pady=(30, 5))
        ctk.CTkLabel(self, text="Algorithm dynamically categorizes tools based on the Pareto Principle (80/20 usage).", font=("Inter", 12), text_color="gray").pack(anchor="w", padx=30, pady=(0, 20))

        header_frame = ctk.CTkFrame(self, fg_color="#1E4528", corner_radius=5, height=40)
        header_frame.pack(fill="x", padx=30)
        header_frame.pack_propagate(False)

        headers = ["Rank", "Tool ID", "Tool Name", "Times Borrowed", "Cumulative %", "ABC Category"]
        weights = [1, 1, 3, 2, 2, 2]

        for col, (text, weight) in enumerate(zip(headers, weights)):
            header_frame.grid_columnconfigure(col, weight=weight)
            ctk.CTkLabel(header_frame, text=text, font=("Inter", 12, "bold"), text_color="white").grid(row=0, column=col, padx=10, pady=10, sticky="w")

        self.data_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.data_scroll.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        self.run_abc_algorithm()

    def run_abc_algorithm(self):
        """ALGORITHM 3: Implements Figure 96 (ABC Inventory Categorization)"""
        conn = get_connection()
        if not conn: return
        
        try:
            cursor = conn.cursor(dictionary=True)
            # 1. Count all historical borrow transactions per tool
            cursor.execute("""
                SELECT t.tool_id, t.name, COUNT(tr.transaction_id) as usage_count
                FROM tool t
                LEFT JOIN transaction tr ON t.tool_id = tr.tool_id AND tr.type = 'Borrow'
                WHERE t.is_archived = 0
                GROUP BY t.tool_id, t.name
                ORDER BY usage_count DESC
            """)
            tools = cursor.fetchall()
            
            # 2. Mathematical Logic for Pareto Sorting
            total_usage = sum(t['usage_count'] for t in tools)
            if total_usage == 0: total_usage = 1 # Prevent division by zero
            
            cumulative = 0
            
            for i, tool in enumerate(tools):
                # Calculate cumulative percentage
                cumulative += tool['usage_count']
                cum_pct = (cumulative / total_usage) * 100
                
                # Assign Categories based on Figure 96 logic
                if cum_pct <= 70:
                    category = "A (High Priority - Top 20%)"
                    color = "#2ECC71"
                elif cum_pct <= 90:
                    category = "B (Medium Priority - Next 30%)"
                    color = "#F1C40F"
                else:
                    category = "C (Low Priority - Bottom 50%)"
                    color = "#E74C3C"
                    
                display_data = [f"#{i+1}", str(tool['tool_id']), tool['name'], str(tool['usage_count']), f"{cum_pct:.1f}%", category]
                
                row_frame = ctk.CTkFrame(self.data_scroll, fg_color="#F9FAFB" if i % 2 == 0 else "white", height=35)
                row_frame.pack(fill="x", pady=2)
                row_frame.pack_propagate(False)
                
                for col, (text, weight) in enumerate(zip(display_data, [1, 1, 3, 2, 2, 2])):
                    row_frame.grid_columnconfigure(col, weight=weight)
                    txt_col = color if col == 5 else "black"
                    ctk.CTkLabel(row_frame, text=text, font=("Inter", 11, "bold" if col==5 else "normal"), text_color=txt_col).grid(row=0, column=col, padx=10, pady=5, sticky="w")
                    
        except Exception as e: print(e)
        finally:
            if conn.is_connected(): cursor.close(); conn.close()
    
    def generate_abc_analysis():
      """Applies the 80/20 Pareto principle to categorize inventory by usage."""
      conn = get_connection()
      cursor = conn.cursor(dictionary=True)
      
      # Get usage frequency for all tools
      cursor.execute("""
          SELECT t.name, COUNT(tr.transaction_id) as usage_count 
          FROM tool t LEFT JOIN transaction tr ON t.tool_id = tr.tool_id
          GROUP BY t.tool_id ORDER BY usage_count DESC
      """)
      tools = cursor.fetchall()
      total_tools = len(tools)
      
      # Assign ABC based on Top 20% (A), Next 30% (B), Bottom 50% (C)
      for index, tool in enumerate(tools):
          percentile = (index + 1) / total_tools
          if percentile <= 0.20:
              category = "A (High Usage - Strict Audit)"
          elif percentile <= 0.50:
              category = "B (Medium Usage - Standard Audit)"
          else:
              category = "C (Low Usage - Minimal Reorder)"
          print(f"{tool['name']} -> {category}")