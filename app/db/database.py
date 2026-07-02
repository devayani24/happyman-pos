import sqlite3
from pathlib import Path
from contextlib import contextmanager
from app.config import DATABASE_PATH
from app.models import Transaction

def build_date_filter(period: str) -> str:
    """Return SQL fragment that filters sales by the requested period.
    
    Assumes the fragment will be appended to WHERE 1=1 in the caller,
    so it starts with 'AND'.
    """
    if period == 'today':
        return "AND date(timestamp) = date('now', 'localtime')"
    if period == 'yesterday':
        return "AND date(timestamp) = date('now', '-1 day', 'localtime')"
    
    if period == 'last_7_days':
        return "AND date(timestamp) >= date('now', '-6 days', 'localtime')"
    
    if period == 'last_30_days':
        return "AND date(timestamp) >= date('now', '-29 days', 'localtime')"
    if period == 'this_month':
        return "AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now', 'localtime')"
    if period == 'all_time':
        return ""
    raise ValueError(f"Unknown period: {period}") 

@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    # rows accessible by column name
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_sales_data():
    """Return all sales with their item counts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.*,
                COUNT(si.id) AS items_count
            FROM sales s
            LEFT JOIN sale_items si ON si.transaction_id = s.id
            GROUP BY s.id
            ORDER BY s.id ASC
        """)
        return [dict(row) for row in cursor.fetchall()]
   
def get_sale_items_data():
   with get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute(
        """
        SELECT 
            s.bill_number,
            s.is_void,
            p.name,
            p.local_name,
            COALESCE(si.cart_weight, si.cart_pieces) AS quantity,
            si.cart_unit AS unit,
            si.cart_packets AS packets,
            si.line_total
        FROM sale_items si
        LEFT JOIN sales s ON s.id = si.transaction_id
        LEFT JOIN products p ON p.product_code = si.product_id
        ORDER BY s.bill_number, p.name
        """
       )
       return [ dict(row) for row in cursor.fetchall()]

def save_sale_to_db(sale: Transaction):
    
    with get_connection() as conn:
      cursor = conn.cursor()
      # get the last bill number from the server
      cursor.execute(
          """ 
          SELECT bill_number FROM sales
          WHERE shop_id = ?
          ORDER BY id DESC LIMIT 1;
          
          """,(sale.shop_id,))
      
      last_row_bill_number =  cursor.fetchone()
      if last_row_bill_number:
          last_number  = int(last_row_bill_number[0].split("-")[1])
          new_number = last_number + 1
      else:
          new_number = 1

      new_bill_number = f"{sale.shop_id}-{new_number}"

      # save sale to the database
      cursor.execute(
        """ INSERT INTO sales (shop_id,bill_number,timestamp,total_price,payment_mode,amount_received,amount_change) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (sale.shop_id, new_bill_number,sale.timestamp.isoformat(), sale.total_price,sale.payment_mode, sale.amount_received,sale.amount_change)
      )
      # get the last sale id from the database
      sale_id = cursor.lastrowid

      for item in sale.items:
        cursor.execute(
            '''INSERT INTO sale_items 
              (transaction_id, product_id, cart_unit, cart_weight,cart_pieces, cart_packets, line_total)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (sale_id, item.product_id, item.cart_unit, item.cart_weight,item.cart_pieces, item.cart_packets, item.line_total)
        )
      return new_bill_number


def get_all_categories():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")

        # Convert rows to dicts with camelCase keys for JS
        categories = [
            {
                'id': row['id'],
                'code': row['code'],
                'type': row['type'],
                'localTypeName': row['local_type_name']
            }
            for row in cursor.fetchall()
        ]
        print(categories)
        
        return categories
    
def get_all_products() -> list:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.product_code AS id,
                p.name,
                p.local_name AS localName,
                p.category_id AS categoryId,
                p.sold_by AS soldBy,
                p.price,
                p.price_unit AS priceUnit,
                p.price_unit_type AS priceUnitType,
                p.image,
                p.is_active AS isActive
            FROM products p
            WHERE p.is_active = 1
            ORDER BY p.category_id, p.product_code
        """)
        products = [dict(row) for row in cursor.fetchall()]
        print(len(products))
        return products

def get_metrics(period: str = "all_time") -> dict:
    """Return aggregated metrics for the Summary sheet.
    
    Args:
        period: One of 'today', 'yesterday', 'last_7_days', 
                'last_30_days', 'this_month', 'all_time'.
    
    Returns:
        Dict with keys: total_revenue, sale_count, avg_transaction,
        cash_total, gpay_total, voided_count, voided_amount.
    """

    date_filter = build_date_filter(period)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                COALESCE(SUM(CASE WHEN is_void = 0 THEN total_price ELSE 0 END), 0) AS total_revenue,
                SUM(CASE WHEN is_void = 0 THEN 1 ELSE 0 END) AS sale_count,
                COALESCE(SUM(CASE WHEN is_void = 0 AND payment_mode = 'cash' THEN total_price ELSE 0 END), 0) AS cash_total,
                COALESCE(SUM(CASE WHEN is_void = 0 AND payment_mode = 'gpay' THEN total_price ELSE 0 END), 0) AS gpay_total,
                SUM(CASE WHEN is_void = 1 THEN 1 ELSE 0 END) AS voided_count,
                COALESCE(SUM(CASE WHEN is_void = 1 THEN total_price ELSE 0 END), 0) AS voided_amount
            FROM sales
            WHERE 1=1
            {date_filter}
        """)
        row = dict(cursor.fetchone())
        # Compute avg in Python to handle divide-by-zero cleanly
        row['avg_transaction'] = (
            row['total_revenue'] / row['sale_count'] 
            if row['sale_count'] > 0 else 0
        )
        return row


def get_top_products(limit=7):
    """Return top products by revenue for the Summary sheet."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.name,
                COUNT(si.id) AS units_sold,
                COALESCE(SUM(si.line_total), 0) AS revenue
            FROM sale_items si
            JOIN products p ON p.product_code = si.product_id
            JOIN sales s ON s.id = si.transaction_id
            WHERE s.is_void = 0
            GROUP BY si.product_id, p.name
            ORDER BY revenue DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    get_all_products()