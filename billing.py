from database import get_connection
from datetime import datetime


def find_customer(customer_id):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, phone, email, address
            FROM customers
            WHERE id = ?
        """, (customer_id,))

        return cursor.fetchone()

    except Exception as error:
        print("Database error:", error)
        return None

    finally:
        connection.close()


def find_product(product_id):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, price, quantity
            FROM products
            WHERE id = ?
        """, (product_id,))

        return cursor.fetchone()

    except Exception as error:
        print("Database error:", error)
        return None

    finally:
        connection.close()


def create_bill():

    print("\n" + "=" * 50)
    print("                 CREATE BILL")
    print("=" * 50)

    # CUSTOMER

    customer_id = input(
        "Enter Customer ID: "
    ).strip()

    if not customer_id:
        print("Customer ID cannot be empty!")
        return

    customer = find_customer(customer_id)

    if customer is None:
        print("Customer not found!")
        print("Please register the customer first.")
        return

    print("\nCustomer:", customer["name"])
    print("Phone   :", customer["phone"])

    # CART

    cart = []

    while True:

        product_id = input(
            "\nEnter Product ID (or 'done' to finish): "
        ).strip()

        if product_id.lower() == "done":

            if not cart:
                print(
                    "Cart is empty! "
                    "Add at least one product."
                )
                continue

            break

        if not product_id:
            print("Product ID cannot be empty!")
            continue

        product = find_product(product_id)

        if product is None:
            print("Product not found!")
            continue

        # Calculate quantity already added to cart

        cart_quantity = 0

        for item in cart:

            if item["product_id"] == product["id"]:
                cart_quantity = item["quantity"]
                break

        # Calculate remaining stock

        remaining_stock = (
            product["quantity"] - cart_quantity
        )

        print("\nProduct:", product["name"])
        print("Price  : ₹", product["price"])
        print("Stock  :", remaining_stock)

        if remaining_stock <= 0:
            print(
                "This product has no more "
                "stock available!"
            )
            continue

        # QUANTITY

        try:

            quantity = int(
                input("Enter Quantity: ")
            )

            if quantity <= 0:
                print(
                    "Quantity must be greater than 0!"
                )
                continue

        except ValueError:

            print(
                "Invalid quantity! "
                "Please enter a whole number."
            )
            continue

        # STOCK CHECK

        if quantity > remaining_stock:

            print(
                f"Insufficient stock! "
                f"Only {remaining_stock} available."
            )
            continue

        # CHECK IF PRODUCT ALREADY IN CART

        existing_item = None

        for item in cart:

            if item["product_id"] == product["id"]:
                existing_item = item
                break

        if existing_item:

            existing_item["quantity"] += quantity

            existing_item["amount"] = (
                existing_item["price"]
                * existing_item["quantity"]
            )

        else:

            amount = (
                product["price"] * quantity
            )

            item = {
                "product_id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "amount": amount
            }

            cart.append(item)

        print("Product added to cart!")

        another = input(
            "Add another product? (y/n): "
        ).strip().lower()

        if another == "n":
            break

        elif another != "y":

            print(
                "Invalid choice. "
                "Continuing with current cart."
            )

    # SUBTOTAL

    subtotal = 0

    for item in cart:
        subtotal += item["amount"]

    print("\n" + "-" * 50)
    print(
        "Subtotal: ₹",
        round(subtotal, 2)
    )
    print("-" * 50)

    # DISCOUNT

    while True:

        discount_input = input(
            "Enter Discount Percentage (0-100): "
        ).strip()

        try:

            discount_percent = float(
                discount_input
            )

            if (
                discount_percent < 0
                or discount_percent > 100
            ):

                print(
                    "Discount must be between 0 and 100."
                )
                continue

            break

        except ValueError:

            print(
                "Invalid discount! "
                "Please enter a number."
            )

    discount_amount = (
        subtotal * discount_percent / 100
    )

    amount_after_discount = (
        subtotal - discount_amount
    )

    # GST

    gst_percent = 5

    # Calculate GST on the original subtotal so equal discount and GST rates offset.
    gst_amount = (
        subtotal
        * gst_percent
        / 100
    )

    grand_total = (
        amount_after_discount
        + gst_amount
    )

    # BILL NUMBER

    bill_number = (
        "B"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        )
    )

    bill_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # SAVE TO DATABASE

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # Double-check stock before completing the bill
        for item in cart:

            cursor.execute("""
                SELECT quantity
                FROM products
                WHERE id = ?
            """, (item["product_id"],))

            current_product = cursor.fetchone()

            if current_product is None:

                print(
                    f"Product {item['product_id']} "
                    f"was not found."
                )

                connection.rollback()
                return

            if item["quantity"] > current_product["quantity"]:

                print(
                    f"Insufficient stock for "
                    f"{item['product_id']}."
                )

                connection.rollback()
                return

        # Insert sale

        cursor.execute("""
            INSERT INTO sales
            (
                bill_number,
                date,
                customer_id,
                customer_name,
                subtotal,
                discount_percent,
                discount_amount,
                gst_percent,
                gst_amount,
                grand_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_number,
            bill_date,
            customer["id"],
            customer["name"],
            round(subtotal, 2),
            discount_percent,
            round(discount_amount, 2),
            gst_percent,
            round(gst_amount, 2),
            round(grand_total, 2)
        ))

        # Insert sale items and update inventory

        for item in cart:

            cursor.execute("""
                INSERT INTO sale_items
                (
                    bill_number,
                    product_id,
                    product_name,
                    price,
                    quantity,
                    amount
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                bill_number,
                item["product_id"],
                item["name"],
                item["price"],
                item["quantity"],
                round(item["amount"], 2)
            ))

            cursor.execute("""
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
            """, (
                item["quantity"],
                item["product_id"]
            ))

        # Commit everything together

        connection.commit()

        print("\nBill saved successfully!")

        # Create dictionary for printing
        sale = {
            "bill_number": bill_number,
            "date": bill_date,
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "items": cart,
            "subtotal": round(subtotal, 2),
            "discount_percent": discount_percent,
            "discount_amount": round(
                discount_amount, 2
            ),
            "gst_percent": gst_percent,
            "gst_amount": round(
                gst_amount, 2
            ),
            "grand_total": round(
                grand_total, 2
            )
        }

        print_bill(sale)

    except Exception as error:

        connection.rollback()

        print(
            "\nDatabase error:",
            error
        )

    finally:

        connection.close()


