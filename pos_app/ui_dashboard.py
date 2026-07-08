from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, 
                             QFormLayout, QComboBox, QMessageBox, QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from database import get_session, Product, Category, Supplier, User

class DashboardWindow(QWidget):
    def __init__(self, user, on_logout):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.init_ui()

    def init_ui(self):
        # Main Layout (Horizontal: Sidebar on the right, content on the left)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Sidebar Container (Right side for RTL Arabic)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        self.sidebar.setStyleSheet("""
            QWidget#sidebar {
                background-color: #2c3e50;
                color: #ffffff;
            }
            QPushButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                border-radius: 0px;
                padding: 15px 20px;
                text-align: right;
                font-size: 15px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #1abc9c;
                font-weight: bold;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(10)
        
        # Shop Logo / Title
        shop_title = QLabel("المنزل السوري\nللسوبر ماركت")
        shop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shop_title.setStyleSheet("color: #1abc9c; font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        sidebar_layout.addWidget(shop_title)
        
        # Sidebar Menu Buttons
        self.btn_pos = QPushButton("🛒 نقطة البيع (الكاشير)")
        self.btn_pos.setCheckable(True)
        self.btn_pos.setChecked(True)
        self.btn_pos.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.btn_pos)
        
        self.btn_inventory = QPushButton("📦 إدارة الأصناف")
        self.btn_inventory.setCheckable(True)
        self.btn_inventory.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.btn_inventory)
        
        self.btn_suppliers = QPushButton("👥 إدارة الموردين")
        self.btn_suppliers.setCheckable(True)
        self.btn_suppliers.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.btn_suppliers)
        
        # Only admins can access reports and settings
        self.btn_reports = QPushButton("📈 التقارير والمبيعات")
        self.btn_reports.setCheckable(True)
        if self.user.role != 'admin':
            self.btn_reports.setEnabled(False)
            self.btn_reports.setToolTip("هذه الصفحة متاحة للمدير فقط")
            self.btn_reports.setStyleSheet("color: #7f8c8d;")
        self.btn_reports.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.btn_reports)
        
        self.btn_sync = QPushButton("🔄 المزامنة السحابية")
        self.btn_sync.setCheckable(True)
        self.btn_sync.clicked.connect(lambda: self.switch_page(4))
        sidebar_layout.addWidget(self.btn_sync)
        
        sidebar_layout.addStretch()
        
        # User Info & Logout
        user_info = QLabel(f"المستخدم: {self.user.username}\nالصلاحية: {self.user.role}")
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_info.setStyleSheet("color: #bdc3c7; font-size: 12px; margin-bottom: 10px;")
        sidebar_layout.addWidget(user_info)
        
        btn_logout = QPushButton("🚪 تسجيل الخروج")
        btn_logout.setObjectName("dangerButton")
        btn_logout.setStyleSheet("background-color: #c0392b; color: white; padding: 10px; margin: 10px;")
        btn_logout.clicked.connect(self.on_logout)
        sidebar_layout.addWidget(btn_logout)
        
        # Map buttons to a list to easily manage "checked" state
        self.menu_buttons = [self.btn_pos, self.btn_inventory, self.btn_suppliers, self.btn_reports, self.btn_sync]
        
        # 2. Main Content Stack (Left side)
        self.container = QStackedWidget()
        self.container.setStyleSheet("background-color: #f4f6f9; padding: 20px;")
        
        # Initialize Pages
        self.page_pos = POSPage(self.user)
        self.page_inventory = InventoryPage()
        self.page_suppliers = SuppliersPage()
        self.page_reports = ReportsPage()
        self.page_sync = SyncPage()
        
        self.container.addWidget(self.page_pos)
        self.container.addWidget(self.page_inventory)
        self.container.addWidget(self.page_suppliers)
        self.container.addWidget(self.page_reports)
        self.container.addWidget(self.page_sync)
        
        # Add to Layout
        main_layout.addWidget(self.container, 1) # content takes remaining space
        main_layout.addWidget(self.sidebar)       # sidebar on right
        
        self.setLayout(main_layout)

    def switch_page(self, index):
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)
        self.container.setCurrentIndex(index)
        
        # Refresh lists when switching pages
        if index == 1:
            self.page_inventory.load_products()
        elif index == 2:
            self.page_suppliers.load_suppliers()
        elif index == 3:
            self.page_reports.load_reports()


