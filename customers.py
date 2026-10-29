from database import get_connection


def add_customer():
    print("\n--- Add Customer ---")

    customer_id = input("Enter Customer ID: ").strip()

    if not customer_id:
        print("Customer ID cannot be empty!")
        return

    name = input("Enter Customer Name: ").strip()

    if not name:
        print("Customer name cannot be empty!")
        return

    phone = input("Enter Phone Number: ").strip()

    if not phone.isdigit() or len(phone) != 10:
        print("Invalid phone number!")
        print("Phone number must contain exactly 10 digits.")
        return

    email = input("Enter Email: ").strip()

    if not email:
        print("Email cannot be empty!")
        return

    if "@" not in email or "." not in email:
        print("Invalid email address!")
        return

    address = input("Enter Address: ").strip()

    if not address:
        print("Address cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check duplicate customer ID
        cursor.execute("""
            SELECT id
            FROM customers
            WHERE id = ?
        """, (customer_id,))

        if cursor.fetchone():
            print("Customer ID already exists!")
            return

        # Check duplicate phone number
        cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = ?
        """, (phone,))

        if cursor.fetchone():
            print("Phone number already exists!")
            return

        cursor.execute("""
            INSERT INTO customers
            (id, name, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
        """, (
            customer_id,
            name,
            phone,
            email,
            address
        ))

        connection.commit()

        print("\nCustomer added successfully!")

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def view_customers():
    print("\n--- Customer List ---")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, phone, email, address
            FROM customers
            ORDER BY id
        """)

        customers = cursor.fetchall()

        if not customers:
            print("No customers available.")
            return

        print("-" * 90)

        print(
            f"{'ID':<10}"
            f"{'Name':<20}"
            f"{'Phone':<15}"
            f"{'Email':<25}"
            f"{'Address':<20}"
        )

        print("-" * 90)

        for customer in customers:
            print(
                f"{customer['id']:<10}"
                f"{customer['name']:<20}"
                f"{customer['phone']:<15}"
                f"{customer['email']:<25}"
                f"{customer['address']:<20}"
            )

        print("-" * 90)

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def search_customer():
    print("\n--- Search Customer ---")

    search = input(
        "Enter Customer ID or Name: "
    ).strip()

    if not search:
        print("Search value cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                phone,
                email,
                address
            FROM customers
            WHERE LOWER(id) = LOWER(?)
               OR LOWER(name) = LOWER(?)
        """, (
            search,
            search
        ))

        customer = cursor.fetchone()

        if customer:
            print("\nCustomer Found!")

            print("ID      :", customer["id"])
            print("Name    :", customer["name"])
            print("Phone   :", customer["phone"])
            print("Email   :", customer["email"])
            print("Address :", customer["address"])

        else:
            print("Customer not found.")

    except Exception as error:
        print("Database error:", error)

    finally:
        connection.close()


def update_customer():
    print("\n--- Update Customer ---")

    customer_id = input(
        "Enter Customer ID to update: "
    ).strip()

    if not customer_id:
        print("Customer ID cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                phone,
                email,
                address
            FROM customers
            WHERE id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            return

        print(
            "\nLeave a field empty "
            "to keep the existing value."
        )

        name = input(
            f"Enter Name [{customer['name']}]: "
        ).strip()

        phone = input(
            f"Enter Phone [{customer['phone']}]: "
        ).strip()

        email = input(
            f"Enter Email [{customer['email']}]: "
        ).strip()

        address = input(
            f"Enter Address [{customer['address']}]: "
        ).strip()

        # Keep old values if input is empty
        if not name:
            name = customer["name"]

        if not phone:
            phone = customer["phone"]

        if not email:
            email = customer["email"]

        if not address:
            address = customer["address"]

        # Validate phone
        if not phone.isdigit() or len(phone) != 10:
            print("Invalid phone number!")
            print(
                "Phone number must contain exactly 10 digits."
            )
            return

        # Validate email
        if "@" not in email or "." not in email:
            print("Invalid email address!")
            return

        # Check if phone belongs to another customer
        cursor.execute("""
            SELECT id
            FROM customers
            WHERE phone = ?
              AND id != ?
        """, (
            phone,
            customer_id
        ))

        if cursor.fetchone():
            print(
                "This phone number is already "
                "used by another customer!"
            )
            return

        cursor.execute("""
            UPDATE customers
            SET
                name = ?,
                phone = ?,
                email = ?,
                address = ?
            WHERE id = ?
        """, (
            name,
            phone,
            email,
            address,
            customer_id
        ))

        connection.commit()

        print("\nCustomer updated successfully!")

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def delete_customer():
    print("\n--- Delete Customer ---")

    customer_id = input(
        "Enter Customer ID to delete: "
    ).strip()

    if not customer_id:
        print("Customer ID cannot be empty!")
        return

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                phone
            FROM customers
            WHERE id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:
            print("Customer not found.")
            return

        print("\nCustomer found:")
        print("Name  :", customer["name"])
        print("Phone :", customer["phone"])

        confirmation = input(
            "Are you sure you want to delete "
            "this customer? (y/n): "
        ).strip().lower()

        if confirmation == "y":

            cursor.execute("""
                DELETE FROM customers
                WHERE id = ?
            """, (customer_id,))

            connection.commit()

            print("\nCustomer deleted successfully!")

        else:
            print("\nDelete operation cancelled.")

    except Exception as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


def customer_menu():

    while True:

        print("\n" + "=" * 40)
        print("       CUSTOMER MANAGEMENT")
        print("=" * 40)

        print("1. Add Customer")
        print("2. View Customers")
        print("3. Search Customer")
        print("4. Update Customer")
        print("5. Delete Customer")
        print("6. Back to Main Menu")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            add_customer()

        elif choice == "2":
            view_customers()

        elif choice == "3":
            search_customer()

        elif choice == "4":
            update_customer()

        elif choice == "5":
            delete_customer()

        elif choice == "6":
            break

        else:
            print(
                "Invalid choice! Please select 1-6."
            )