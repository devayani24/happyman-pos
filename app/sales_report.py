from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from app.config import REPORT_DIR, SHOP_ID
from datetime import datetime
from app.db.database import get_sales_data, get_sale_items_data,get_top_products, get_metrics


def build_sales_list_sheet(wb, timestamp):
  

  # Query database
  sales = get_sales_data()

  # Define headers - user-friendly
  headers = [
        "Bill #", "Date", "Time", "Total", "Payment Mode",
        "Items", "Type(Sale/Refund)", "Refund For(Bill #)", "Voided"
    ] 
  
   # Layout constants — self-documenting
  TITLE_ROW = 1
  HEADER_ROW = 3
  DATA_START_ROW = 4

  # Build workbook
  # wb = Workbook()
  # ws = wb.active
  ws = wb.create_sheet("Sales List")

  # Title (row 1)
  last_col = get_column_letter(len(headers))
  ws.cell(row =TITLE_ROW, column = 1, value = f"Sales List — {timestamp}")
  ws.merge_cells(f"A{TITLE_ROW}:{last_col}{TITLE_ROW}")

  # Headers (row 3)
  for col_index, header in enumerate(headers, start = 1):
     ws.cell(row=HEADER_ROW, column=col_index, value=header)
  
  # Data rows
  if not sales:
    ws.cell(row=DATA_START_ROW, column=1, value="No sales recorded")
    
    return

  for row_offset, sale in enumerate(sales):
    row = DATA_START_ROW + row_offset
    
    ws.cell(row=row, column=1, value=sale['bill_number'])
    ws.cell(row=row, column=2, value=sale['timestamp'][:10])  # date
    ws.cell(row=row, column=3, value=sale['timestamp'][11:16])  # time
    ws.cell(row=row, column=4, value=sale['total_price'])
    ws.cell(row=row, column=5, value=sale['payment_mode'])
    ws.cell(row=row, column=6, value=sale['items_count'])
    ws.cell(row=row, column=7, value=sale['transaction_type'])
    ws.cell(row=row, column=8, value=sale['refund_for_bill'])
    ws.cell(row=row, column=9, value='Yes' if sale['is_void'] else 'No')

  # Totals row
  data_end_row = DATA_START_ROW + len(sales) - 1
  totals_row = data_end_row + 2

  # Label spanning columns 1-3
  ws.cell(row=totals_row, column=1, value="Net Total")
  ws.merge_cells(
      start_row=totals_row, start_column=1,
      end_row=totals_row, end_column=3
  )
  
  # SUMIF formula — uses Yes/No instead of 0/1 because we changed display
  void_col = "I"   # column 9 — "Voided" column
  total_col = "D"  # column 4 — "Total" column
  
  formula = (
      f'=SUMIF({void_col}{DATA_START_ROW}:{void_col}{data_end_row},"No",'
      f'{total_col}{DATA_START_ROW}:{total_col}{data_end_row})'
  )
  ws.cell(row=totals_row, column=4, value=formula)

