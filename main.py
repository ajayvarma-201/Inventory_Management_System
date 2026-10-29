from products import product_menu
from inventory import inventory_menu
from customers import customer_menu
from billing import billing_menu
from reports import reports_menu
from analytics import analytics_menu


def main_menu():

    while True:

        print("\n" + "=" * 50)
        print("   SMART BILLING & INVENTORY MANAGEMENT")
        print("=" * 50)

        print("1. Product Management")
        print("2. Inventory Management")
        print("3. Customer Management")
        print("4. Billing")
        print("5. Sales Reports")
        print("6. Data Analytics")
        print("7. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            product_menu()

        elif choice == "2":
            inventory_menu()

        elif choice == "3":
            customer_menu()

        elif choice == "4":
            billing_menu()

        elif choice == "5":
            reports_menu()
            
        elif choice == "6":
            analytics_menu()

        elif choice == "7":
            print("\nThank you for using the system!")
            break

        else:
            print("\nInvalid choice! Please try again.")


main_menu()