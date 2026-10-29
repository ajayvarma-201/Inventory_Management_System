from database import get_connection


def best_selling_products():

    print("\n" + "=" * 60)
    print("              BEST-SELLING PRODUCTS")
    print("=" * 60)

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
            ORDER BY quantity_sold DESC
        """)

        products = cursor.fetchall()

        if not products:
            print("\nNo sales data available.")
            return

        print(
            f"{'Product':<25}"
            f"{'Quantity Sold':<18}"
            f"{'Revenue (₹)':<15}"
        )

        print("-" * 60)

        for product in products:

            print(
                f"{product['product_name']:<25}"
                f"{product['quantity_sold']:<18}"
                f"{product['revenue']:<15.2f}"
            )

        print("-" * 60)

    except Exception as error:

        print("Database error:", error)

    finally:

        connection.close()

    
def revenue_analysis():

    print("\n" + "=" * 60)
    print("                 REVENUE ANALYSIS")
    print("=" * 60)

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
            ORDER BY revenue DESC
        """)

        products = cursor.fetchall()

        if not products:
            print("\nNo sales data available.")
            return

        print(
            f"{'Product':<25}"
            f"{'Quantity Sold':<18}"
            f"{'Revenue (₹)':<15}"
        )

        print("-" * 60)

        for product in products:

            print(
                f"{product['product_name']:<25}"
                f"{product['quantity_sold']:<18}"
                f"{product['revenue']:<15.2f}"
            )

        print("-" * 60)

    except Exception as error:

        print("Database error:", error)

    finally:

        connection.close()
        
    
def customer_analysis():

    print("\n" + "=" * 60)
    print("             CUSTOMER PURCHASE ANALYSIS")
    print("=" * 60)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                customer_name,
                COUNT(bill_number) AS total_bills,
                SUM(grand_total) AS total_spent
            FROM sales
            GROUP BY customer_name
            ORDER BY total_spent DESC
        """)

        customers = cursor.fetchall()

        if not customers:
            print("\nNo customer sales data available.")
            return

        print(
            f"{'Customer':<25}"
            f"{'Bills':<15}"
            f"{'Total Spent (₹)':<20}"
        )

        print("-" * 60)

        for customer in customers:

            print(
                f"{customer['customer_name']:<25}"
                f"{customer['total_bills']:<15}"
                f"{customer['total_spent']:<20.2f}"
            )

        print("-" * 60)

    except Exception as error:

        print("Database error:", error)

    finally:

        connection.close()

    
def monthly_sales():

    print("\n" + "=" * 60)
    print("                 MONTHLY SALES ANALYSIS")
    print("=" * 60)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                strftime('%Y-%m', date) AS month,
                COUNT(bill_number) AS total_bills,
                SUM(grand_total) AS total_revenue
            FROM sales
            GROUP BY month
            ORDER BY month
        """)

        monthly_data = cursor.fetchall()

        if not monthly_data:
            print("\nNo sales data available.")
            return

        print(
            f"{'Month':<20}"
            f"{'Bills':<15}"
            f"{'Revenue (₹)':<20}"
        )

        print("-" * 60)

        for data in monthly_data:

            print(
                f"{data['month']:<20}"
                f"{data['total_bills']:<15}"
                f"{data['total_revenue']:<20.2f}"
            )

        print("-" * 60)

    except Exception as error:

        print("Database error:", error)

    finally:

        connection.close()
        
    
def demand_analysis():

    print("\n" + "=" * 75)
    print("                    PRODUCT DEMAND ANALYSIS")
    print("=" * 75)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                product_name,
                SUM(quantity) AS quantity_sold,
                COUNT(DISTINCT bill_number) AS bills
            FROM sale_items
            GROUP BY product_name
            ORDER BY quantity_sold DESC
        """)

        products = cursor.fetchall()

        if not products:
            print("\nNo sales data available.")
            return

        print(
            f"{'Product':<20}"
            f"{'Quantity Sold':<18}"
            f"{'Bills':<12}"
            f"{'Avg/ Bill':<15}"
            f"{'Demand':<10}"
        )

        print("-" * 75)

        for product in products:

            quantity = product["quantity_sold"]
            bills = product["bills"]

            average = quantity / bills

            if quantity >= 20:
                demand = "High"

            elif quantity >= 5:
                demand = "Medium"

            else:
                demand = "Low"

            print(
                f"{product['product_name']:<20}"
                f"{quantity:<18}"
                f"{bills:<12}"
                f"{average:<15.2f}"
                f"{demand:<10}"
            )

        print("-" * 75)

    except Exception as error:

        print("Database error:", error)

    finally:

        connection.close()
        
def analytics_menu():

    while True:

        print("\n" + "=" * 50)
        print("              DATA ANALYTICS")
        print("=" * 50)

        print("1. Best-Selling Products")
        print("2. Revenue Analysis")
        print("3. Customer Purchase Analysis")
        print("4. Monthly Sales Analysis")
        print("5. Product Demand Analysis")
        print("6. Back to Main Menu")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            best_selling_products()

        elif choice == "2":
            revenue_analysis()

        elif choice == "3":
            customer_analysis()

        elif choice == "4":
            monthly_sales()

        elif choice == "5":
            demand_analysis()

        elif choice == "6":
            break

        else:
            print("\nInvalid choice! Please try again.")
            
if __name__ == "__main__":
    analytics_menu()