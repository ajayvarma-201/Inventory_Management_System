import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from database import get_connection
from datetime import date, timedelta

st.set_page_config(
    page_title="Smart Billing & Inventory",
    page_icon="🛒",
    layout="wide"
)

# PRINT CSS

st.markdown(
    """
    <style>

    @media print {

        body * {
            visibility: hidden !important;
        }

        .st-key-invoice_container,
        .st-key-invoice_container * {
            visibility: visible !important;
        }

        .st-key-invoice_container {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 10px !important;
            height: auto !important;
            min-height: 0 !important;
            overflow: visible !important;
            break-after: avoid !important;
            page-break-after: avoid !important;
        }

        section[data-testid="stSidebar"] {
            display: none !important;
        }

        header {
            display: none !important;
        }

        button {
            display: none !important;
        }

        input,
        textarea,
        select {
            display: none !important;
        }

        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            min-height: 0 !important;
            height: auto !important;
        }

        .st-key-invoice_container * {
            break-before: auto !important;
            break-after: avoid !important;
        }

        @page {
            size: A4 portrait;
            margin: 10mm;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)

# SIDEBAR

st.sidebar.title("🛒 Smart Billing")

st.sidebar.markdown("---")

if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"


def sidebar_button(label):

    if st.sidebar.button(
        label,
        key=f"menu_{label}",
        use_container_width=True
    ):
        st.session_state.menu = label
        st.rerun()


sidebar_button("🏠 Dashboard")
sidebar_button("📦 Products")
sidebar_button("📊 Inventory")
sidebar_button("👥 Customers")
sidebar_button("🧾 Billing")
sidebar_button("📈 Reports")
sidebar_button("📊 Analytics")

menu = st.session_state.menu

st.sidebar.markdown("---")

st.sidebar.info(
    "Smart Billing & Inventory Management System"
)

# SIDEBAR STYLING

st.markdown(
    """
    <style>

    /* Sidebar menu buttons */
    section[data-testid="stSidebar"] button {
        width: 100%;
        min-height: 45px;
        border-radius: 8px;
        margin-bottom: 6px;
        font-size: 16px;
        font-weight: 500;
        text-align: left;
        padding-left: 15px;
    }

    /* Hover effect */
    section[data-testid="stSidebar"] button:hover {
        border: 1px solid #ff4b4b;
        transform: translateX(3px);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# DASHBOARD

if menu == "🏠 Dashboard":

    st.title("🛒 Smart Billing & Inventory Management System")

    st.write(
        "Welcome to the Smart Billing and Inventory Management System"
    )

    # DASHBOARD SUMMARY

    connection = get_connection()

    try:

        # Total Products
        total_products = connection.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        # Total Customers
        total_customers = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        # Total Bills
        total_bills = connection.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

        # Total Revenue
        total_revenue = connection.execute(
            """
            SELECT COALESCE(SUM(grand_total), 0)
            FROM sales
            """
        ).fetchone()[0]

        # Today's date
        today = date.today().strftime("%Y-%m-%d")

        # Today's Revenue
        today_revenue = connection.execute(
            """
            SELECT COALESCE(SUM(grand_total), 0)
            FROM sales
            WHERE date LIKE ?
            """,
            (today + "%",)
        ).fetchone()[0]

        # Low Stock Products
        low_stock_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM products
            WHERE quantity <= 5
            """
        ).fetchone()[0]

        # SUMMARY CARDS

        st.divider()

        st.subheader("📊 Business Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📦 Total Products",
                total_products
            )

        with col2:
            st.metric(
                "👥 Total Customers",
                total_customers
            )

        with col3:
            st.metric(
                "🧾 Total Bills",
                total_bills
            )

        with col4:
            st.metric(
                "💰 Total Revenue",
                f"₹{total_revenue:,.2f}"
            )

        # TODAY'S SUMMARY

        st.subheader("📅 Today's Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "💵 Today's Revenue",
                f"₹{today_revenue:,.2f}"
            )

        with col2:
            st.metric(
                "🧾 Today's Bills",
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM sales
                    WHERE date LIKE ?
                    """,
                    (today + "%",)
                ).fetchone()[0]
            )

        with col3:
            st.metric(
                "⚠️ Low Stock Products",
                low_stock_count
            )

    finally:
        connection.close()

    st.divider()

    st.subheader("📊 System Modules")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📦 Product Management")
        st.write("Manage products and their details.")

    with col2:
        st.info("🧾 Billing")
        st.write("Create bills and manage sales.")

    with col3:
        st.info("📊 Data Analytics")
        st.write("Analyze sales and product demand.")

    st.divider()


# PRODUCTS

