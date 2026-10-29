from database import get_connection


def add_product():
    print("\n--- Add Product ---")

    product_id = input("Enter Product ID: ").strip()

    if not product_id:
        print("Product ID cannot be empty!")
        return

    name = input("Enter Product Name: ").strip()

    if not name:
        print("Product name cannot be empty!")
        return

    category = input("Enter Category: ").strip()

    if not category:
        print("Category cannot be empty!")
        return

    # Price validation
    try:
        price = float(input("Enter Price: "))

        if price <= 0:
            print("Price must be greater than 0!")
            return

    except ValueError:
        print("Invalid price! Please enter a number.")
        return

    # Quantity validation
    try:
        quantity = int(input("Enter Quantity: "))

        if quantity < 0:
            print("Quantity cannot be negative!")
            return

    except ValueError:
        print("Invalid quantity! Please enter a whole number.")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check duplicate Product ID
        cursor.execute(
            "SELECT id FROM products WHERE id = ?",
            (product_id,)
        )

        if cursor.fetchone():
            print("Product ID already exists!")
            return

        cursor.execute("""
            INSERT INTO products
            (id, name, category, price, quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            name,
            category,
            price,
            quantity
        ))

        connection.commit()

        print("\nProduct added successfully!")

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def view_products():
    print("\n--- Product List ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, price, quantity
            FROM products
            ORDER BY id
        """)

        products = cursor.fetchall()

        if not products:
            print("No products available.")
            return

        print("-" * 75)
        print(
            f"{'ID':<10}"
            f"{'Name':<20}"
            f"{'Category':<15}"
            f"{'Price':<10}"
            f"{'Quantity':<10}"
        )
        print("-" * 75)

        for product in products:
            print(
                f"{product['id']:<10}"
                f"{product['name']:<20}"
                f"{product['category']:<15}"
                f"{product['price']:<10.2f}"
                f"{product['quantity']:<10}"
            )

        print("-" * 75)

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def search_product():
    print("\n--- Search Product ---")

    search = input(
        "Enter Product ID or Name: "
    ).strip()

    if not search:
        print("Search value cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, price, quantity
            FROM products
            WHERE LOWER(id) = LOWER(?)
               OR LOWER(name) = LOWER(?)
        """, (
            search,
            search
        ))

        product = cursor.fetchone()

        if product:
            print("\nProduct Found!")
            print("ID       :", product["id"])
            print("Name     :", product["name"])
            print("Category :", product["category"])
            print("Price    :", product["price"])
            print("Quantity :", product["quantity"])

        else:
            print("Product not found.")

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def update_product():
    print("\n--- Update Product ---")

    product_id = input(
        "Enter Product ID to update: "
    ).strip()

    if not product_id:
        print("Product ID cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, price, quantity
            FROM products
            WHERE id = ?
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            print("Product not found.")
            return

        print("\nLeave a field empty to keep the existing value.")

        name = input(
            f"Enter Name [{product['name']}]: "
        ).strip()

        category = input(
            f"Enter Category [{product['category']}]: "
        ).strip()

        price_input = input(
            f"Enter Price [{product['price']}]: "
        ).strip()

        quantity_input = input(
            f"Enter Quantity [{product['quantity']}]: "
        ).strip()

        # Keep existing values if input is empty
        if not name:
            name = product["name"]

        if not category:
            category = product["category"]

        if price_input:
            try:
                price = float(price_input)

                if price <= 0:
                    print("Price must be greater than 0!")
                    return

            except ValueError:
                print("Invalid price!")
                return
        else:
            price = product["price"]

        if quantity_input:
            try:
                quantity = int(quantity_input)

                if quantity < 0:
                    print("Quantity cannot be negative!")
                    return

            except ValueError:
                print("Invalid quantity!")
                return
        else:
            quantity = product["quantity"]

        cursor.execute("""
            UPDATE products
            SET name = ?,
                category = ?,
                price = ?,
                quantity = ?
            WHERE id = ?
        """, (
            name,
            category,
            price,
            quantity,
            product_id
        ))

        connection.commit()

        print("\nProduct updated successfully!")

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def delete_product():
    print("\n--- Delete Product ---")

    product_id = input(
        "Enter Product ID to delete: "
    ).strip()

    if not product_id:
        print("Product ID cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, price
            FROM products
            WHERE id = ?
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            print("Product not found.")
            return

        print("\nProduct found:")
        print("Name :", product["name"])
        print("Price:", product["price"])

        confirmation = input(
            "Are you sure you want to delete this product? (y/n): "
        ).strip().lower()

        if confirmation == "y":

            cursor.execute(
                "DELETE FROM products WHERE id = ?",
                (product_id,)
            )

            connection.commit()

            print("\nProduct deleted successfully!")

        else:
            print("\nDelete operation cancelled.")

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def product_menu():

    while True:

        print("\n" + "=" * 40)
        print("       PRODUCT MANAGEMENT")
        print("=" * 40)

        print("1. Add Product")
        print("2. View Products")
        print("3. Search Product")
        print("4. Update Product")
        print("5. Delete Product")
        print("6. Back to Main Menu")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            add_product()

        elif choice == "2":
            view_products()

        elif choice == "3":
            search_product()

        elif choice == "4":
            update_product()

        elif choice == "5":
            delete_product()

        elif choice == "6":
            break

        else:
            print("Invalid choice! Please select 1-6.")