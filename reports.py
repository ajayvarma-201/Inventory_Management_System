from database import get_connection
from datetime import datetime


def view_sales():
    print("\n--- Sales History ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                bill_number,
                date,
                customer_name,
                grand_total
            FROM sales
            ORDER BY date DESC
        """)

        sales = cursor.fetchall()

        if not sales:
            print("No sales records available.")
            return

        print("-" * 85)
        print(
            f"{'Bill Number':<25}"
            f"{'Date':<22}"
            f"{'Customer':<20}"
            f"{'Total (₹)':<15}"
        )
        print("-" * 85)

        for sale in sales:

            print(
                f"{sale['bill_number']:<25}"
                f"{sale['date']:<22}"
                f"{sale['customer_name']:<20}"
                f"{sale['grand_total']:<15.2f}"
            )

        print("-" * 85)

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def search_sale():
    print("\n--- Search Sale ---")

    bill_number = input(
        "Enter Bill Number: "
    ).strip()

    if not bill_number:
        print("Bill number cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Get bill information
        cursor.execute("""
            SELECT
                bill_number,
                date,
                customer_name,
                subtotal,
                discount_percent,
                discount_amount,
                gst_percent,
                gst_amount,
                grand_total
            FROM sales
            WHERE bill_number = ?
        """, (bill_number,))

        sale = cursor.fetchone()

        if not sale:
            print("Bill not found!")
            return

        # Get items belonging to this bill
        cursor.execute("""
            SELECT
                product_name,
                price,
                quantity,
                amount
            FROM sale_items
            WHERE bill_number = ?
        """, (bill_number,))

        items = cursor.fetchall()

        print("\nBill Found!")
        print("=" * 50)

        print(
            "Bill Number :",
            sale["bill_number"]
        )

        print(
            "Date        :",
            sale["date"]
        )

        print(
            "Customer    :",
            sale["customer_name"]
        )

        print("-" * 50)

        print(
            f"{'Product':<20}"
            f"{'Price':<10}"
            f"{'Qty':<8}"
            f"{'Amount':<12}"
        )

        print("-" * 50)

        for item in items:

            print(
                f"{item['product_name']:<20}"
                f"{item['price']:<10.2f}"
                f"{item['quantity']:<8}"
                f"{item['amount']:<12.2f}"
            )

        print("-" * 50)

        print(
            f"Subtotal       : "
            f"₹{sale['subtotal']:.2f}"
        )

        print(
            f"Discount       : "
            f"₹{sale['discount_amount']:.2f}"
        )

        print(
            f"GST            : "
            f"₹{sale['gst_amount']:.2f}"
        )

        print(
            f"Grand Total    : "
            f"₹{sale['grand_total']:.2f}"
        )

        print("=" * 50)

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def total_revenue():
    print("\n--- Total Revenue ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_bills,
                COALESCE(SUM(grand_total), 0)
                AS total_revenue
            FROM sales
        """)

        result = cursor.fetchone()

        if result["total_bills"] == 0:
            print(
                "No sales available "
                "to calculate revenue."
            )
            return

        print(
            f"Total Revenue: "
            f"₹{result['total_revenue']:.2f}"
        )

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def today_sales():
    print("\n--- Today's Sales ---")

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                bill_number,
                customer_name,
                grand_total
            FROM sales
            WHERE date LIKE ?
            ORDER BY date DESC
        """, (today + "%",))

        sales = cursor.fetchall()

        if not sales:
            print("No sales recorded today.")
            return

        total = 0

        print("-" * 70)

        for sale in sales:

            print(
                f"Bill: {sale['bill_number']} | "
                f"Customer: {sale['customer_name']} | "
                f"Total: ₹{sale['grand_total']:.2f}"
            )

            total += sale["grand_total"]

        print("-" * 70)

        print(
            "Number of Bills:",
            len(sales)
        )

        print(
            f"Today's Revenue: ₹{total:.2f}"
        )

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def product_sales():
    print("\n--- Product-Wise Sales ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                product_name,
                SUM(quantity) AS quantity_sold,
                SUM(amount) AS revenue
            FROM sale_items
            GROUP BY product_name
            ORDER BY product_name
        """)

        products = cursor.fetchall()

        if not products:
            print("No sales records available.")
            return

        print("-" * 60)

        print(
            f"{'Product':<25}"
            f"{'Quantity Sold':<15}"
            f"{'Sales Amount (₹)':<20}"
        )

        print("-" * 60)

        for product in products:

            print(
                f"{product['product_name']:<25}"
                f"{product['quantity_sold']:<15}"
                f"{product['revenue']:<20.2f}"
            )

        print("-" * 60)

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def sales_summary():
    print("\n--- Sales Summary ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Total bills and revenue
        cursor.execute("""
            SELECT
                COUNT(*) AS total_bills,
                COALESCE(SUM(grand_total), 0)
                AS total_revenue
            FROM sales
        """)

        sales_result = cursor.fetchone()

        if sales_result["total_bills"] == 0:
            print("No sales records available.")
            return

        # Total items sold
        cursor.execute("""
            SELECT
                COALESCE(SUM(quantity), 0)
                AS total_items
            FROM sale_items
        """)

        items_result = cursor.fetchone()

        total_bills = sales_result["total_bills"]
        total_revenue_amount = sales_result[
            "total_revenue"
        ]
        total_items = items_result["total_items"]

        average_bill = (
            total_revenue_amount / total_bills
        )

        print(
            "Total Bills      :",
            total_bills
        )

        print(
            "Total Items Sold :",
            total_items
        )

        print(
            f"Total Revenue    : "
            f"₹{total_revenue_amount:.2f}"
        )

        print(
            f"Average Bill     : "
            f"₹{average_bill:.2f}"
        )

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def reports_menu():

    while True:

        print("\n" + "=" * 40)
        print("          SALES REPORTS")
        print("=" * 40)

        print("1. View Sales History")
        print("2. Search Bill")
        print("3. Total Revenue")
        print("4. Today's Sales")
        print("5. Product-Wise Sales")
        print("6. Sales Summary")
        print("7. Back to Main Menu")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            view_sales()

        elif choice == "2":
            search_sale()

        elif choice == "3":
            total_revenue()

        elif choice == "4":
            today_sales()

        elif choice == "5":
            product_sales()

        elif choice == "6":
            sales_summary()

        elif choice == "7":
            break

        else:
            print(
                "Invalid choice! Please select 1-7."
            )