elif menu == "📦 Products":

    st.title("📦 Product Management")

    st.subheader("Add New Product")

    col1, col2 = st.columns(2)

    with col1:
        product_id = st.text_input("Product ID")
        product_name = st.text_input("Product Name")
        category = st.text_input("Category")

    with col2:
        price = st.number_input(
            "Price (₹)",
            min_value=0.0,
            step=0.01
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0,
            step=1
        )

    if st.button("➕ Add Product"):

        if not product_id or not product_name or not category:
            st.error("Please fill all required fields.")

        elif price <= 0:
            st.error("Price must be greater than 0.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO products
                    (id, name, category, price, quantity)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    product_id,
                    product_name,
                    category,
                    price,
                    quantity
                ))

                connection.commit()

                st.success(
                    f"Product '{product_name}' added successfully!"
                )

            except Exception as error:

                connection.rollback()

                st.error(f"Error: {error}")

            finally:
                connection.close()

    st.divider()

    st.subheader("📋 Product List")

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, price, quantity
            FROM products
            ORDER BY id
        """)

        products = cursor.fetchall()

        if products:

            for product in products:

                col1, col2, col3, col4, col5 = st.columns(5)

                col1.write(product["id"])
                col2.write(product["name"])
                col3.write(product["category"])
                col4.write(f"₹{product['price']:.2f}")
                col5.write(product["quantity"])

        else:

            st.info("No products available.")

    except Exception as error:

        st.error(f"Database error: {error}")

    finally:

        connection.close()
        
    st.divider()

    st.subheader("🔍 Search Product")

    search_id = st.text_input("Enter Product ID to search")

    if st.button("Search Product"):

        if not search_id:
            st.warning("Please enter a Product ID.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    SELECT id, name, category, price, quantity
                    FROM products
                    WHERE id = ?
                """, (search_id,))

                product = cursor.fetchone()

                if product:

                    st.success("Product found!")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Product ID:**", product["id"])
                        st.write("**Product Name:**", product["name"])
                        st.write("**Category:**", product["category"])

                    with col2:
                        st.write(
                            "**Price:**",
                            f"₹{product['price']:.2f}"
                        )
                        st.write(
                            "**Quantity:**",
                            product["quantity"]
                        )

                else:

                    st.warning("Product not found.")

            except Exception as error:

                st.error(f"Database error: {error}")

            finally:

                connection.close()
                
    st.divider()

    st.subheader("✏️ Update Product")

    update_id = st.text_input("Enter Product ID to update")

    if st.button("Load Product"):

        if not update_id:
            st.warning("Please enter a Product ID.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    SELECT id, name, category, price, quantity
                    FROM products
                    WHERE id = ?
                """, (update_id,))

                product = cursor.fetchone()

                if product:

                    st.session_state.update_product = dict(product)
                    st.success("Product loaded successfully!")

                else:

                    st.warning("Product not found.")

            except Exception as error:

                st.error(f"Database error: {error}")

            finally:

                connection.close()


    if "update_product" in st.session_state:

        product = st.session_state.update_product

        new_name = st.text_input(
            "Product Name",
            value=product["name"],
            key="update_name"
        )

        new_category = st.text_input(
            "Category",
            value=product["category"],
            key="update_category"
        )

        new_price = st.number_input(
            "Price (₹)",
            min_value=0.01,
            value=float(product["price"]),
            step=0.01,
            key="update_price"
        )

        new_quantity = st.number_input(
            "Quantity",
            min_value=0,
            value=int(product["quantity"]),
            step=1,
            key="update_quantity"
        )

        if st.button("💾 Update Product"):

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    UPDATE products
                    SET name = ?,
                        category = ?,
                        price = ?,
                        quantity = ?
                    WHERE id = ?
                """, (
                    new_name,
                    new_category,
                    new_price,
                    new_quantity,
                    update_id
                ))

                connection.commit()

                st.success("Product updated successfully!")

                del st.session_state.update_product

            except Exception as error:

                connection.rollback()

                st.error(f"Database error: {error}")

            finally:

                connection.close()
    st.divider()

    st.subheader("🗑️ Delete Product")

    delete_id = st.text_input("Enter Product ID to delete")

    if st.button("🗑️ Delete Product"):

        if not delete_id:

            st.warning("Please enter a Product ID.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                # Check if product exists
                cursor.execute("""
                    SELECT name
                    FROM products
                    WHERE id = ?
                """, (delete_id,))

                product = cursor.fetchone()

                if not product:

                    st.warning("Product not found.")

                else:

                    cursor.execute("""
                        DELETE FROM products
                        WHERE id = ?
                    """, (delete_id,))

                    connection.commit()

                    st.success(
                        f"Product '{product['name']}' deleted successfully!"
                    )

            except Exception as error:

                connection.rollback()

                st.error(f"Database error: {error}")

            finally:

                connection.close()


# INVENTORY

elif menu == "📊 Inventory":

    st.title("📊 Inventory Management")

    st.subheader("📦 Current Inventory")

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, price, quantity
            FROM products
            ORDER BY id
        """)

        products = cursor.fetchall()

        if products:

            st.write(
                f"**Total Products: {len(products)}**"
            )

            st.divider()

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.write("**Product ID**")
            col2.write("**Product**")
            col3.write("**Category**")
            col4.write("**Price**")
            col5.write("**Stock**")

            for product in products:

                col1, col2, col3, col4, col5 = st.columns(5)

                col1.write(product["id"])
                col2.write(product["name"])
                col3.write(product["category"])
                col4.write(f"₹{product['price']:.2f}")
                col5.write(product["quantity"])

        else:

            st.info("No products available.")

    except Exception as error:

        st.error(f"Database error: {error}")

    finally:

        connection.close()
        
    st.divider()

    st.subheader("📥 Add Stock")

    add_stock_id = st.text_input(
        "Enter Product ID",
        key="add_stock_id"
    )

    add_quantity = st.number_input(
        "Quantity to Add",
        min_value=1,
        step=1,
        key="add_quantity"
    )

    if st.button("📥 Add Stock"):

        if not add_stock_id:

            st.warning("Please enter a Product ID.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                # Check product
                cursor.execute("""
                    SELECT name, quantity
                    FROM products
                    WHERE id = ?
                """, (add_stock_id,))

                product = cursor.fetchone()

                if not product:

                    st.warning("Product not found.")

                else:

                    new_quantity = (
                        product["quantity"] + add_quantity
                    )

                    cursor.execute("""
                        UPDATE products
                        SET quantity = ?
                        WHERE id = ?
                    """, (
                        new_quantity,
                        add_stock_id
                    ))

                    connection.commit()

                    st.success(
                        f"Added {add_quantity} units to "
                        f"'{product['name']}'. "
                        f"New stock: {new_quantity}"
                    )

            except Exception as error:

                connection.rollback()

                st.error(f"Database error: {error}")

            finally:

                connection.close()
                
    st.divider()

    st.subheader("📤 Remove Stock")

    remove_stock_id = st.text_input(
        "Enter Product ID",
        key="remove_stock_id"
    )

    remove_quantity = st.number_input(
        "Quantity to Remove",
        min_value=1,
        step=1,
        key="remove_quantity"
    )

    if st.button("📤 Remove Stock"):

        if not remove_stock_id:

            st.warning("Please enter a Product ID.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                # Check product
                cursor.execute("""
                    SELECT name, quantity
                    FROM products
                    WHERE id = ?
                """, (remove_stock_id,))

                product = cursor.fetchone()

                if not product:

                    st.warning("Product not found.")

                elif remove_quantity > product["quantity"]:

                    st.error(
                        f"Cannot remove {remove_quantity} units. "
                        f"Only {product['quantity']} units are available."
                    )

                else:

                    new_quantity = (
                        product["quantity"] - remove_quantity
                    )

                    cursor.execute("""
                        UPDATE products
                        SET quantity = ?
                        WHERE id = ?
                    """, (
                        new_quantity,
                        remove_stock_id
                    ))

                    connection.commit()

                    st.success(
                        f"Removed {remove_quantity} units from "
                        f"'{product['name']}'. "
                        f"Remaining stock: {new_quantity}"
                    )

            except Exception as error:

                connection.rollback()

                st.error(f"Database error: {error}")

            finally:

                connection.close()
                
    st.divider()

    st.subheader("⚠️ Low Stock Alert")

    LOW_STOCK_LIMIT = 10

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, quantity
            FROM products
            WHERE quantity <= ?
            ORDER BY quantity ASC
        """, (LOW_STOCK_LIMIT,))

        low_stock_products = cursor.fetchall()

        if low_stock_products:

            st.warning(
                f"{len(low_stock_products)} product(s) "
                f"have low stock."
            )

            for product in low_stock_products:

                col1, col2, col3, col4 = st.columns(4)

                col1.write(product["id"])
                col2.write(product["name"])
                col3.write(product["category"])
                col4.write(
                    f"⚠️ {product['quantity']} units"
                )

        else:

            st.success("✅ No low-stock products.")

    except Exception as error:

        st.error(f"Database error: {error}")

    finally:

        connection.close()
        
    st.divider()

    st.subheader("💰 Inventory Summary")

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_products,
                COALESCE(SUM(quantity), 0) AS total_units,
                COALESCE(SUM(price * quantity), 0) AS inventory_value
            FROM products
        """)

        summary = cursor.fetchone()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "📦 Total Products",
                summary["total_products"]
            )

        with col2:
            st.metric(
                "📊 Total Units",
                summary["total_units"]
            )

        with col3:
            st.metric(
                "💰 Inventory Value",
                f"₹{summary['inventory_value']:.2f}"
            )

    except Exception as error:

        st.error(f"Database error: {error}")

    finally:

        connection.close()


# CUSTOMERS

elif menu == "👥 Customers":

    st.title("👥 Customer Management")

    st.subheader("➕ Add New Customer")

    col1, col2 = st.columns(2)

    with col1:

        customer_id = st.text_input(
            "Customer ID"
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        phone = st.text_input(
            "Phone Number"
        )

    with col2:

        email = st.text_input(
            "Email"
        )

        address = st.text_area(
            "Address"
        )

    if st.button("➕ Add Customer"):

        if not customer_id or not customer_name:
            st.error(
                "Customer ID and Name are required."
            )

        elif not phone.isdigit() or len(phone) != 10:
            st.error(
                "Phone number must contain exactly 10 digits."
            )

        elif "@" not in email or "." not in email:
            st.error(
                "Please enter a valid email address."
            )

        elif not address:
            st.error(
                "Address is required."
            )

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO customers
                    (id, name, phone, email, address)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    customer_id,
                    customer_name,
                    phone,
                    email,
                    address
                ))

                connection.commit()

                st.success(
                    f"Customer '{customer_name}' "
                    "added successfully!"
                )

            except Exception as error:

                connection.rollback()

                st.error(
                    f"Error: {error}"
                )

            finally:

                connection.close()
                
    st.divider()

    st.subheader("📋 Customer List")

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, phone, email, address
            FROM customers
            ORDER BY id
        """)

        customers = cursor.fetchall()

        if customers:

            st.write(
                f"**Total Customers: {len(customers)}**"
            )

            for customer in customers:

                with st.container(border=True):

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            "**Customer ID:**",
                            customer["id"]
                        )

                        st.write(
                            "**Name:**",
                            customer["name"]
                        )

                        st.write(
                            "**Phone:**",
                            customer["phone"]
                        )

                    with col2:

                        st.write(
                            "**Email:**",
                            customer["email"]
                        )

                        st.write(
                            "**Address:**",
                            customer["address"]
                        )

        else:

            st.info("No customers available.")

    except Exception as error:

        st.error(
            f"Database error: {error}"
        )

    finally:

        connection.close()
        
    st.divider()

    st.subheader("🔍 Search Customer")

    search_customer = st.text_input(
        "Enter Customer ID or Name"
    )

    if st.button("🔍 Search Customer"):

        if not search_customer.strip():

            st.warning(
                "Please enter a Customer ID or Name."
            )

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                search_value = search_customer.strip()

                cursor.execute("""
                    SELECT id, name, phone, email, address
                    FROM customers
                    WHERE id = ?
                       OR name LIKE ?
                    ORDER BY id
                """, (
                    search_value,
                    f"%{search_value}%"
                ))

                customers = cursor.fetchall()

                if customers:

                    st.success(
                        f"{len(customers)} customer(s) found!"
                    )

                    for customer in customers:

                        with st.container(border=True):

                            col1, col2 = st.columns(2)

                            with col1:

                                st.write(
                                    "**Customer ID:**",
                                    customer["id"]
                                )

                                st.write(
                                    "**Name:**",
                                    customer["name"]
                                )

                                st.write(
                                    "**Phone:**",
                                    customer["phone"]
                                )

                            with col2:

                                st.write(
                                    "**Email:**",
                                    customer["email"]
                                )

                                st.write(
                                    "**Address:**",
                                    customer["address"]
                                )

                else:

                    st.warning(
                        "No customer found."
                    )

            except Exception as error:

                st.error(
                    f"Database error: {error}"
                )

            finally:

                connection.close()
                
    st.divider()

    st.subheader("✏️ Update Customer")

    update_customer_id = st.text_input(
        "Enter Customer ID to update",
        key="update_customer_id"
    )

    if st.button("Load Customer"):

        if not update_customer_id:

            st.warning(
                "Please enter a Customer ID."
            )

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    SELECT id, name, phone, email, address
                    FROM customers
                    WHERE id = ?
                """, (update_customer_id,))

                customer = cursor.fetchone()

                if customer:

                    st.session_state.update_customer = dict(customer)

                    st.success(
                        "Customer loaded successfully!"
                    )

                else:

                    st.warning(
                        "Customer not found."
                    )

            except Exception as error:

                st.error(
                    f"Database error: {error}"
                )

            finally:

                connection.close()


    if "update_customer" in st.session_state:

        customer = st.session_state.update_customer

        new_name = st.text_input(
            "Customer Name",
            value=customer["name"],
            key="update_customer_name"
        )

        new_phone = st.text_input(
            "Phone Number",
            value=customer["phone"],
            key="update_customer_phone"
        )

        new_email = st.text_input(
            "Email",
            value=customer["email"],
            key="update_customer_email"
        )

        new_address = st.text_area(
            "Address",
            value=customer["address"],
            key="update_customer_address"
        )

        if st.button("💾 Update Customer"):

            if not new_name.strip():

                st.error(
                    "Customer name is required."
                )

            elif not new_phone.isdigit() or len(new_phone) != 10:

                st.error(
                    "Phone number must contain exactly 10 digits."
                )

            elif "@" not in new_email or "." not in new_email:

                st.error(
                    "Please enter a valid email address."
                )

            elif not new_address.strip():

                st.error(
                    "Address is required."
                )

            else:

                connection = get_connection()

                try:

                    cursor = connection.cursor()

                    cursor.execute("""
                        UPDATE customers
                        SET name = ?,
                            phone = ?,
                            email = ?,
                            address = ?
                        WHERE id = ?
                    """, (
                        new_name,
                        new_phone,
                        new_email,
                        new_address,
                        customer["id"]
                    ))

                    connection.commit()

                    st.success(
                        "Customer updated successfully!"
                    )

                    del st.session_state.update_customer

                except Exception as error:

                    connection.rollback()

                    st.error(
                        f"Database error: {error}"
                    )

                finally:

                    connection.close()
                    
    st.divider()

    st.subheader("🗑️ Delete Customer")

    delete_customer_id = st.text_input(
        "Enter Customer ID to delete",
        key="delete_customer_id"
    )

    if st.button("🗑️ Delete Customer"):

        if not delete_customer_id.strip():
            st.warning("Please enter a Customer ID.")

        else:
            connection = get_connection()

            try:
                cursor = connection.cursor()

                # Check whether customer exists
                cursor.execute("""
                    SELECT id, name
                    FROM customers
                    WHERE id = ?
                """, (delete_customer_id,))

                customer = cursor.fetchone()

                if not customer:
                    st.warning("Customer not found.")

                else:
                    # Check whether customer has sales records
                    cursor.execute("""
                        SELECT COUNT(*) AS total_sales
                        FROM sales
                        WHERE customer_id = ?
                    """, (delete_customer_id,))

                    sales_count = cursor.fetchone()["total_sales"]

                    if sales_count > 0:

                        st.error(
                            "Cannot delete this customer because "
                            "sales records already exist for this customer."
                        )

                    else:
                        cursor.execute("""
                            DELETE FROM customers
                            WHERE id = ?
                        """, (delete_customer_id,))

                        connection.commit()

                        st.success(
                            f"Customer '{customer['name']}' deleted successfully!"
                        )

            except Exception as error:
                connection.rollback()
                st.error(f"Database error: {error}")

            finally:
                connection.close()
    

# BILLING

elif menu == "🧾 Billing":

    st.title("🧾 Billing")

    # CUSTOMER SELECTION

    st.subheader("👤 Select Customer")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, phone
            FROM customers
            ORDER BY name
        """)

        customers = cursor.fetchall()

    except Exception as error:
        st.error(f"Database error: {error}")
        customers = []

    finally:
        connection.close()

    if not customers:

        st.warning(
            "No customers available. Please add a customer first."
        )

    else:

        customer_options = {
            f"{customer['id']} - {customer['name']} "
            f"({customer['phone']})": customer["id"]
            for customer in customers
        }

        selected_customer = st.selectbox(
            "Select Customer",
            list(customer_options.keys())
        )

        selected_customer_id = customer_options[selected_customer]

        # PRODUCT SELECTION

        st.divider()
        st.subheader("📦 Add Products")

        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, name, price, quantity
                FROM products
                WHERE quantity > 0
                ORDER BY name
            """)

            products = cursor.fetchall()

        except Exception as error:
            st.error(f"Database error: {error}")
            products = []

        finally:
            connection.close()

        if not products:

            st.warning("No products available in stock.")

        else:

            product_options = {
                f"{product['id']} - {product['name']} "
                f"(₹{product['price']:.2f}, "
                f"Stock: {product['quantity']})":
                product["id"]
                for product in products
            }

            selected_product = st.selectbox(
                "Select Product",
                list(product_options.keys())
            )

            selected_product_id = product_options[selected_product]

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=1,
                step=1
            )

            # ADD TO CART

            if st.button("➕ Add to Cart"):

                connection = get_connection()

                try:
                    cursor = connection.cursor()

                    cursor.execute("""
                        SELECT id, name, price, quantity
                        FROM products
                        WHERE id = ?
                    """, (selected_product_id,))

                    product = cursor.fetchone()

                    if not product:

                        st.error("Product not found.")

                    elif quantity > product["quantity"]:

                        st.error(
                            f"Only {product['quantity']} units available."
                        )

                    else:

                        if "cart" not in st.session_state:
                            st.session_state.cart = []

                        # Check if product already exists in cart
                        existing_product = None

                        for item in st.session_state.cart:

                            if item["product_id"] == product["id"]:
                                existing_product = item
                                break

                        if existing_product:

                            new_quantity = (
                                existing_product["quantity"] + quantity
                            )

                            if new_quantity > product["quantity"]:

                                st.error(
                                    f"Only {product['quantity']} units "
                                    f"available."
                                )

                            else:

                                existing_product["quantity"] = new_quantity

                                existing_product["amount"] = (
                                    new_quantity * product["price"]
                                )

                                st.success(
                                    "Product quantity updated in cart."
                                )

                        else:

                            st.session_state.cart.append({
                                "product_id": product["id"],
                                "product_name": product["name"],
                                "price": product["price"],
                                "quantity": quantity,
                                "amount": quantity * product["price"]
                            })

                            st.success(
                                f"{product['name']} added to cart."
                            )

                except Exception as error:

                    st.error(f"Database error: {error}")

                finally:
                    connection.close()

        # SHOPPING CART

        st.divider()
        st.subheader("🛒 Shopping Cart")

        if "cart" not in st.session_state:
            st.session_state.cart = []

        if st.session_state.cart:

            subtotal = 0

            # Display cart items
            for index, item in enumerate(
                st.session_state.cart
            ):

                with st.container(border=True):

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.write(
                            f"**{item['product_name']}**"
                        )

                    with col2:
                        st.write(
                            f"Price: ₹{item['price']:.2f}"
                        )

                    with col3:
                        st.write(
                            f"Quantity: {item['quantity']}"
                        )

                    with col4:
                        st.write(
                            f"Amount: ₹{item['amount']:.2f}"
                        )

                    if st.button(
                        "❌ Remove",
                        key=f"remove_cart_{index}"
                    ):

                        st.session_state.cart.pop(index)

                        st.rerun()

                subtotal += item["amount"]

            # SUBTOTAL

            st.markdown("---")

            st.metric(
                "Subtotal",
                f"₹{subtotal:,.2f}"
            )

            # DISCOUNT & GST

            st.divider()
            st.subheader("💰 Bill Calculation")

            col1, col2 = st.columns(2)

            with col1:

                discount_percent = st.number_input(
                    "Discount (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    format="%.2f",
                    key="discount_percent"
                )

            with col2:

                gst_percent = st.number_input(
                    "GST (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    step=1.0,
                    format="%.2f",
                    key="gst_percent"
                )

            # CALCULATE DISCOUNT

            discount_amount = (
                subtotal * discount_percent / 100
            )

            # Amount after discount
            amount_after_discount = (
                subtotal - discount_amount
            )

            # CALCULATE GST

            gst_amount = (
                amount_after_discount * gst_percent / 100
            )

            # GRAND TOTAL

            grand_total = (
                amount_after_discount + gst_amount
            )

            # BILL SUMMARY

            st.subheader("🧾 Bill Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Subtotal",
                    f"₹{subtotal:,.2f}"
                )

            with col2:

                st.metric(
                    "Discount",
                    f"₹{discount_amount:,.2f}"
                )

            with col3:

                st.metric(
                    "GST",
                    f"₹{gst_amount:,.2f}"
                )

            with col4:

                st.metric(
                    "Grand Total",
                    f"₹{grand_total:,.2f}"
                )
                
            # GENERATE BILL

            st.divider()

            if st.button("🧾 Generate Bill", type="primary"):

                connection = get_connection()

                try:
                    cursor = connection.cursor()

                    # Generate unique bill number
                    from datetime import datetime

                    bill_number = (
                        "B" +
                        datetime.now().strftime("%Y%m%d%H%M%S%f")
                    )

                    bill_date = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Verify stock before saving bill

                    stock_valid = True

                    for item in st.session_state.cart:

                        cursor.execute("""
                            SELECT quantity
                            FROM products
                            WHERE id = ?
                        """, (item["product_id"],))

                        product = cursor.fetchone()

                        if not product:

                            st.error(
                                f"Product {item['product_id']} no longer exists."
                            )

                            stock_valid = False
                            break

                        if item["quantity"] > product["quantity"]:

                            st.error(
                                f"Insufficient stock for {item['product_name']}. "
                                f"Available: {product['quantity']}"
                            )

                            stock_valid = False
                            break

                    if stock_valid:

                        # Insert Sale

                        cursor.execute("""
                            INSERT INTO sales (
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
                            SELECT
                                ?,
                                ?,
                                id,
                                name,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?,
                                ?
                            FROM customers
                            WHERE id = ?
                        """, (
                            bill_number,
                            bill_date,
                            subtotal,
                            discount_percent,
                            discount_amount,
                            gst_percent,
                            gst_amount,
                            grand_total,
                            selected_customer_id
                        ))

                        # Insert Sale Items

                        for item in st.session_state.cart:

                            cursor.execute("""
                                INSERT INTO sale_items (
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
                                item["product_name"],
                                item["price"],
                                item["quantity"],
                                item["amount"]
                            ))

                            # Update Product Stock

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

                        # Save bill number for display
                        st.session_state.last_bill_number = bill_number
                        st.session_state.last_bill_total = grand_total

                        # Clear cart
                        st.session_state.cart = []

                        st.success(
                            f"✅ Bill {bill_number} generated successfully!"
                        )

                except Exception as error:

                    connection.rollback()

                    st.error(
                        f"Unable to generate bill: {error}"
                    )

                finally:

                    connection.close()


            # INVOICE DISPLAY

            if "last_bill_number" in st.session_state:

                st.divider()

                st.subheader("🧾 Generated Invoice")

                bill_number = st.session_state.last_bill_number

                connection = get_connection()

                try:
                    cursor = connection.cursor()

                    # Get bill information
                    cursor.execute("""
                        SELECT
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
                        FROM sales
                        WHERE bill_number = ?
                    """, (bill_number,))

                    bill = cursor.fetchone()

                    # Get bill items
                    cursor.execute("""
                        SELECT
                            product_name,
                            price,
                            quantity,
                            amount
                        FROM sale_items
                        WHERE bill_number = ?
                    """, (bill_number,))

                    bill_items = cursor.fetchall()

                except Exception as error:

                    st.error(f"Database error: {error}")

                    bill = None
                    bill_items = []

                finally:

                    connection.close()

                if bill:

                    # PRINTABLE INVOICE CONTAINER

                    with st.container(key="invoice_container"):

                        st.markdown(
                            """
                            <div style="text-align:center;">
                                <h1>🛒 SMART BILLING SYSTEM</h1>
                                <h3>INVOICE</h3>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.divider()

                        # BILL DETAILS

                        col1, col2 = st.columns(2)

                        with col1:

                            st.write(
                                f"**Bill Number:** {bill['bill_number']}"
                            )

                            st.write(
                                f"**Date:** {bill['date']}"
                            )

                        with col2:

                            st.write(
                                f"**Customer:** {bill['customer_name']}"
                            )

                            st.write(
                                f"**Customer ID:** {bill['customer_id']}"
                            )

                        st.divider()

                        # PURCHASED ITEMS

                        st.subheader("📦 Purchased Items")

                        for item in bill_items:

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.write(
                                    f"**{item['product_name']}**"
                                )

                            with col2:
                                st.write(
                                    f"₹{item['price']:.2f}"
                                )

                            with col3:
                                st.write(
                                    f"{item['quantity']}"
                                )

                            with col4:
                                st.write(
                                    f"₹{item['amount']:.2f}"
                                )

                        st.divider()

                        # TOTALS

                        col1, col2 = st.columns(2)

                        with col2:

                            st.write(
                                f"**Subtotal:** "
                                f"₹{bill['subtotal']:,.2f}"
                            )

                            st.write(
                                f"**Discount "
                                f"({bill['discount_percent']:.2f}%):** "
                                f"- ₹{bill['discount_amount']:,.2f}"
                            )

                            st.write(
                                f"**GST "
                                f"({bill['gst_percent']:.2f}%):** "
                                f"₹{bill['gst_amount']:,.2f}"
                            )

                            st.markdown("---")

                            st.markdown(
                                f"### **Grand Total: "
                                f"₹{bill['grand_total']:,.2f}**"
                            )

                    # SUCCESS MESSAGE

                    st.success(
                        f"✅ Invoice {bill['bill_number']} generated successfully!"
                    )

                    # PRINT INVOICE

                    st.divider()

                    st.subheader("🖨️ Invoice Options")

                    components.html(
                        """
                        <button
                            onclick="window.parent.print()"
                            style="
                                background-color:#ff4b4b;
                                color:white;
                                border:none;
                                padding:12px 24px;
                                border-radius:8px;
                                font-size:16px;
                                font-weight:bold;
                                cursor:pointer;
                            ">
                                🖨️ Print Invoice
                        </button>
                        """,
                        height=60
                    )
            
        else:

            st.info("Your cart is empty.")


# REPORTS

elif menu == "📈 Reports":

    st.title("📈 Sales Reports")

    st.write(
        "View and analyze sales records from the billing system."
    )

    st.divider()

    # DATE FILTER

    st.subheader("📅 Select Date Range")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "From Date",
            value=date.today()
        )

    with col2:
        end_date = st.date_input(
            "To Date",
            value=date.today()
        )

    if start_date > end_date:

        st.error(
            "From Date cannot be greater than To Date."
        )

    else:

        # Convert dates to strings
        start_datetime = (
            start_date.strftime("%Y-%m-%d") + " 00:00:00"
        )

        end_datetime = (
            (end_date + timedelta(days=1))
            .strftime("%Y-%m-%d") + " 00:00:00"
        )

        connection = get_connection()

        try:

            cursor = connection.cursor()

            # GET SALES

            cursor.execute("""
                SELECT
                    bill_number,
                    date,
                    customer_id,
                    customer_name,
                    subtotal,
                    discount_amount,
                    gst_amount,
                    grand_total
                FROM sales
                WHERE date >= ?
                AND date < ?
                ORDER BY date DESC
            """, (
                start_datetime,
                end_datetime
            ))

            sales = cursor.fetchall()

            # SALES SUMMARY

            st.subheader("📊 Sales Summary")

            total_bills = len(sales)

            total_revenue = sum(
                sale["grand_total"]
                for sale in sales
            )

            total_subtotal = sum(
                sale["subtotal"]
                for sale in sales
            )

            total_discount = sum(
                sale["discount_amount"]
                for sale in sales
            )

            total_gst = sum(
                sale["gst_amount"]
                for sale in sales
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "🧾 Total Bills",
                    total_bills
                )

            with col2:
                st.metric(
                    "💰 Total Revenue",
                    f"₹{total_revenue:,.2f}"
                )

            with col3:
                st.metric(
                    "🎁 Total Discount",
                    f"₹{total_discount:,.2f}"
                )

            with col4:
                st.metric(
                    "🧾 Total GST",
                    f"₹{total_gst:,.2f}"
                )

            st.divider()

            # SALES RECORDS

            st.subheader("📋 Sales Records")

            if sales:

                header1, header2, header3, header4, header5 = st.columns(5)

                header1.write("**Bill Number**")
                header2.write("**Date**")
                header3.write("**Customer**")
                header4.write("**Subtotal**")
                header5.write("**Grand Total**")

                for sale in sales:

                    col1, col2, col3, col4, col5 = st.columns(5)

                    col1.write(
                        sale["bill_number"]
                    )

                    col2.write(
                        sale["date"]
                    )

                    col3.write(
                        sale["customer_name"]
                    )

                    col4.write(
                        f"₹{sale['subtotal']:,.2f}"
                    )

                    col5.write(
                        f"₹{sale['grand_total']:,.2f}"
                    )

            else:

                st.info(
                    "No sales found for the selected date range."
                )

            st.divider()
            
            # DOWNLOAD SALES REPORT

            if sales:

                import csv
                import io

                st.subheader("📥 Download Report")

                output = io.StringIO()

                writer = csv.writer(output)

                writer.writerow([
                    "Bill Number",
                    "Date",
                    "Customer ID",
                    "Customer Name",
                    "Subtotal",
                    "Discount",
                    "GST",
                    "Grand Total"
                ])

                for sale in sales:

                    writer.writerow([
                        sale["bill_number"],
                        sale["date"],
                        sale["customer_id"],
                        sale["customer_name"],
                        sale["subtotal"],
                        sale["discount_amount"],
                        sale["gst_amount"],
                        sale["grand_total"]
                    ])

                st.download_button(
                    label="📥 Download Sales Report",
                    data=output.getvalue(),
                    file_name="sales_report.csv",
                    mime="text/csv"
                )

            # BILL DETAILS

            st.subheader("🧾 Bill Details")

            if sales:

                bill_options = [
                    sale["bill_number"]
                    for sale in sales
                ]

                selected_bill = st.selectbox(
                    "Select a Bill",
                    bill_options
                )

                selected_sale = None

                for sale in sales:

                    if sale["bill_number"] == selected_bill:
                        selected_sale = sale
                        break

                if selected_sale:

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"**Bill Number:** "
                            f"{selected_sale['bill_number']}"
                        )

                        st.write(
                            f"**Customer ID:** "
                            f"{selected_sale['customer_id']}"
                        )

                        st.write(
                            f"**Customer Name:** "
                            f"{selected_sale['customer_name']}"
                        )

                        st.write(
                            f"**Date:** "
                            f"{selected_sale['date']}"
                        )

                    with col2:

                        st.write(
                            f"**Subtotal:** "
                            f"₹{selected_sale['subtotal']:,.2f}"
                        )

                        st.write(
                            f"**Discount:** "
                            f"₹{selected_sale['discount_amount']:,.2f}"
                        )

                        st.write(
                            f"**GST:** "
                            f"₹{selected_sale['gst_amount']:,.2f}"
                        )

                        st.write(
                            f"**Grand Total:** "
                            f"₹{selected_sale['grand_total']:,.2f}"
                        )

                    # BILL ITEMS

                    st.subheader("📦 Purchased Items")

                    cursor.execute("""
                        SELECT
                            product_name,
                            price,
                            quantity,
                            amount
                        FROM sale_items
                        WHERE bill_number = ?
                    """, (selected_bill,))

                    bill_items = cursor.fetchall()

                    if bill_items:

                        col1, col2, col3, col4 = st.columns(4)

                        col1.write("**Product**")
                        col2.write("**Price**")
                        col3.write("**Quantity**")
                        col4.write("**Amount**")

                        for item in bill_items:

                            col1, col2, col3, col4 = st.columns(4)

                            col1.write(
                                item["product_name"]
                            )

                            col2.write(
                                f"₹{item['price']:,.2f}"
                            )

                            col3.write(
                                item["quantity"]
                            )

                            col4.write(
                                f"₹{item['amount']:,.2f}"
                            )

        except Exception as error:

            st.error(
                f"Database error: {error}"
            )

        finally:

            connection.close()


# ANALYTICS

elif menu == "📊 Analytics":

    st.title("📊 Data Analytics")

    st.write(
        "Analyze sales, products, customers, and business performance."
    )

    st.divider()
    
    connection = get_connection()
    
    try:
    
        cursor = connection.cursor()

        # 1. BEST-SELLING PRODUCTS

        st.subheader("🏆 Best-Selling Products")


        cursor.execute("""
            SELECT
                product_name,
                SUM(quantity) AS total_quantity,
                SUM(amount) AS total_revenue
            FROM sale_items
            GROUP BY product_id, product_name
            ORDER BY total_quantity DESC
        """)

        products = cursor.fetchall()

        if products:

            # Convert database result to DataFrame
            product_data = pd.DataFrame(
                [
                    {
                        "Product": product["product_name"],
                        "Quantity Sold": product["total_quantity"],
                        "Revenue": product["total_revenue"]
                    }
                    for product in products
                ]
            )

            # TOP PRODUCT

            top_product = products[0]

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "🥇 Best-Selling Product",
                    top_product["product_name"]
                )

            with col2:

                st.metric(
                    "📦 Units Sold",
                    top_product["total_quantity"]
                )

            with col3:

                st.metric(
                    "💰 Revenue",
                    f"₹{top_product['total_revenue']:,.2f}"
                )

            st.divider()

            # PRODUCT SALES TABLE

            st.write("### 📋 Product Sales Summary")

            st.dataframe(
                product_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # QUANTITY SOLD CHART

            st.write("### 📊 Quantity Sold by Product")

            quantity_chart = product_data[
                ["Product", "Quantity Sold"]
            ].set_index("Product")

            st.bar_chart(
                quantity_chart
            )

            st.divider()

            # REVENUE BY PRODUCT

            st.write("### 💰 Revenue by Product")

            revenue_chart = product_data[
                ["Product", "Revenue"]
            ].set_index("Product")

            st.bar_chart(
                revenue_chart
            )

        else:

            st.info(
                "No sales data available for analysis."
            )

        # 2. REVENUE ANALYSIS

        st.subheader("💰 Revenue Analysis")

        cursor.execute("""
            SELECT
                date,
                grand_total,
                discount_amount,
                gst_amount
            FROM sales
            ORDER BY date
        """)

        revenue_records = cursor.fetchall()

        if revenue_records:

            revenue_data = pd.DataFrame(
                [
                    {
                        "Date": record["date"],
                        "Revenue": record["grand_total"],
                        "Discount": record["discount_amount"],
                        "GST": record["gst_amount"]
                    }
                    for record in revenue_records
                ]
            )

            # REVENUE SUMMARY

            total_revenue = revenue_data["Revenue"].sum()

            average_bill = revenue_data["Revenue"].mean()

            highest_bill = revenue_data["Revenue"].max()

            total_discount = revenue_data["Discount"].sum()

            total_gst = revenue_data["GST"].sum()


            # First row
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "💰 Total Revenue",
                    f"₹{total_revenue:,.2f}"
                )

            with col2:
                st.metric(
                    "📊 Average Bill",
                    f"₹{average_bill:,.2f}"
                )

            with col3:
                st.metric(
                    "🔝 Highest Bill",
                    f"₹{highest_bill:,.2f}"
                )


            # Second row
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "🎁 Total Discount",
                    f"₹{total_discount:,.2f}"
                )

            with col2:
                st.metric(
                    "🧾 Total GST",
                    f"₹{total_gst:,.2f}"
                )

            # REVENUE TABLE

            st.write("### 📋 Revenue Details")

            st.dataframe(
                revenue_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # REVENUE CHART

            st.write("### 📈 Revenue by Sale")

            revenue_chart = revenue_data[
                ["Date", "Revenue"]
            ].set_index("Date")

            st.line_chart(
                revenue_chart
            )

        else:

            st.info(
                "No sales data available for revenue analysis."
            )

        # 3. CUSTOMER PURCHASE ANALYSIS

        st.subheader("👥 Customer Purchase Analysis")

        cursor.execute("""
            SELECT
                customer_id,
                customer_name,
                COUNT(bill_number) AS total_bills,
                SUM(grand_total) AS total_spent
            FROM sales
            GROUP BY customer_id, customer_name
            ORDER BY total_spent DESC
        """)

        customer_records = cursor.fetchall()

        if customer_records:

            customer_data = pd.DataFrame(
                [
                    {
                        "Customer ID": record["customer_id"],
                        "Customer Name": record["customer_name"],
                        "Total Bills": record["total_bills"],
                        "Total Spent": record["total_spent"]
                    }
                    for record in customer_records
                ]
            )

            # CUSTOMER SUMMARY

            total_customers = len(customer_records)

            top_customer = customer_records[0]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "👥 Customers Purchased",
                    total_customers
                )

            with col2:
                st.metric(
                    "🥇 Top Customer",
                    top_customer["customer_name"]
                )

            with col3:
                st.metric(
                    "💰 Top Customer Spending",
                    f"₹{top_customer['total_spent']:,.2f}"
                )

            st.divider()

            # CUSTOMER PURCHASE TABLE

            st.write("### 📋 Customer Purchase Summary")

            st.dataframe(
                customer_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # PURCHASES BY CUSTOMER

            st.write("### 📊 Number of Bills by Customer")

            bills_chart = customer_data[
                ["Customer Name", "Total Bills"]
            ].set_index("Customer Name")

            st.bar_chart(
                bills_chart
            )

            st.divider()

            # REVENUE BY CUSTOMER

            st.write("### 💰 Spending by Customer")

            spending_chart = customer_data[
                ["Customer Name", "Total Spent"]
            ].set_index("Customer Name")

            st.bar_chart(
                spending_chart
            )

        else:

            st.info(
                "No customer purchase data available."
            )
            
        # 4. MONTHLY SALES ANALYSIS

        st.subheader("📅 Monthly Sales Analysis")

        cursor.execute("""
            SELECT
                strftime('%Y-%m', date) AS month,
                COUNT(bill_number) AS total_bills,
                SUM(grand_total) AS total_revenue
            FROM sales
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
        """)

        monthly_records = cursor.fetchall()

        if monthly_records:

            monthly_data = pd.DataFrame(
                [
                    {
                        "Month": record["month"],
                        "Total Bills": record["total_bills"],
                        "Total Revenue": record["total_revenue"]
                    }
                    for record in monthly_records
                ]
            )

            # MONTHLY SUMMARY

            total_months = len(monthly_records)

            highest_month = max(
                monthly_records,
                key=lambda x: x["total_revenue"]
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "📅 Months with Sales",
                    total_months
                )

            with col2:
                st.metric(
                    "🧾 Total Bills",
                    sum(
                        record["total_bills"]
                        for record in monthly_records
                    )
                )

            with col3:
                st.metric(
                    "🏆 Best Sales Month",
                    highest_month["month"]
                )

            st.divider()

            # MONTHLY SALES TABLE

            st.write("### 📋 Monthly Sales Summary")

            st.dataframe(
                monthly_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # MONTHLY REVENUE CHART

            st.write("### 💰 Monthly Revenue")

            monthly_revenue_chart = monthly_data[
                ["Month", "Total Revenue"]
            ].set_index("Month")

            st.bar_chart(
                monthly_revenue_chart
            )

            st.divider()

            # MONTHLY BILL COUNT CHART

            st.write("### 🧾 Monthly Bill Count")

            monthly_bill_chart = monthly_data[
                ["Month", "Total Bills"]
            ].set_index("Month")

            st.line_chart(
                monthly_bill_chart
            )

        else:

            st.info(
                "No monthly sales data available."
            )
            
        # 5. PRODUCT DEMAND ANALYSIS

        st.subheader("📦 Product Demand Analysis")

        cursor.execute("""
            SELECT
                product_id,
                product_name,
                SUM(quantity) AS total_quantity,
                COUNT(DISTINCT bill_number) AS number_of_bills
            FROM sale_items
            GROUP BY product_id, product_name
            ORDER BY total_quantity DESC
        """)

        demand_records = cursor.fetchall()

        if demand_records:

            demand_data = pd.DataFrame(
                [
                    {
                        "Product ID": record["product_id"],
                        "Product": record["product_name"],
                        "Quantity Sold": record["total_quantity"],
                        "Number of Bills": record["number_of_bills"]
                    }
                    for record in demand_records
                ]
            )

            # DEMAND SUMMARY

            highest_demand = demand_records[0]

            lowest_demand = demand_records[-1]

            total_products = len(demand_records)

            total_units = sum(
                record["total_quantity"]
                for record in demand_records
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "📦 Products Sold",
                    total_products
                )

            with col2:
                st.metric(
                    "🔥 High-Demand Product",
                    highest_demand["product_name"]
                )

            with col3:
                st.metric(
                    "📊 Total Units Sold",
                    total_units
                )

            st.divider()

            # DEMAND TABLE

            st.write("### 📋 Product Demand Summary")

            st.dataframe(
                demand_data,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # DEMAND CHART

            st.write("### 📊 Product Demand")

            demand_chart = demand_data[
                ["Product", "Quantity Sold"]
            ].set_index("Product")

            st.bar_chart(
                demand_chart
            )

            st.divider()

            # PURCHASE FREQUENCY

            st.write("### 🧾 Purchase Frequency")

            frequency_chart = demand_data[
                ["Product", "Number of Bills"]
            ].set_index("Product")

            st.bar_chart(
                frequency_chart
            )

            st.divider()

            # DEMAND INSIGHT

            st.write("### 💡 Demand Insight")

            st.success(
                f"🔥 **{highest_demand['product_name']}** "
                f"is currently the highest-demand product "
                f"with **{highest_demand['total_quantity']} units sold**."
            )

            if highest_demand["product_id"] != lowest_demand["product_id"]:

                st.info(
                    f"📉 **{lowest_demand['product_name']}** "
                    f"has the lowest demand with "
                    f"**{lowest_demand['total_quantity']} units sold**."
                )

        else:

            st.info(
                "No product demand data available."
            )
        

    except Exception as error:
        st.error(f"Database error: {error}")

    finally:
        connection.close()