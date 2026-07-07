from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from app.config import REPORT_DIR, SHOP_ID
from datetime import datetime
from app.db.database import get_sales_data, get_sale_items_data,get_daily_metrics, get_top_products_by_revenue, get_top_products_by_weight, get_top_products_by_pieces
from openpyxl.chart import BarChart, Reference


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

def build_daily_charts(ws):
    """Build the daily time-series charts on the Summary sheet."""
    daily = get_daily_metrics(days=30)
    
    if not daily:
        ws.cell(row=1, column=1, value="No sales in the last 30 days")
        return
    
    # Layout constants
    HEADER_ROW = 1
    DATA_START_ROW = 2
    
    # Write headers
    headers = list(daily[0].keys())
    ws.append(headers)
    
    # Write data
    for row in daily:
        ws.append(list(row.values()))
    
    last_data_row = HEADER_ROW + len(daily)
    
    # Categories reference — dates in column A
    categories = Reference(ws, min_col=1, min_row=DATA_START_ROW, max_row=last_data_row)
    
    # Chart 1: Daily Revenue
    revenue_chart = BarChart()
    revenue_chart.title = "Daily Revenue (Last 30 Days)"
    revenue_chart.y_axis.title = "Revenue (₹)"
    revenue_chart.x_axis.title = "Date"
    revenue_chart.legend = None
    
    revenue_data = Reference(ws, min_col=2, min_row=HEADER_ROW, max_row=last_data_row)
    revenue_chart.add_data(revenue_data, titles_from_data=True)
    revenue_chart.set_categories(categories)
    
    # Chart 2: Cash vs GPay
    payment_chart = BarChart()
    payment_chart.title = "Cash vs GPay (Last 30 Days)"
    payment_chart.y_axis.title = "Amount (₹)"
    payment_chart.x_axis.title = "Date"
    
    payment_data = Reference(ws, min_col=4, min_row=HEADER_ROW, max_col=5, max_row=last_data_row)
    payment_chart.add_data(payment_data, titles_from_data=True)
    payment_chart.set_categories(categories)
    
    # Position charts to the RIGHT of data (columns 1-7 have data)
    ws.add_chart(revenue_chart, "I2")
    ws.add_chart(payment_chart, "I20")

    return last_data_row

def build_top_products_chart(
      ws, 
      start_row: int, 
      top_product_func: function, 
      limit: int, 
      period: str, 
      chart_title: str, 
      chart_y_title: str, 
      cell_placement: str
    ) -> int:
   
    header_row = start_row + 1
    first_data_row = header_row + 1
    last_data_row = first_data_row + len(top_products) - 1
    """Build the top products charts on the Summary sheet."""
    top_products = top_product_func(limit=limit, period=period)

    if not top_products:
        ws.cell(row=header_row, column=1, value=f"No data for {chart_title}")
        return header_row
    
    # Write headers
    headers = list(top_products[0].keys())
    ws.append(headers)

    # Write data
    for row in top_products:
        ws.append(list(row.values()))
    
    

    # Categories reference — dates in column A
    categories = Reference(ws, min_col=1, min_row=first_data_row, max_row=last_data_row)
    
    # Chart 1
    top_products_chart = BarChart()
    top_products_chart.title = chart_title
    top_products_chart.y_axis.title = chart_y_title
    top_products_chart.legend = None
    
    top_products_data = Reference(ws, min_col=2, min_row=header_row, max_row=last_data_row)
    
    top_products_chart.add_data(top_products_data, titles_from_data=True)
    top_products_chart.set_categories(categories)

    ws.add_chart(top_products_chart, cell_placement)
    return last_data_row

def build_summary_sheet(wb, timestamp):
    ws = wb.create_sheet("Summary")
    
    
    current_row  = build_daily_charts(ws)
    # print(get_daily_metrics(days=30))
    current_row  = build_top_products_chart(ws, current_row ,get_top_products_by_revenue,7, "last_30_days","Top Products by Revenue (Last 30 Days)","Revenue (₹)",  "I40")
    current_row  = build_top_products_chart(ws, current_row ,get_top_products_by_weight,7, "last_30_days","Top Products by Weight (Last 30 Days)","Weight (kg)",  "I60")
    current_row  = build_top_products_chart(ws, current_row ,get_top_products_by_pieces,7, "last_30_days","Top Products by Pieces (Last 30 Days)","Pieces",  "I80")
    

  

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

