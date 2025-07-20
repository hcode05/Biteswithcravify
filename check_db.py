import sqlite3
import os

# Get the database path
db_path = r"c:\Users\ADMIN\Desktop\foodproject\db.sqlite3"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== RECENT ORDERS ===")
    cursor.execute("""
        SELECT order_number, first_name, last_name, status, is_ordered, payment_method, total, created_at, payment_id
        FROM orders_order 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    orders = cursor.fetchall()
    for order in orders:
        print(f"Order: {order[0]} | Name: {order[1]} {order[2]} | Status: {order[3]} | Ordered: {order[4]} | Method: {order[5]} | Total: ${order[6]} | Payment ID: {order[8]}")
    
    print("\n=== RECENT PAYMENTS ===")
    cursor.execute("""
        SELECT id, user_id, transaction_id, payment_method, amount, status, created_at
        FROM orders_payment 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    payments = cursor.fetchall()
    for payment in payments:
        print(f"Payment ID: {payment[0]} | User: {payment[1]} | Transaction: {payment[2]} | Method: {payment[3]} | Amount: ${payment[4]} | Status: {payment[5]}")
    
    print("\n=== ORDERS WITHOUT PAYMENTS ===")
    cursor.execute("""
        SELECT order_number, status, is_ordered, payment_id
        FROM orders_order 
        WHERE payment_id IS NULL
        ORDER BY created_at DESC
    """)
    
    orphan_orders = cursor.fetchall()
    for order in orphan_orders:
        print(f"Order: {order[0]} | Status: {order[1]} | Ordered: {order[2]} | Payment ID: {order[3]}")
    
    conn.close()
else:
    print("Database file not found at:", db_path)