def build_items_detail_sheet(wb, timestamp):

  # Query database
  sale_items = get_sale_items_data()

  # Define headers - user-friendly
  headers = [
        "Bill #", "is_void", "Product", "Local Name", "Quantity", "Unit", "Packets", "Line Total"
    ] 
  
   # Layout constants — self-documenting
  TITLE_ROW = 1
  HEADER_ROW = 3
  DATA_START_ROW = 4

  ws = wb.create_sheet("Items Detail")

  # Title (row 1)
  last_col = get_column_letter(len(headers))
  ws.cell(row =TITLE_ROW, column = 1, value = f"Items Detail — {timestamp}")
  ws.merge_cells(f"A{TITLE_ROW}:{last_col}{TITLE_ROW}")

  # Headers (row 3)
  for col_index, header in enumerate(headers, start = 1):
     ws.cell(row=HEADER_ROW, column=col_index, value=header)
  
  # Data rows
  if not sale_items:
    ws.cell(row=DATA_START_ROW, column=1, value="No sale items recorded")
    
    return
  
  for row_offset, sale_item in enumerate(sale_items):
    row = DATA_START_ROW + row_offset
    
    ws.cell(row=row, column=1, value=sale_item['bill_number'])
    ws.cell(row=row, column=2, value='Yes' if sale_item['is_void'] else 'No')
    ws.cell(row=row, column=3, value=sale_item['name']) 
    ws.cell(row=row, column=4, value=sale_item['local_name']) 
    ws.cell(row=row, column=5, value=sale_item['quantity'])
    ws.cell(row=row, column=6, value=sale_item['unit'])
    ws.cell(row=row, column=7, value=sale_item['packets'])
    ws.cell(row=row, column=8, value=sale_item['line_total'])

  # Totals row
  data_end_row = DATA_START_ROW + len(sale_items) - 1
  totals_row = data_end_row + 2

  # Label spanning columns 1-3
  ws.cell(row=totals_row, column=1, value="Grand Total")
  ws.merge_cells(
      start_row=totals_row, start_column=1,
      end_row=totals_row, end_column=7
  )
  
  # SUM formula
  total_col = "H"  # column 4 — "Total" column
  
  formula = (
      f"=SUM({total_col}{DATA_START_ROW}:{total_col}{data_end_row})")
  
  ws.cell(row=totals_row, column=8, value=formula)

def build_summary_sheet(wb, timestamp):
    ws = wb.create_sheet("Summary")
    
    # Layout constants
    TITLE_ROW = 1
    FIRST_BLOCK_ROW = 3
    ROWS_PER_BLOCK = 10   # 1 header + 7 metrics + 2 spacer
    
    # Define periods once
    periods = [
        ('TODAY', 'today'),
        ('YESTERDAY', 'yesterday'),
        ('LAST 7 DAYS', 'last_7_days'),
        ('LAST 30 DAYS', 'last_30_days'),
        ('THIS MONTH', 'this_month'),
        ('ALL TIME', 'all_time'),
    ]
    
    # Define metric display order and labels
    DISPLAY_ORDER = [
        ('total_revenue', 'Total Revenue'),
        ('sale_count', 'Sale Count'),
        ('avg_transaction', 'Avg Transaction'),
        ('cash_total', 'Cash Total'),
        ('gpay_total', 'GPay Total'),
        ('voided_count', 'Voided Count'),
        ('voided_amount', 'Voided Amount'),
    ]
    
    # Title
    ws.cell(row=TITLE_ROW, column=1, value=f"HappyMan Sweets — Summary — {timestamp}")
    ws.merge_cells(f"A{TITLE_ROW}:G{TITLE_ROW}")
    
    # Write each period block
    for block_index, (title, period) in enumerate(periods):
        # Position for this block
        block_start = FIRST_BLOCK_ROW + (block_index * ROWS_PER_BLOCK)
        header_row = block_start
        first_metric_row = block_start + 1
        
        # Block header
        ws.cell(row=header_row, column=1, value=title)
        ws.merge_cells(f"A{header_row}:B{header_row}")
        
        # Metrics
        metrics = get_metrics(period=period)
        for offset, (key, label) in enumerate(DISPLAY_ORDER):
            row = first_metric_row + offset
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=metrics[key])
  

def main():
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"HappyMan_{SHOP_ID}_{timestamp}.xlsx"
    report_path = REPORT_DIR / filename

    wb = Workbook()
    # Remove the default sheet
    wb.remove(wb.active)
    
    # Build sheets in display order
    build_summary_sheet(wb, timestamp)
    build_sales_list_sheet(wb, timestamp)
    build_items_detail_sheet(wb, timestamp)
    
    # Set the active sheet to Summary so it's what opens first
    wb.active = wb["Summary"]
    
    wb.save(report_path)
    print(f"Saved: {report_path}")
    return report_path

if __name__ == "__main__":
  main()

