from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, 
                             QFormLayout, QComboBox, QMessageBox, QDoubleSpinBox, QSpinBox,
                             QGroupBox, QCheckBox, QDialog, QListWidget, QListWidgetItem, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QShortcut, QKeySequence
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
        self.sidebar.setFixedWidth(70)
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
                padding: 15px 5px;
                text-align: center;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #1abc9c;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(15)
        
        # Shop Logo / Title
        shop_title = QLabel("🏡")
        shop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shop_title.setStyleSheet("font-size: 32px; margin-bottom: 20px;")
        shop_title.setToolTip(f"المنزل السوري - المستخدم: {self.user.username} ({self.user.role})")
        sidebar_layout.addWidget(shop_title)
        
        # Sidebar Menu Buttons
        self.btn_pos = QPushButton("🛒")
        self.btn_pos.setToolTip("نقطة البيع (الكاشير)")
        self.btn_pos.setCheckable(True)
        self.btn_pos.setChecked(True)
        self.btn_pos.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.btn_pos)
        
        self.btn_inventory = QPushButton("📦")
        self.btn_inventory.setToolTip("إدارة الأصناف")
        self.btn_inventory.setCheckable(True)
        self.btn_inventory.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.btn_inventory)
        
        self.btn_suppliers = QPushButton("👥")
        self.btn_suppliers.setToolTip("إدارة الموردين")
        self.btn_suppliers.setCheckable(True)
        self.btn_suppliers.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.btn_suppliers)
        
        # Only admins can access reports and settings
        self.btn_reports = QPushButton("📈")
        self.btn_reports.setToolTip("التقارير والمبيعات")
        self.btn_reports.setCheckable(True)
        if self.user.role != 'admin':
            self.btn_reports.setEnabled(False)
            self.btn_reports.setToolTip("هذه الصفحة متاحة للمدير فقط")
            self.btn_reports.setStyleSheet("color: #7f8c8d; font-size: 24px;")
        self.btn_reports.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.btn_reports)
        
        self.btn_sync = QPushButton("🔄")
        self.btn_sync.setToolTip("المزامنة السحابية")
        self.btn_sync.setCheckable(True)
        self.btn_sync.clicked.connect(lambda: self.switch_page(4))
        sidebar_layout.addWidget(self.btn_sync)
        
        sidebar_layout.addStretch()
        
        btn_logout = QPushButton("🚪")
        btn_logout.setToolTip("تسجيل الخروج")
        btn_logout.setObjectName("dangerButton")
        btn_logout.setStyleSheet("background-color: #c0392b; color: white; padding: 10px; margin: 5px;")
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


