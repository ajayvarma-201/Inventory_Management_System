import sqlite3
import os

# Database location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "billing.db")


def get_connection():
    """Create and return a database connection."""

    connection = sqlite3.connect(DB_FILE)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    """Create all required database tables."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0),
                quantity INTEGER NOT NULL CHECK(quantity >= 0)
            )
        """)

        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                address TEXT NOT NULL
            )
        """)

        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                bill_number TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount_percent REAL NOT NULL,
                discount_amount REAL NOT NULL,
                gst_percent REAL NOT NULL,
                gst_amount REAL NOT NULL,
                grand_total REAL NOT NULL,

                FOREIGN KEY (customer_id)
                    REFERENCES customers(id)
            )
        """)

        # Sale items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                amount REAL NOT NULL,

                FOREIGN KEY (bill_number)
                    REFERENCES sales(bill_number)
                    ON DELETE CASCADE
            )
        """)

        connection.commit()

        print("Database tables created successfully!")

    except sqlite3.Error as error:

        connection.rollback()

        print("Database error:", error)

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()