# ==================== PAGE 1: POS / CASHIER ====================
class POSPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = {} # {barcode: {name, price, qty}}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("🛒 نقطة البيع (الكاشير)")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Barcode input and Quick Search
        search_layout = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("امسح الباركود أو اكتب اسم الصنف هنا...")
        self.barcode_input.returnPressed.connect(self.add_by_barcode)
        
        btn_add = QPushButton("إضافة للفاتورة")
        btn_add.clicked.connect(self.add_by_barcode)
        
        search_layout.addWidget(self.barcode_input, 4)
        search_layout.addWidget(btn_add, 1)
        layout.addLayout(search_layout)
        
        # Cart Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "السعر", "الكمية", "الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Total Summary & Checkout Button
        summary_layout = QHBoxLayout()
        
        self.total_label = QLabel("الإجمالي: 0.00 ل.س")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60;")
        
        btn_pay = QPushButton("💳 دفع وإنهاء الفاتورة")
        btn_pay.setStyleSheet("background-color: #27ae60; font-size: 16px; padding: 12px 25px;")
        btn_pay.clicked.connect(self.checkout)
        
        btn_clear = QPushButton("🗑️ تفريغ السلة")
        btn_clear.setObjectName("dangerButton")
        btn_clear.setStyleSheet("background-color: #e74c3c; font-size: 16px; padding: 12px 25px;")
        btn_clear.clicked.connect(self.clear_cart)
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addStretch()
        summary_layout.addWidget(btn_clear)
        summary_layout.addWidget(btn_pay)
        
        layout.addLayout(summary_layout)
        self.setLayout(layout)

    def add_by_barcode(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        session = get_session()
        # Search by barcode or name
        product = session.query(Product).filter((Product.barcode == barcode) | (Product.name.like(f"%{barcode}%"))).first()
        session.close()
        
        if product:
            if product.quantity <= 0:
                QMessageBox.warning(self, "تنبيه", "هذا المنتج غير متوفر في المخزن (الكمية 0)")
                return
                
            if product.barcode in self.cart:
                if self.cart[product.barcode]['qty'] < product.quantity:
                    self.cart[product.barcode]['qty'] += 1
                else:
                    QMessageBox.warning(self, "تنبيه", "الكمية المطلوبة تتجاوز المتاح في المخزن")
            else:
                self.cart[product.barcode] = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'qty': 1
                }
            self.barcode_input.clear()
            self.update_cart_table()
        else:
            QMessageBox.critical(self, "خطأ", "المنتج غير موجود في قاعدة البيانات")
            self.barcode_input.clear()

    def update_cart_table(self):
        self.table.setRowCount(0)
        total = 0.0
        for barcode, item in self.cart.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            subtotal = item['price'] * item['qty']
            total += subtotal
            
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"{subtotal:.2f}"))
            
        self.total_label.setText(f"الإجمالي: {total:.2f} ل.س")

    def clear_cart(self):
        self.cart.clear()
        self.update_cart_table()

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "السلة فارغة", "الرجاء إضافة منتجات للفاتورة أولاً")
            return
            
        session = get_session()
        try:
            # Update product stocks
            for barcode, item in self.cart.items():
                prod = session.query(Product).filter_by(barcode=barcode).first()
                if prod:
                    prod.quantity -= item['qty']
            session.commit()
            QMessageBox.information(self, "نجاح العملية", "تم إصدار الفاتورة وحفظ البيع بنجاح!")
            self.clear_cart()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل إتمام العملية: {str(e)}")
        finally:
            session.close()