# ==================== DIALOGS FOR POS ====================
class ProductSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("بحث عن المنتجات (F1 للبحث)")
        self.resize(600, 450)
        self.selected_barcode = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("اكتب اسم المنتج أو الباركود للبحث...")
        self.search_input.textChanged.connect(self.search_products)
        layout.addWidget(self.search_input)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "السعر", "النوع"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.accept_selection)
        layout.addWidget(self.table)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.search_products()
        self.search_input.setFocus()

    def search_products(self):
        self.table.setRowCount(0)
        query = self.search_input.text().strip()
        
        session = get_session()
        products = session.query(Product).filter(
            (Product.name.like(f"%{query}%")) | (Product.barcode.like(f"%{query}%"))
        ).all()
        session.close()
        
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p.barcode))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{p.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem("بالوزن" if p.is_weighted else "بالقطعة"))

    def accept_selection(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.selected_barcode = self.table.item(selected_row, 0).text()
            self.accept()
        else:
            self.reject()


class RecallDialog(QDialog):
    def __init__(self, invoices, parent=None):
        super().__init__(parent)
        self.setWindowTitle("استدعاء فاتورة معلقة")
        self.resize(550, 350)
        self.invoices = invoices
        self.selected_invoice = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        for i, inv in enumerate(self.invoices):
            cust_name = inv['customer_name'] if inv['customer_name'] else "عميل سفري"
            desc = f"فاتورة معلقة #{i+1} | العميل: {cust_name} | الإجمالي: {inv['total']:.2f} ل.س | الأصناف: {len(inv['cart'])}"
            item = QListWidgetItem(desc)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.list_widget.addItem(item)
            
        self.list_widget.doubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept_selection(self):
        selected = self.list_widget.selectedItems()
        if selected:
            idx = selected[0].data(Qt.ItemDataRole.UserRole)
            self.selected_invoice = self.invoices[idx]
            self.invoices.pop(idx) # إزالة من قائمة المعلقات بعد استدعائها
            self.accept()
        else:
            self.reject()


# ==================== PAGE 1: POS / CASHIER ====================
class POSPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = {} # {barcode: {id, name, price, qty, is_weighted}}
        self.held_invoices = []
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        # تصميم عمودي بالكامل
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # 1. القسم العلوي (الباركود والأزرار الفرعية)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("امسح الباركود أو اكتب اسم الصنف هنا... (F1 للبحث)")
        self.barcode_input.setMinimumHeight(40)
        self.barcode_input.returnPressed.connect(self.add_by_barcode)
        
        btn_search = QPushButton("🔍 بحث متقدم (F1)")
        btn_search.setStyleSheet("background-color: #34495e; padding: 10px 15px;")
        btn_search.clicked.connect(self.open_search_dialog)
        
        btn_hold = QPushButton("⏸️ تعليق الفاتورة (F3)")
        btn_hold.setStyleSheet("background-color: #e67e22; padding: 10px 15px;")
        btn_hold.clicked.connect(self.hold_invoice)
        
        btn_recall = QPushButton("▶️ استدعاء المعلقات (F4)")
        btn_recall.setStyleSheet("background-color: #3498db; padding: 10px 15px;")
        btn_recall.clicked.connect(self.recall_invoice)
        
        btn_clear = QPushButton("🗑️ تفريغ السلة")
        btn_clear.setObjectName("dangerButton")
        btn_clear.setStyleSheet("background-color: #e74c3c; padding: 10px 15px;")
        btn_clear.clicked.connect(self.clear_cart)
        
        top_layout.addWidget(self.barcode_input, 4)
        top_layout.addWidget(btn_search, 1)
        top_layout.addWidget(btn_hold, 1)
        top_layout.addWidget(btn_recall, 1)
        top_layout.addWidget(btn_clear, 1)
        
        layout.addLayout(top_layout)
        
        # 2. القسم الأوسط (الجدول بعرض الشاشة بالكامل)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "سعر البيع", "الكمية / الوزن", "الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellChanged.connect(self.on_cell_changed)
        layout.addWidget(self.table)
        
        # 3. القسم السفلي (بيانات العميل، طريقة الدفع، الإجمالي وزر الدفع بشكل أفقي متناسق)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # حقول العميل بشكل مدمج
        cust_group = QGroupBox("بيانات العميل / الأوردر")
        cust_layout = QHBoxLayout(cust_group)
        cust_layout.setContentsMargins(10, 5, 10, 5)
        cust_layout.setSpacing(10)
        
        self.cust_name = QLineEdit()
        self.cust_name.setPlaceholderText("اسم العميل")
        self.cust_phone = QLineEdit()
        self.cust_phone.setPlaceholderText("رقم الهاتف")
        self.cust_address = QLineEdit()
        self.cust_address.setPlaceholderText("عنوان التوصيل")
        
        cust_layout.addWidget(self.cust_name)
        cust_layout.addWidget(self.cust_phone)
        cust_layout.addWidget(self.cust_address)
        
        # طريقة الدفع
        payment_group = QGroupBox("طريقة الدفع")
        payment_layout = QHBoxLayout(payment_group)
        payment_layout.setContentsMargins(10, 5, 10, 5)
        self.payment_method = QComboBox()
        self.payment_method.addItems(["نقدي (Cash)", "فيزا (Visa)", "إنستا باي (InstaPay)", "فودافون كاش"])
        self.payment_method.setMinimumHeight(35)
        payment_layout.addWidget(self.payment_method)
        
        # الإجمالي الإجمالي والدفع
        summary_group = QGroupBox("الحساب")
        summary_layout = QHBoxLayout(summary_group)
        summary_layout.setContentsMargins(10, 5, 10, 5)
        summary_layout.setSpacing(15)
        
        self.total_label = QLabel("الإجمالي: 0.00 ل.س")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60;")
        
        btn_pay = QPushButton("💳 دفع وإنهاء (F5)")
        btn_pay.setStyleSheet("background-color: #2ecc71; color: white; font-size: 16px; padding: 8px 20px; font-weight: bold;")
        btn_pay.setMinimumHeight(40)
        btn_pay.clicked.connect(self.checkout)
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(btn_pay)
        
        bottom_layout.addWidget(cust_group, 4)
        bottom_layout.addWidget(payment_group, 2)
        bottom_layout.addWidget(summary_group, 3)
        
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def setup_shortcuts(self):
        # F1: التركيز على حقل البحث
        self.sh_focus = QShortcut(QKeySequence("F1"), self)
        self.sh_focus.activated.connect(self.barcode_input.setFocus)
        
        # F3: تعليق الفاتورة
        self.sh_hold = QShortcut(QKeySequence("F3"), self)
        self.sh_hold.activated.connect(self.hold_invoice)
        
        # F4: استدعاء الفاتورة
        self.sh_recall = QShortcut(QKeySequence("F4"), self)
        self.sh_recall.activated.connect(self.recall_invoice)
        
        # F5: دفع وإنهاء الفاتورة
        self.sh_pay = QShortcut(QKeySequence("F5"), self)
        self.sh_pay.activated.connect(self.checkout)

    def open_search_dialog(self):
        dialog = ProductSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.add_by_barcode()

    def add_by_barcode(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        session = get_session()
        product = session.query(Product).filter((Product.barcode == barcode) | (Product.name == barcode)).first()
        session.close()
        
        if product:
            if product.quantity <= 0:
                QMessageBox.warning(self, "تنبيه", "هذا المنتج غير متوفر في المخزن")
                return
                
            if product.barcode in self.cart:
                # للمنتجات العادية نزيد قطعة، للمنتجات الموزونة نزيد 1 جرام (0.001) أو كيلو
                step = 0.1 if product.is_weighted else 1.0
                if self.cart[product.barcode]['qty'] + step <= product.quantity:
                    self.cart[product.barcode]['qty'] += step
                else:
                    QMessageBox.warning(self, "تنبيه", "الكمية المطلوبة تتجاوز المتاح في المخزن")
            else:
                self.cart[product.barcode] = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'qty': 1.0 if product.is_weighted else 1.0,
                    'is_weighted': product.is_weighted
                }
            self.barcode_input.clear()
            self.update_cart_table()
        else:
            # إذا لم يجد بالباركود نبحث بحث جزئي بالاسم
            self.open_search_dialog()

    def update_cart_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        total = 0.0
        for barcode, item in self.cart.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            subtotal = item['price'] * item['qty']
            total += subtotal
            
            b_item = QTableWidgetItem(barcode)
            b_item.setFlags(b_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            n_item = QTableWidgetItem(item['name'])
            n_item.setFlags(n_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            p_item = QTableWidgetItem(f"{item['price']:.2f}") # قابل للتعديل
            
            # عرض الكمية ككسر إذا كان المنتج موزوناً، أو كعدد صحيح
            qty_str = f"{item['qty']:.3f}" if item['is_weighted'] else str(int(item['qty']))
            q_item = QTableWidgetItem(qty_str) # قابل للتعديل
            
            s_item = QTableWidgetItem(f"{subtotal:.2f}")
            s_item.setFlags(s_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.table.setItem(row, 0, b_item)
            self.table.setItem(row, 1, n_item)
            self.table.setItem(row, 2, p_item)
            self.table.setItem(row, 3, q_item)
            self.table.setItem(row, 4, s_item)
            
        self.total_label.setText(f"الإجمالي: {total:.2f} ل.س")
        self.table.blockSignals(False)

    def on_cell_changed(self, row, column):
        self.table.blockSignals(True)
        barcode = self.table.item(row, 0).text()
        item = self.cart.get(barcode)
        
        if not item:
            self.table.blockSignals(False)
            return
            
        session = get_session()
        db_product = session.query(Product).filter_by(barcode=barcode).first()
        session.close()
        
        if column == 2: # تعديل السعر
            try:
                new_price = float(self.table.item(row, column).text())
                if db_product and new_price < db_product.price:
                    QMessageBox.warning(self, "تنبيه", f"لا يمكن بيع المنتج بسعر أقل من سعر البيع الأساسي ({db_product.price:.2f} ل.س)")
                    new_price = db_product.price
                item['price'] = new_price
            except ValueError:
                pass
                
        elif column == 3: # تعديل الكمية / الوزن (جرامات)
            try:
                new_qty = float(self.table.item(row, column).text())
                if db_product:
                    if not db_product.is_weighted:
                        new_qty = int(new_qty)
                    if new_qty > db_product.quantity:
                        QMessageBox.warning(self, "تنبيه", f"الكمية المتاحة في المخزن فقط: {db_product.quantity}")
                        new_qty = db_product.quantity
                    if new_qty <= 0:
                        new_qty = 1
                item['qty'] = new_qty
            except ValueError:
                pass
                
        self.table.blockSignals(False)
        self.update_cart_table()

    def update_total_amount(self):
        total = sum(item['price'] * item['qty'] for item in self.cart.values())
        self.total_label.setText(f"الإجمالي: {total:.2f} ل.س")

    def hold_invoice(self):
        if not self.cart:
            return
        total = sum(item['price'] * item['qty'] for item in self.cart.values())
        invoice = {
            'cart': dict(self.cart),
            'customer_name': self.cust_name.text().strip(),
            'customer_phone': self.cust_phone.text().strip(),
            'customer_address': self.cust_address.text().strip(),
            'payment_method': self.payment_method.currentText(),
            'total': total
        }
        self.held_invoices.append(invoice)
        QMessageBox.information(self, "تم تعليق الفاتورة", f"تم حفظ الفاتورة مؤقتاً بنجاح. عدد الفواتير المعلقة: {len(self.held_invoices)}")
        self.clear_cart()
        self.cust_name.clear()
        self.cust_phone.clear()
        self.cust_address.clear()

    def recall_invoice(self):
        if not self.held_invoices:
            QMessageBox.information(self, "تنبيه", "لا توجد فواتير معلقة حالياً.")
            return
        dialog = RecallDialog(self.held_invoices, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            inv = dialog.selected_invoice
            self.cart = inv['cart']
            self.cust_name.setText(inv['customer_name'])
            self.cust_phone.setText(inv['customer_phone'])
            self.cust_address.setText(inv['customer_address'])
            idx = self.payment_method.findText(inv['payment_method'])
            if idx >= 0:
                self.payment_method.setCurrentIndex(idx)
            self.update_cart_table()

    def clear_cart(self):
        self.cart.clear()
        self.update_cart_table()

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "السلة فارغة", "الرجاء إضافة منتجات للفاتورة أولاً")
            return
            
        session = get_session()
        try:
            # تحديث مخزن البضائع
            for barcode, item in self.cart.items():
                prod = session.query(Product).filter_by(barcode=barcode).first()
                if prod:
                    prod.quantity -= item['qty']
            session.commit()
            
            QMessageBox.information(self, "تمت العملية", f"تم تسجيل الفاتورة بنجاح ودفعها عن طريق ({self.payment_method.currentText()})")
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
        
        # نموذج إدخال المنتجات
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("الباركود")
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("اسم الصنف")
        
        self.input_price = QDoubleSpinBox()
        self.input_price.setMaximum(999999.0)
        self.input_price.setPrefix("السعر: ")
        
        self.input_qty = QDoubleSpinBox() # تغييرها لتدعم الكسور في الكمية (الوزن)
        self.input_qty.setMaximum(99999.0)
        self.input_qty.setPrefix("الكمية: ")
        
        self.check_weighted = QCheckBox("منتج بالوزن / جرامات")
        
        btn_save = QPushButton("إضافة/تعديل صنف")
        btn_save.clicked.connect(self.save_product)
        btn_save.setStyleSheet("background-color: #1abc9c;")
        
        form_layout.addWidget(self.input_barcode)
        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_price)
        form_layout.addWidget(self.input_qty)
        form_layout.addWidget(self.check_weighted)
        form_layout.addWidget(btn_save)
        
        layout.addWidget(form_widget)
        
        # جدول عرض البضائع المتاحة
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "السعر", "الكمية المتاحة", "نوع البيع"])
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
            
            qty_str = f"{prod.quantity:.3f}" if prod.is_weighted else str(int(prod.quantity))
            self.table.setItem(row, 3, QTableWidgetItem(qty_str))
            self.table.setItem(row, 4, QTableWidgetItem("بالوزن" if prod.is_weighted else "بالقطعة"))

    def save_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        price = self.input_price.value()
        qty = self.input_qty.value()
        is_weighted = self.check_weighted.isChecked()
        
        if not barcode or not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء تعبئة حقل الباركود والاسم")
            return
            
        session = get_session()
        prod = session.query(Product).filter_by(barcode=barcode).first()
        if prod:
            prod.name = name
            prod.price = price
            prod.quantity = qty
            prod.is_weighted = is_weighted
        else:
            prod = Product(barcode=barcode, name=name, price=price, quantity=qty, is_weighted=is_weighted)
            session.add(prod)
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "تم الحفظ", "تم حفظ الصنف بنجاح!")
        self.input_barcode.clear()
        self.input_name.clear()
        self.input_price.setValue(0)
        self.input_qty.setValue(0)
        self.check_weighted.setChecked(False)
        self.load_products()

    def load_row_to_form(self):
        row = self.table.currentRow()
        if row >= 0:
            self.input_barcode.setText(self.table.item(row, 0).text())
            self.input_name.setText(self.table.item(row, 1).text())
            self.input_price.setValue(float(self.table.item(row, 2).text()))
            self.input_qty.setValue(float(self.table.item(row, 3).text()))
            self.check_weighted.setChecked(self.table.item(row, 4).text() == "بالوزن")


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