def print_bill(sale):

    print("\n")
    print("=" * 60)
    print("                 SMART BILL")
    print("=" * 60)

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

    print(
        "Customer ID :",
        sale["customer_id"]
    )

    print("-" * 60)

    print(
        f"{'Product':<20}"
        f"{'Price':<10}"
        f"{'Qty':<8}"
        f"{'Amount':<12}"
    )

    print("-" * 60)

    for item in sale["items"]:

        print(
            f"{item['name']:<20}"
            f"{item['price']:<10.2f}"
            f"{item['quantity']:<8}"
            f"{item['amount']:<12.2f}"
        )

    print("-" * 60)

    print(
        f"Subtotal          : "
        f"₹{sale['subtotal']:.2f}"
    )

    print(
        f"Discount "
        f"({sale['discount_percent']:.1f}%)"
        f"   : "
        f"₹{sale['discount_amount']:.2f}"
    )

    print(
        f"GST "
        f"({sale['gst_percent']}%)"
        f"             : "
        f"₹{sale['gst_amount']:.2f}"
    )

    print("-" * 60)

    print(
        f"GRAND TOTAL       : "
        f"₹{sale['grand_total']:.2f}"
    )

    print("=" * 60)
    print(
        "             Thank You! Visit Again!"
    )
    print("=" * 60)


def billing_menu():

    while True:

        print("\n" + "=" * 40)
        print("          BILLING SYSTEM")
        print("=" * 40)

        print("1. Create New Bill")
        print("2. Back to Main Menu")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":

            create_bill()

        elif choice == "2":

            break

        else:

            print(
                "Invalid choice! Please select 1 or 2."
            )