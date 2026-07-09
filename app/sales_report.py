from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from app.config import REPORT_DIR, SHOP_ID
from datetime import datetime
from app.db.database import get_sales_data, get_sale_items_data,get_daily_metrics, get_top_products_by_revenue, get_top_products_by_weight, get_top_products_by_pieces
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side



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

def build_daily_charts(ws,data_ws):
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
    data_ws.append(headers)
    
    # Write data
    for row in daily:
        data_ws.append(list(row.values()))
    
    last_data_row = HEADER_ROW + len(daily)
    
    # Categories reference — dates in column A
    categories = Reference(data_ws, min_col=1, min_row=DATA_START_ROW, max_row=last_data_row)
    
    # Chart 1: Daily Revenue
    revenue_chart = BarChart()
    revenue_chart.title = "Daily Revenue (Last 30 Days)"
    revenue_chart.y_axis.title = "Revenue (₹)"
    revenue_chart.x_axis.title = "Date"
    revenue_chart.legend = None
    
    revenue_data = Reference(data_ws, min_col=2, min_row=HEADER_ROW, max_row=last_data_row)
    revenue_chart.add_data(revenue_data, titles_from_data=True)
    revenue_chart.set_categories(categories)
    
    # Chart 2: Cash vs GPay
    payment_chart = BarChart()
    payment_chart.title = "Cash vs GPay (Last 30 Days)"
    payment_chart.y_axis.title = "Amount (₹)"
    payment_chart.x_axis.title = "Date"
    
    payment_data = Reference(data_ws, min_col=4, min_row=HEADER_ROW, max_col=5, max_row=last_data_row)
    payment_chart.add_data(payment_data, titles_from_data=True)
    payment_chart.set_categories(categories)
    
    # Position charts to the RIGHT of data (columns 1-7 have data)
    ws.add_chart(revenue_chart, "B5")
    ws.add_chart(payment_chart, "L5")

    return last_data_row

def build_top_products_chart(
      ws, 
      data_ws, 
      start_row: int, 
      top_product_func, 
      limit: int, 
      period: str, 
      chart_title: str, 
      chart_y_title: str, 
      cell_placement: str
    ) -> int:
   
    """Build the top products charts on the Summary sheet."""
    top_products = top_product_func(limit=limit, period=period)

    header_row = start_row + 1
    first_data_row = header_row + 1
    last_data_row = first_data_row + len(top_products) - 1
    

    if not top_products:
        ws.cell(row=header_row, column=1, value=f"No data for {chart_title}")
        return header_row
    
    # Write headers
    headers = list(top_products[0].keys())
    data_ws.append(headers)

    # Write data
    for row in top_products:
        data_ws.append(list(row.values()))
    
    

    # Categories reference — dates in column A
    categories = Reference(data_ws, min_col=1, min_row=first_data_row, max_row=last_data_row)
    
    # Chart 1
    top_products_chart = BarChart()
    top_products_chart.title = chart_title
    top_products_chart.y_axis.title = chart_y_title
    top_products_chart.legend = None
    
    top_products_data = Reference(data_ws, min_col=2, min_row=header_row, max_row=last_data_row)
    
    top_products_chart.add_data(top_products_data, titles_from_data=True)
    top_products_chart.set_categories(categories)

    ws.add_chart(top_products_chart, cell_placement)
    return last_data_row