# ==================== PAGE 2: INVENTORY / PRODUCTS ====================
class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("📦 إدارة الأصناف")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Product Entry Form / Add Layout
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("الباركود")
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("اسم الصنف")
        self.input_price = QDoubleSpinBox()
        self.input_price.setMaximum(999999.0)
        self.input_price.setPrefix("السعر: ")
        self.input_qty = QSpinBox()
        self.input_qty.setMaximum(99999)
        self.input_qty.setPrefix("الكمية: ")
        
        btn_save = QPushButton("إضافة/تعديل صنف")
        btn_save.clicked.connect(self.save_product)
        btn_save.setStyleSheet("background-color: #1abc9c;")
        
        form_layout.addWidget(self.input_barcode)
        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_price)
        form_layout.addWidget(self.input_qty)
        form_layout.addWidget(btn_save)
        
        layout.addWidget(form_widget)
        
        # Product List Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "السعر", "الكمية المتاحة"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.load_row_to_form)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_products()

    def load_products(self):
        self.table.setRowCount(0)
        session = get_session()
        products = session.query(Product).all()
        session.close()
        
        for prod in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(prod.barcode))
            self.table.setItem(row, 1, QTableWidgetItem(prod.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{prod.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(prod.quantity)))

    def save_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price = self.input_price.value()
        qty = self.input_qty.value()
        
        if not barcode or not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء تعبئة حقل الباركود والاسم")
            return
            
        session = get_session()
        # Check if product exists to update it, else create
        prod = session.query(Product).filter_by(barcode=barcode).first()
        if prod:
            prod.name = name
            prod.price = price
            prod.quantity = qty
        else:
            prod = Product(barcode=barcode, name=name, price=price, quantity=qty)
            session.add(prod)
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "تم الحفظ", "تم حفظ الصنف بنجاح!")
        self.input_barcode.clear()
        self.input_name.clear()
        self.input_price.setValue(0)
        self.input_qty.setValue(0)
        self.load_products()

    def load_row_to_form(self):
        row = self.table.currentRow()
        if row >= 0:
            self.input_barcode.setText(self.table.item(row, 0).text())
            self.input_name.setText(self.table.item(row, 1).text())
            self.input_price.setValue(float(self.table.item(row, 2).text()))
            self.input_qty.setValue(int(self.table.item(row, 3).text()))


# ==================== PAGE 3: SUPPLIERS ====================
class SuppliersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("👥 إدارة الموردين")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Form
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("اسم المورد")
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("رقم الهاتف")
        self.input_balance = QDoubleSpinBox()
        self.input_balance.setMaximum(9999999.0)
        self.input_balance.setPrefix("الرصيد/الحساب: ")
        
        btn_add = QPushButton("إضافة مورد")
        btn_add.clicked.connect(self.save_supplier)
        btn_add.setStyleSheet("background-color: #4a90e2;")
        
        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_phone)
        form_layout.addWidget(self.input_balance)
        form_layout.addWidget(btn_add)
        
        layout.addWidget(form_widget)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["الاسم", "الهاتف", "الرصيد المستحق"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_suppliers()

    def load_suppliers(self):
        self.table.setRowCount(0)
        session = get_session()
        suppliers = session.query(Supplier).all()
        session.close()
        
        for sup in suppliers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(sup.name))
            self.table.setItem(row, 1, QTableWidgetItem(sup.phone if sup.phone else ""))
            self.table.setItem(row, 2, QTableWidgetItem(f"{sup.balance:.2f}"))

    def save_supplier(self):
        name = self.input_name.text().strip()
        phone = self.input_phone.text().strip()
        balance = self.input_balance.value()
        
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم المورد")
            return
            
        session = get_session()
        sup = session.query(Supplier).filter_by(name=name).first()
        if sup:
            sup.phone = phone
            sup.balance = balance
        else:
            sup = Supplier(name=name, phone=phone, balance=balance)
            session.add(sup)
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "تم الحفظ", "تم حفظ المورد بنجاح!")
        self.input_name.clear()
        self.input_phone.clear()
        self.input_balance.setValue(0.0)
        self.load_suppliers()


