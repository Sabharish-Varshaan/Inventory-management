
import sys
import sqlite3
import bcrypt
from datetime import datetime
from decimal import Decimal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTabWidget, QLabel, QLineEdit, 
                              QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
                              QTableWidget, QTableWidgetItem, QMessageBox,
                              QDialog, QFormLayout, QTextEdit, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class DatabaseManager:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.init_database()
        self.create_sample_data()

    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                sku_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                product_name TEXT NOT NULL,
                description TEXT,
                tax_rate REAL DEFAULT 0.0,
                price REAL NOT NULL,
                unit_of_measurement TEXT NOT NULL,
                stock_quantity REAL DEFAULT 0.0,
                product_image_path TEXT
            )
        """)

        # Suppliers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        # Goods receiving table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goods_receiving (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                supplier_id INTEGER,
                quantity REAL NOT NULL,
                rate_per_unit REAL NOT NULL,
                tax_amount REAL,
                total_amount REAL NOT NULL,
                date_received TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                received_by TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        """)

        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                customer_id INTEGER,
                quantity REAL NOT NULL,
                rate_per_unit REAL NOT NULL,
                tax_amount REAL,
                total_amount REAL NOT NULL,
                date_sold TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sold_by TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)

        conn.commit()
        conn.close()

    def create_sample_data(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Create users
            goods_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
            sales_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())

            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                          ("goods_operator", goods_password, "goods_receiving"))
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                          ("sales_operator", sales_password, "sales"))

        # Check if products already exist
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            # Sample products
            products = [
                ("ELC001", "SKU001", "Electronics", "Laptops", "Dell Laptop", "High-performance laptop", 18.0, 50000.0, "piece"),
                ("ELC002", "SKU002", "Electronics", "Accessories", "Wireless Mouse", "Optical wireless mouse", 12.0, 1500.0, "piece"),
                ("ELC003", "SKU003", "Electronics", "Monitors", "LED Monitor", "24-inch LED monitor", 18.0, 15000.0, "piece"),
                ("ELC004", "SKU004", "Electronics", "Accessories", "Keyboard", "Mechanical keyboard", 12.0, 3000.0, "piece"),
                ("ELC005", "SKU005", "Electronics", "Storage", "External HDD", "1TB external hard drive", 18.0, 5000.0, "piece")
            ]

            for barcode, sku, cat, subcat, name, desc, tax, price, unit in products:
                cursor.execute("""INSERT INTO products 
                                 (barcode, sku_id, category, subcategory, product_name, 
                                  description, tax_rate, price, unit_of_measurement) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (barcode, sku, cat, subcat, name, desc, tax, price, unit))

        # Check if suppliers already exist
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        if cursor.fetchone()[0] == 0:
            suppliers = [
                ("Tech Suppliers Ltd", "John Doe", "9876543210", "john@techsuppliers.com", "123 Tech Street"),
                ("Electronics Wholesale", "Jane Smith", "9876543211", "jane@ewholesale.com", "456 Electronics Ave"),
                ("Global Components", "Mike Johnson", "9876543212", "mike@globalcomp.com", "789 Component Road")
            ]

            for name, contact, phone, email, address in suppliers:
                cursor.execute("INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                              (name, contact, phone, email, address))

        # Check if customers already exist
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] == 0:
            customers = [
                ("ABC Corporation", "9876543220", "contact@abc.com", "123 Business Street"),
                ("XYZ Enterprises", "9876543221", "info@xyz.com", "456 Corporate Ave"),
                ("Individual Customer", "9876543222", "customer@email.com", "789 Customer Road")
            ]

            for name, phone, email, address in customers:
                cursor.execute("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                              (name, phone, email, address))

        conn.commit()
        conn.close()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System - Login")
        self.setFixedSize(300, 150)
        self.user_role = None
        self.username = None
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.authenticate)

        layout.addRow("Username:", self.username_edit)
        layout.addRow("Password:", self.password_edit)
        layout.addRow("", login_button)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            self.user_role = result[1]
            self.username = username
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

class InventoryMainWindow(QMainWindow):
    def __init__(self, user_role, username):
        super().__init__()
        self.user_role = user_role
        self.username = username
        self.setWindowTitle(f"Inventory Management System - {username}")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # User info
        user_label = QLabel(f"Logged in as: {self.username} ({self.user_role})")
        user_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(user_label)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Add tabs based on user role
        if self.user_role == "goods_receiving":
            self.add_goods_receiving_tab()
        elif self.user_role == "sales":
            self.add_sales_tab()

        # Common tabs
        self.add_product_master_tab()
        self.add_inventory_tab()

    def add_goods_receiving_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form
        form_layout = QFormLayout()

        # Product selection
        self.product_combo = QComboBox()
        self.load_products(self.product_combo)
        form_layout.addRow("Product:", self.product_combo)

        # Supplier selection
        self.supplier_combo = QComboBox()
        self.load_suppliers()
        form_layout.addRow("Supplier:", self.supplier_combo)

        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMaximum(9999.99)
        self.quantity_spin.setDecimals(2)
        form_layout.addRow("Quantity:", self.quantity_spin)

        # Unit of measurement (readonly, from product)
        self.unit_label = QLabel()
        form_layout.addRow("Unit:", self.unit_label)

        # Rate per unit
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setMaximum(999999.99)
        self.rate_spin.setDecimals(2)
        form_layout.addRow("Rate per Unit:", self.rate_spin)

        # Tax rate (from product)
        self.tax_rate_label = QLabel()
        form_layout.addRow("Tax Rate (%):", self.tax_rate_label)

        # Total amount (calculated)
        self.total_label = QLabel("0.00")
        form_layout.addRow("Total Amount:", self.total_label)

        # Connect signals for calculation
        self.quantity_spin.valueChanged.connect(self.calculate_goods_total)
        self.rate_spin.valueChanged.connect(self.calculate_goods_total)
        self.product_combo.currentTextChanged.connect(self.update_product_info)

        # Add button
        add_button = QPushButton("Add Goods Receiving Entry")
        add_button.clicked.connect(self.add_goods_receiving)

        layout.addLayout(form_layout)
        layout.addWidget(add_button)

        self.tab_widget.addTab(tab, "Goods Receiving")

        # Update initial product info
        self.update_product_info()

    def add_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Form
        form_layout = QFormLayout()

        # Product selection
        self.sales_product_combo = QComboBox()
        self.load_products(self.sales_product_combo)
        form_layout.addRow("Product:", self.sales_product_combo)

        # Customer selection
        self.customer_combo = QComboBox()
        self.load_customers()
        form_layout.addRow("Customer:", self.customer_combo)

        # Quantity
        self.sales_quantity_spin = QDoubleSpinBox()
        self.sales_quantity_spin.setMaximum(9999.99)
        self.sales_quantity_spin.setDecimals(2)
        form_layout.addRow("Quantity:", self.sales_quantity_spin)

        # Unit of measurement (readonly, from product)
        self.sales_unit_label = QLabel()
        form_layout.addRow("Unit:", self.sales_unit_label)

        # Rate per unit (from product price)
        self.sales_rate_label = QLabel()
        form_layout.addRow("Rate per Unit:", self.sales_rate_label)

        # Available stock
        self.stock_label = QLabel()
        form_layout.addRow("Available Stock:", self.stock_label)

        # Tax rate (from product)
        self.sales_tax_rate_label = QLabel()
        form_layout.addRow("Tax Rate (%):", self.sales_tax_rate_label)

        # Total amount (calculated)
        self.sales_total_label = QLabel("0.00")
        form_layout.addRow("Total Amount:", self.sales_total_label)

        # Connect signals for calculation
        self.sales_quantity_spin.valueChanged.connect(self.calculate_sales_total)
        self.sales_product_combo.currentTextChanged.connect(self.update_sales_product_info)

        # Add button
        add_button = QPushButton("Process Sale")
        add_button.clicked.connect(self.add_sale)

        layout.addLayout(form_layout)
        layout.addWidget(add_button)

        self.tab_widget.addTab(tab, "Sales Processing")

        # Update initial product info
        self.update_sales_product_info()

    def add_product_master_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Product table
        self.product_table = QTableWidget()
        self.load_product_table()
        layout.addWidget(self.product_table)

        self.tab_widget.addTab(tab, "Product Master List")

    def add_inventory_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Inventory table
        self.inventory_table = QTableWidget()
        self.load_inventory_table()
        layout.addWidget(self.inventory_table)

        self.tab_widget.addTab(tab, "Current Inventory")

    def load_products(self, combo):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, sku_id FROM products")
        products = cursor.fetchall()
        conn.close()

        combo.clear()
        for product_id, name, sku in products:
            combo.addItem(f"{name} ({sku})", product_id)

    def load_suppliers(self):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM suppliers")
        suppliers = cursor.fetchall()
        conn.close()

        self.supplier_combo.clear()
        for supplier_id, name in suppliers:
            self.supplier_combo.addItem(name, supplier_id)

    def load_customers(self):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM customers")
        customers = cursor.fetchall()
        conn.close()

        self.customer_combo.clear()
        for customer_id, name in customers:
            self.customer_combo.addItem(name, customer_id)

    def update_product_info(self):
        if not hasattr(self, 'product_combo'):
            return

        product_id = self.product_combo.currentData()
        if product_id:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT unit_of_measurement, tax_rate FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.unit_label.setText(result[0])
                self.tax_rate_label.setText(f"{result[1]}%")

        self.calculate_goods_total()

    def update_sales_product_info(self):
        if not hasattr(self, 'sales_product_combo'):
            return

        product_id = self.sales_product_combo.currentData()
        if product_id:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT unit_of_measurement, tax_rate, price, stock_quantity FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.sales_unit_label.setText(result[0])
                self.sales_tax_rate_label.setText(f"{result[1]}%")
                self.sales_rate_label.setText(f"₹{result[2]:.2f}")
                self.stock_label.setText(f"{result[3]:.2f} {result[0]}")

        self.calculate_sales_total()

    def calculate_goods_total(self):
        if not hasattr(self, 'quantity_spin'):
            return

        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()

        product_id = self.product_combo.currentData()
        tax_rate = 0.0

        if product_id:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT tax_rate FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                tax_rate = result[0] / 100.0

        subtotal = quantity * rate
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        self.total_label.setText(f"₹{total:.2f}")

    def calculate_sales_total(self):
        if not hasattr(self, 'sales_quantity_spin'):
            return

        quantity = self.sales_quantity_spin.value()

        product_id = self.sales_product_combo.currentData()
        if product_id:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT price, tax_rate FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                rate = result[0]
                tax_rate = result[1] / 100.0

                subtotal = quantity * rate
                tax_amount = subtotal * tax_rate
                total = subtotal + tax_amount

                self.sales_total_label.setText(f"₹{total:.2f}")

    def add_goods_receiving(self):
        product_id = self.product_combo.currentData()
        supplier_id = self.supplier_combo.currentData()
        quantity = self.quantity_spin.value()
        rate = self.rate_spin.value()

        if not all([product_id, supplier_id, quantity, rate]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        # Calculate totals
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT tax_rate FROM products WHERE id = ?", (product_id,))
        tax_rate = cursor.fetchone()[0] / 100.0

        subtotal = quantity * rate
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        # Insert goods receiving record
        cursor.execute("""INSERT INTO goods_receiving 
                         (product_id, supplier_id, quantity, rate_per_unit, tax_amount, total_amount, received_by)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (product_id, supplier_id, quantity, rate, tax_amount, total, self.username))

        # Update product stock
        cursor.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                      (quantity, product_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Goods receiving entry added successfully")

        # Reset form
        self.quantity_spin.setValue(0)
        self.rate_spin.setValue(0)

        # Refresh inventory table if visible
        if hasattr(self, 'inventory_table'):
            self.load_inventory_table()

    def add_sale(self):
        product_id = self.sales_product_combo.currentData()
        customer_id = self.customer_combo.currentData()
        quantity = self.sales_quantity_spin.value()

        if not all([product_id, customer_id, quantity]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        # Check stock availability
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT stock_quantity, price, tax_rate FROM products WHERE id = ?", (product_id,))
        result = cursor.fetchone()

        if not result:
            QMessageBox.warning(self, "Error", "Product not found")
            return

        current_stock, price, tax_rate = result

        if quantity > current_stock:
            QMessageBox.warning(self, "Error", f"Insufficient stock. Available: {current_stock}")
            return

        # Calculate totals
        tax_rate = tax_rate / 100.0
        subtotal = quantity * price
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        # Insert sales record
        cursor.execute("""INSERT INTO sales 
                         (product_id, customer_id, quantity, rate_per_unit, tax_amount, total_amount, sold_by)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (product_id, customer_id, quantity, price, tax_amount, total, self.username))

        # Update product stock
        cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                      (quantity, product_id))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Sale processed successfully")

        # Reset form
        self.sales_quantity_spin.setValue(0)

        # Refresh inventory table and sales product info
        if hasattr(self, 'inventory_table'):
            self.load_inventory_table()
        self.update_sales_product_info()

    def load_product_table(self):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT barcode, sku_id, category, subcategory, product_name, 
                         description, tax_rate, price, unit_of_measurement, stock_quantity
                         FROM products""")
        products = cursor.fetchall()
        conn.close()

        self.product_table.setRowCount(len(products))
        self.product_table.setColumnCount(10)
        self.product_table.setHorizontalHeaderLabels([
            "Barcode", "SKU ID", "Category", "Subcategory", "Product Name",
            "Description", "Tax Rate (%)", "Price (₹)", "Unit", "Stock"
        ])

        for row, product in enumerate(products):
            for col, value in enumerate(product):
                item = QTableWidgetItem(str(value))
                self.product_table.setItem(row, col, item)

        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def load_inventory_table(self):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT p.sku_id, p.product_name, p.category, p.subcategory,
                         p.stock_quantity, p.unit_of_measurement, p.price
                         FROM products p
                         ORDER BY p.product_name""")
        inventory = cursor.fetchall()
        conn.close()

        self.inventory_table.setRowCount(len(inventory))
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels([
            "SKU ID", "Product Name", "Category", "Subcategory",
            "Stock Quantity", "Unit", "Price (₹)"
        ])

        for row, item in enumerate(inventory):
            for col, value in enumerate(item):
                table_item = QTableWidgetItem(str(value))
                self.inventory_table.setItem(row, col, table_item)

        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

def main():
    app = QApplication(sys.argv)

    # Initialize database
    db_manager = DatabaseManager()

    # Show login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        # Show main window
        main_window = InventoryMainWindow(login_dialog.user_role, login_dialog.username)
        main_window.show()

        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