def build_kpi_box(ws, top_left_cell, label, value, context, color):
    """Draw a KPI box with label, value, and context text."""
    row, col = top_left_cell

    FONT_NAME = 'Calibri'
    TEXT_COLOR = '1F3864'      # Dark blue for value
    LABEL_TEXT_COLOR = 'FFFFFF' # White for header text on colored bg
    CONTEXT_COLOR = '595959'    # Muted grey for subtitle
    BORDER_COLOR = 'BFBFBF'     # Light grey border

    thin_border = Side(style='thin', color=BORDER_COLOR)
    box_border = Border(
        left=thin_border,
        right=thin_border,
        top=thin_border,
        bottom=thin_border,
    )
    
    # Label cell (colored header)
    label_cell = ws.cell(row=row, column=col, value=label.upper())

    label_cell.fill = PatternFill(
        fill_type='solid',
        start_color=color,
    )
    label_cell.font = Font(
        name=FONT_NAME,
        size=10,
        bold=True,
        color=LABEL_TEXT_COLOR,
    )
    label_cell.alignment = Alignment(
        horizontal='center',
        vertical='center',
    )
    label_cell.border = box_border

    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+3)
    ws.row_dimensions[row].height = 22
    
    # Value cell (large number)
    value_cell = ws.cell(row=row+1, column=col, value=value)
    value_cell.font = Font(
        name=FONT_NAME,
        size=20,
        bold=True,
        color=TEXT_COLOR,
    )
    value_cell.alignment = Alignment(
        horizontal='center',
        vertical='center',
    )
    value_cell.number_format = '"₹"#,##0'
    ws.merge_cells(start_row=row+1, start_column=col, end_row=row+3, end_column=col+3)
    # ws.row_dimensions[row+2].height = 20
    # ws.row_dimensions[row+3].height = 20
    
    # Context cell (subtitle)
    context_cell = ws.cell(row=row+4, column=col, value=context)
    context_cell.font = Font(
        name=FONT_NAME,
        size=9,
        italic=True,
        color=CONTEXT_COLOR,
    )
    context_cell.alignment = Alignment(
        horizontal='center',
        vertical='center',
    )
    ws.merge_cells(start_row=row+4, start_column=col, end_row=row+4, end_column=col+3)
    ws.row_dimensions[row+4].height = 18
    
    # ==================================================
    # SIDE BORDERS (to close the "card" appearance)
    # ==================================================
    # The label and value cells already have full borders.
    # Add left/right borders to intermediate cells to complete the card look.
    for r in range(row+1, row+5):
       for c in range(col,col+4):
        cell = ws.cell(row=r, column=c)
        existing = cell.border
        cell.border = Border(
            left=thin_border if c == col else existing.left,
            right=thin_border if c == (col+3) else existing.right,
            bottom=thin_border if r == (row+4) else existing.bottom,
        )
        
       

def build_summary_sheet(wb, timestamp, data_sheet):
    ws = wb.create_sheet("Summary")
    
    today = get_daily_metrics(days=1)[0]
    yesterday = get_daily_metrics(days=2)[0]
    # last_7 = get_metrics(period='last_7_days')
    

    # Box 1: Today's Revenue
    build_kpi_box(ws, top_left_cell=(3, 1), 
                label="TODAY'S REVENUE",
                value=today['total_revenue'],
                context=f"yesterday: ₹{yesterday['total_revenue']:,.0f}",
                color='1F3864') # Dark blue

    # Box 2: Today's Sale Count
    build_kpi_box(ws, top_left_cell=(3, 6), # 5 columns spacing (4 cols wide + 1 gap)
                label="TODAY'S SALES",
                value=today['sale_count'],
                context=f"yesterday: {yesterday['sale_count']}",
                color='2E7D32')
    




    current_row  = build_daily_charts(ws, data_sheet)
    current_row  = build_top_products_chart(ws, data_sheet, current_row ,get_top_products_by_weight,7, "last_30_days","Top Products by Weight (Last 30 Days)","Weight (kg)",  "B25")
    current_row  = build_top_products_chart(ws, data_sheet, current_row ,get_top_products_by_pieces,7, "last_30_days","Top Products by Pieces (Last 30 Days)","Pieces",  "L25")
    current_row  = build_top_products_chart(ws, data_sheet, current_row ,get_top_products_by_revenue,7, "last_30_days","Top Products by Revenue (Last 30 Days)","Revenue (₹)",  "B45")
    # Turn off worksheet gridlines
    ws.sheet_view.showGridLines = False

  

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"HappyMan_{SHOP_ID}_{timestamp}.xlsx"
    report_path = REPORT_DIR / filename

    wb = Workbook()
    wb.remove(wb.active)
    
    # Create hidden data sheet first (will be moved to end)
    data_sheet = wb.create_sheet("data_sheet")
    data_sheet.sheet_state = 'hidden'
    
    # Create visible sheets in display order
    build_summary_sheet(wb, timestamp, data_sheet)
    build_sales_list_sheet(wb, timestamp)
    build_items_detail_sheet(wb, timestamp)
    
    # Move data_sheet to the end
    wb.move_sheet("data_sheet", offset=len(wb.sheetnames) - wb.sheetnames.index("data_sheet") - 1)
    
    # Set active sheet
    wb.active = wb["Summary"]
    
    wb.save(report_path)
    print(f"✓ Saved: {report_path}")
    return report_path

if __name__ == "__main__":
  main()