# ==================== PAGE 4: REPORTS & SALES (ADMIN ONLY) ====================
class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("📈 التقارير والمبيعات")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Small stats widgets
        stats_layout = QHBoxLayout()
        
        self.total_sales_card = QLabel("إجمالي المبيعات: 0.00 ل.س")
        self.total_sales_card.setStyleSheet("background-color: #2ecc71; color: white; font-size: 16px; padding: 20px; border-radius: 8px; font-weight: bold;")
        self.total_sales_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.total_products_card = QLabel("عدد الأصناف بالمخزن: 0")
        self.total_products_card.setStyleSheet("background-color: #3498db; color: white; font-size: 16px; padding: 20px; border-radius: 8px; font-weight: bold;")
        self.total_products_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        stats_layout.addWidget(self.total_sales_card)
        stats_layout.addWidget(self.total_products_card)
        layout.addLayout(stats_layout)
        
        # Recent sales placeholder or description
        info_label = QLabel("سجل المبيعات الأخيرة وجرد المخزون:")
        info_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["الصنف", "الكمية الحالية", "سعر البيع"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_reports()

    def load_reports(self):
        session = get_session()
        
        # Calculate total products in stock
        total_products = session.query(Product).count()
        self.total_products_card.setText(f"عدد الأصناف بالمخزن: {total_products}")
        
        # Load active inventory statuses
        products = session.query(Product).all()
        self.table.setRowCount(0)
        for prod in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(prod.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(prod.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(f"{prod.price:.2f}"))
            
        session.close()


# ==================== PAGE 5: SYNC PAGE ====================
class SyncPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("🔄 المزامنة السحابية (SQLite ↔ MySQL)")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        info = QLabel("قم بمزامنة المنتجات الحالية من وإلى استضافة Hostinger السحابية لربط الكاشير بالمتجر الإلكتروني.")
        info.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        self.status_label = QLabel("الحالة: جاهز للمزامنة")
        self.status_label.setStyleSheet("font-weight: bold; color: #34495e; font-size: 16px; margin-bottom: 20px;")
        layout.addWidget(self.status_label)

        btn_upload = QPushButton("⬆️ رفع المنتجات المحلية للمتجر السحابي")
        btn_upload.setStyleSheet("background-color: #3498db; color: white; padding: 15px; font-size: 15px; margin-bottom: 10px;")
        btn_upload.clicked.connect(self.upload_data)
        
        btn_download = QPushButton("⬇️ تحميل وتحديث المنتجات من المتجر السحابي")
        btn_download.setStyleSheet("background-color: #2ecc71; color: white; padding: 15px; font-size: 15px;")
        btn_download.clicked.connect(self.download_data)

        layout.addWidget(btn_upload)
        layout.addWidget(btn_download)
        layout.addStretch()
        self.setLayout(layout)

    def upload_data(self):
        self.status_label.setText("جاري رفع البيانات...")
        from sync import sync_products_to_online
        success, msg = sync_products_to_online()
        if success:
            QMessageBox.information(self, "نجاح المزامنة", msg)
            self.status_label.setText("الحالة: تم الرفع بنجاح")
        else:
            QMessageBox.warning(self, "فشل المزامنة", msg)
            self.status_label.setText("الحالة: فشل الرفع")

    def download_data(self):
        self.status_label.setText("جاري تحميل البيانات...")
        from sync import sync_products_from_online
        success, msg = sync_products_from_online()
        if success:
            QMessageBox.information(self, "نجاح المزامنة", msg)
            self.status_label.setText("الحالة: تم التحميل بنجاح")
        else:
            QMessageBox.warning(self, "فشل المزامنة", msg)
            self.status_label.setText("الحالة: فشل التحميل")
