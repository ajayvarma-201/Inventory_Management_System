from database import get_connection

LOW_STOCK_LIMIT = 10


def view_inventory():
    print("\n--- Inventory ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, price, quantity
            FROM products
            ORDER BY id
        """)

        products = cursor.fetchall()

        if not products:
            print("No products available.")
            return

        print("-" * 65)
        print(
            f"{'ID':<10}"
            f"{'Name':<20}"
            f"{'Price':<12}"
            f"{'Stock':<10}"
            f"{'Status':<15}"
        )
        print("-" * 65)

        for product in products:

            quantity = product["quantity"]

            if quantity == 0:
                status = "OUT OF STOCK"
            elif quantity <= LOW_STOCK_LIMIT:
                status = "LOW STOCK"
            else:
                status = "AVAILABLE"

            print(
                f"{product['id']:<10}"
                f"{product['name']:<20}"
                f"{product['price']:<12.2f}"
                f"{quantity:<10}"
                f"{status:<15}"
            )

        print("-" * 65)

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def add_stock():
    print("\n--- Add Stock ---")

    product_id = input("Enter Product ID: ").strip()

    if not product_id:
        print("Product ID cannot be empty!")
        return

    try:
        quantity = int(input("Enter quantity to add: "))

        if quantity <= 0:
            print("Quantity must be greater than 0!")
            return

    except ValueError:
        print("Invalid quantity! Please enter a whole number.")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, quantity
            FROM products
            WHERE id = ?
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            print("Product not found!")
            return

        new_quantity = product["quantity"] + quantity

        cursor.execute("""
            UPDATE products
            SET quantity = ?
            WHERE id = ?
        """, (
            new_quantity,
            product_id
        ))

        connection.commit()

        print(
            f"\n{quantity} units added successfully!"
        )
        print(
            f"Current stock: {new_quantity}"
        )

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def remove_stock():
    print("\n--- Remove Stock ---")

    product_id = input("Enter Product ID: ").strip()

    if not product_id:
        print("Product ID cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, quantity
            FROM products
            WHERE id = ?
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            print("Product not found!")
            return

        print("Product:", product["name"])
        print("Available Stock:", product["quantity"])

        try:
            quantity = int(
                input("Enter quantity to remove: ")
            )

            if quantity <= 0:
                print("Quantity must be greater than 0!")
                return

        except ValueError:
            print("Invalid quantity! Please enter a whole number.")
            return

        if quantity > product["quantity"]:
            print(
                f"Insufficient stock! "
                f"Only {product['quantity']} units available."
            )
            return

        new_quantity = product["quantity"] - quantity

        cursor.execute("""
            UPDATE products
            SET quantity = ?
            WHERE id = ?
        """, (
            new_quantity,
            product_id
        ))

        connection.commit()

        print(
            f"\n{quantity} units removed successfully!"
        )
        print(
            f"Remaining stock: {new_quantity}"
        )

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def low_stock_alert():
    print("\n--- Low Stock Alert ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, quantity
            FROM products
            WHERE quantity <= ?
            ORDER BY quantity
        """, (LOW_STOCK_LIMIT,))

        products = cursor.fetchall()

        if not products:
            print("No low-stock products.")
            return

        for product in products:
            print(
                f"{product['id']} - "
                f"{product['name']} - "
                f"Stock: {product['quantity']}"
            )

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def inventory_summary():
    print("\n--- Inventory Summary ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_products,
                COALESCE(SUM(quantity), 0) AS total_units,
                COALESCE(
                    SUM(
                        CASE
                            WHEN quantity <= ? THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS low_stock_products,
                COALESCE(
                    SUM(
                        CASE
                            WHEN quantity = 0 THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS out_of_stock,
                COALESCE(
                    SUM(quantity * price),
                    0
                ) AS inventory_value
            FROM products
        """, (LOW_STOCK_LIMIT,))

        summary = cursor.fetchone()

        print(
            "Total Products        :",
            summary["total_products"]
        )

        print(
            "Total Units           :",
            summary["total_units"]
        )

        print(
            "Low Stock Products    :",
            summary["low_stock_products"]
        )

        print(
            "Out of Stock          :",
            summary["out_of_stock"]
        )

        print(
            "Inventory Value       : ₹",
            round(summary["inventory_value"], 2)
        )

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def inventory_menu():

    while True:

        print("\n" + "=" * 40)
        print("       INVENTORY MANAGEMENT")
        print("=" * 40)

        print("1. View Inventory")
        print("2. Add Stock")
        print("3. Remove Stock")
        print("4. Low Stock Alert")
        print("5. Inventory Summary")
        print("6. Back to Main Menu")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            view_inventory()

        elif choice == "2":
            add_stock()

        elif choice == "3":
            remove_stock()

        elif choice == "4":
            low_stock_alert()

        elif choice == "5":
            inventory_summary()

        elif choice == "6":
            break

        else:
            print("Invalid choice! Please select 1-6.")