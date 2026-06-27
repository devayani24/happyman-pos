from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from app.config import REPORT_DIR, SHOP_ID
from datetime import datetime
from app.db.database import get_sales_data, get_sale_items_data



def sales_report():
  timestamp = datetime.now().strftime("%Y-%m-%d")
  filename = f"HappyMan_{SHOP_ID}_{timestamp}.xlsx"
  report_path = REPORT_DIR / filename

  # Query database
  sales = get_sales_data()
  sale_items = get_sale_items_data()

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
  wb = Workbook()
  ws = wb.active
  ws.title = "Sales List"

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
    wb.save(report_path)
    return report_path

  for row_offset, sale in enumerate(sales):
    row = DATA_START_ROW + row_offset
    items_count = [item for item in sale_items if item['transaction_id'] == sale['id']]
    
    ws.cell(row=row, column=1, value=sale['bill_number'])
    ws.cell(row=row, column=2, value=sale['timestamp'][:10])  # date
    ws.cell(row=row, column=3, value=sale['timestamp'][11:16])  # time
    ws.cell(row=row, column=4, value=sale['total_price'])
    ws.cell(row=row, column=5, value=sale['payment_mode'])
    ws.cell(row=row, column=6, value=len(items_count))
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
  
  wb.save(report_path)
  print(f"✓ Saved: {report_path}")
  return report_path
     
  

if __name__ == "__main__":
  sales_report()

