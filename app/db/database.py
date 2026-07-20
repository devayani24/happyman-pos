import sqlite3
from pathlib import Path
from contextlib import contextmanager
from app.config import DATABASE_PATH
from app.models import Transaction
from datetime import date, timedelta

def build_date_filter(period: str, column: str = 'timestamp') -> str:
    """Return SQL fragment that filters by the requested period.
    
    Args:
        period: One of 'today', 'yesterday', 'last_7_days', 'last_30_days', 'this_month', 'all_time'.
        column: Column to filter on. Use table alias if joined
                (e.g., 's.timestamp').
    
    Returns:
        SQL fragment starting with 'AND', or empty string for 'all_time'.
    """
    if period == 'today':
        return f"AND date({column}) = date('now', 'localtime')"
    
    if period == 'yesterday':
        return f"AND date({column}) = date('now', '-1 day', 'localtime')"
    
    if period == 'last_7_days':
        return f"AND date({column}) >= date('now', '-6 days', 'localtime')"
    
    if period == 'last_30_days':
        return f"AND date({column}) >= date('now', '-29 days', 'localtime')"
    
    if period == 'this_month':
        return f"AND strftime('%Y-%m', {column}) = strftime('%Y-%m', 'now', 'localtime')"
    
    if period == 'all_time':
        return ""
    
    raise ValueError(f"Unknown period: {period}")

@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    # rows accessible by column name
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_sales_data(period: str = "all_time"):
    """Return all sales with their item counts."""
    
    date_filter = build_date_filter(period, column='s.timestamp')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                date(timestamp) as date,
	            time(timestamp) as time,
                s.*,
                COUNT(si.id) AS items_count
            FROM sales s
            LEFT JOIN sale_items si ON si.transaction_id = s.id
            GROUP BY s.id
            HAVING 1=1
            {date_filter}
            ORDER BY s.id DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
   
def get_sale_items_data(period: str = "all_time"):
   date_filter = build_date_filter(period, column='s.timestamp')
   with get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute(
        f"""
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
        WHERE 1=1
        {date_filter}
        ORDER BY s.bill_number DESC, p.name
        """
       )
       return [ dict(row) for row in cursor.fetchall()]
   
def get_items_for_sale(bill_number: int):
    """Return items for a specific sale."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                si.*,
                p.name as product_name,
                p.local_name as product_local_name
            FROM sale_items si
            LEFT JOIN products p ON p.product_code = si.product_id
            WHERE si.transaction_id = (
                SELECT id FROM sales WHERE bill_number = ?
            )
        """, (bill_number,))
        return [dict(row) for row in cursor.fetchall()]

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
      
      row =  cursor.fetchone()
      if row:
          last_number  = row['bill_number']
          new_number = last_number + 1
      else:
          new_number = 1

      new_bill_number = f"{new_number}"

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

def get_daily_metrics(days: int = 30) -> list:
    """Return per-day aggregated metrics for the last N days.
    
    Used for time-series charts on the Summary sheet.
    
    Args:
        days: Number of days to include. Default 30.
    
    Returns:
        List of dicts, one per day with keys:
        sale_date, total_revenue, sale_count, cash_total, 
        gpay_total, voided_count, voided_amount.
        Ordered oldest first.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                date(timestamp) AS sale_date,
                COALESCE(SUM(CASE WHEN is_void = 0 THEN total_price ELSE 0 END), 0) AS total_revenue,
                COALESCE(SUM(CASE WHEN is_void = 0 THEN 1 ELSE 0 END), 0) AS sale_count,
                COALESCE(SUM(CASE WHEN is_void = 0 AND payment_mode = 'cash' THEN total_price ELSE 0 END), 0) AS cash_total,
                COALESCE(SUM(CASE WHEN is_void = 0 AND payment_mode = 'gpay' THEN total_price ELSE 0 END), 0) AS gpay_total,
                COALESCE(SUM(CASE WHEN is_void = 1 THEN 1 ELSE 0 END), 0) AS voided_count,
                COALESCE(SUM(CASE WHEN is_void = 1 THEN total_price ELSE 0 END), 0) AS voided_amount
            FROM sales
            WHERE date(timestamp) >= date('now', ?, 'localtime')
            GROUP BY date(timestamp)
            ORDER BY sale_date ASC
        """, (f'-{days - 1} days',))

        # Sparse: only dates that have sales
        metrics_by_date = {row['sale_date']: dict(row) for row in cursor.fetchall()}
        
        # Date range boundaries
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        # Fill in every day, using zeros for days without sales
        result = []
        current_date = start_date
        while current_date <= end_date:
            key = current_date.isoformat()
            if key in metrics_by_date:
                result.append(metrics_by_date[key])
            else:
                result.append({
                    'sale_date': key,
                    'total_revenue': 0,
                    'sale_count': 0,
                    'cash_total': 0,
                    'gpay_total': 0,
                    'voided_count': 0,
                    'voided_amount': 0,
                })
            current_date += timedelta(days=1)
        
        return result


def get_top_products_by_revenue(limit: int = 7, period: str = "all_time") -> list:
    """Top products ranked by revenue. Reuses existing pattern."""
    ...
    date_filter = build_date_filter(period, column='s.timestamp')

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                p.name,
                COALESCE(SUM(si.line_total), 0) AS revenue
            FROM sale_items si
            INNER JOIN products p ON p.product_code = si.product_id
            INNER JOIN sales s ON s.id = si.transaction_id
            WHERE s.is_void = 0
            {date_filter}
            GROUP BY si.product_id, p.name
            ORDER BY revenue DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_top_products_by_weight(limit: int = 7, period: str = "last_7_days") -> list:
    """Top products ranked by weight sold (kg). 
    
    Only includes items sold by weight (g or kg).
    Excludes voided sales.
    """
    date_filter = build_date_filter(period, column='s.timestamp')

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                p.name,
                SUM(
                    CASE 
                        WHEN si.cart_unit = 'g' THEN (0.001 * si.cart_weight * si.cart_packets)
                        WHEN si.cart_unit = 'kg' THEN (si.cart_weight * si.cart_packets)
                        ELSE 0
                    END
                ) AS weight_kg
            FROM sale_items si
            INNER JOIN products p ON p.product_code = si.product_id
            INNER JOIN sales s ON s.id = si.transaction_id
            WHERE s.is_void = 0
                AND si.cart_unit IN ('g', 'kg')
            {date_filter}
            GROUP BY si.product_id, p.name
            HAVING weight_kg > 0
            ORDER BY weight_kg DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_top_products_by_pieces(limit: int = 7, period: str = "last_7_days") -> list:
    """Top products ranked by pieces sold.
    
    Only includes items sold by piece.
    Excludes voided sales.
    """
    date_filter = build_date_filter(period, column='s.timestamp')

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                p.name,
                SUM(si.cart_pieces * si.cart_packets) AS pieces_sold
            FROM sale_items si
            INNER JOIN products p ON p.product_code = si.product_id
            INNER JOIN sales s ON s.id = si.transaction_id
            WHERE s.is_void = 0
                AND si.cart_unit = 'pc'
            GROUP BY si.product_id, p.name
            HAVING pieces_sold > 0
            ORDER BY pieces_sold DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    print(get_sale_items_data(period = "today"))