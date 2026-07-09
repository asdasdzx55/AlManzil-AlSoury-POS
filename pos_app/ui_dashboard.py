from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, 
                             QFormLayout, QComboBox, QMessageBox, QDoubleSpinBox, QSpinBox,
                             QGroupBox, QCheckBox, QDialog, QListWidget, QListWidgetItem, QDialogButtonBox,
                             QTabWidget, QTextEdit, QDateEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QShortcut, QKeySequence
from database import get_session, Product, Category, Supplier, User

class DashboardWindow(QWidget):
    def __init__(self, user, on_logout):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.dark_mode = True # المظهر الافتراضي هو الليلي
        self.init_ui()

    def init_ui(self):
        # Layout الرئيسي (شريط جانبي يمين، والصفحات على اليسار مع استجابة للشاشة)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. شريط القوائم الجانبي
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(75)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(15)
        
        # شعار المحل
        shop_title = QLabel("🏡")
        shop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shop_title.setStyleSheet("font-size: 32px; margin-bottom: 20px;")
        shop_title.setToolTip(f"المنزل السوري - المستخدم: {self.user.username} ({self.user.role})")
        sidebar_layout.addWidget(shop_title)
        
        # أزرار شريط التنقل
        self.btn_pos = QPushButton("🛒")
        self.btn_pos.setToolTip("نقطة البيع (الكاشير)")
        self.btn_pos.setCheckable(True)
        self.btn_pos.setChecked(True)
        self.btn_pos.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.btn_pos)
        
        self.btn_returns = QPushButton("↩️")
        self.btn_returns.setToolTip("مرتجع المبيعات")
        self.btn_returns.setCheckable(True)
        self.btn_returns.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.btn_returns)
        
        self.btn_purchases = QPushButton("📥")
        self.btn_purchases.setToolTip("فاتورة المشتريات والتوريد")
        self.btn_purchases.setCheckable(True)
        self.btn_purchases.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.btn_purchases)
        
        self.btn_inventory = QPushButton("📦")
        self.btn_inventory.setToolTip("إدارة الأصناف")
        self.btn_inventory.setCheckable(True)
        self.btn_inventory.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.btn_inventory)
        
        self.btn_suppliers = QPushButton("👥")
        self.btn_suppliers.setToolTip("إدارة الموردين")
        self.btn_suppliers.setCheckable(True)
        self.btn_suppliers.clicked.connect(lambda: self.switch_page(4))
        sidebar_layout.addWidget(self.btn_suppliers)
        
        self.btn_hr = QPushButton("👤")
        self.btn_hr.setToolTip("إدارة شؤون الموظفين والرواتب (HR)")
        self.btn_hr.setCheckable(True)
        self.btn_hr.clicked.connect(lambda: self.switch_page(5))
        sidebar_layout.addWidget(self.btn_hr)
        
        self.btn_reports = QPushButton("📈")
        self.btn_reports.setToolTip("التقارير والمبيعات")
        self.btn_reports.setCheckable(True)
        if self.user.role != 'admin':
            self.btn_reports.setEnabled(False)
            self.btn_reports.setToolTip("هذه الصفحة متاحة للمدير فقط")
            self.btn_reports.setStyleSheet("color: #7f8c8d; font-size: 24px;")
        self.btn_reports.clicked.connect(lambda: self.switch_page(6))
        sidebar_layout.addWidget(self.btn_reports)
        
        self.btn_sync = QPushButton("🔄")
        self.btn_sync.setToolTip("المزامنة السحابية")
        self.btn_sync.setCheckable(True)
        self.btn_sync.clicked.connect(lambda: self.switch_page(7))
        sidebar_layout.addWidget(self.btn_sync)
        
        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setToolTip("الإعدادات والشركاء")
        self.btn_settings.setCheckable(True)
        self.btn_settings.clicked.connect(lambda: self.switch_page(8))
        sidebar_layout.addWidget(self.btn_settings)
        
        sidebar_layout.addStretch()
        
        # زر تبديل المظهر (ليلي / مضيء)
        self.btn_theme = QPushButton("☀️")
        self.btn_theme.setToolTip("تفعيل المود المضيء")
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)
        
        # زر تسجيل الخروج
        btn_logout = QPushButton("🚪")
        btn_logout.setToolTip("تسجيل الخروج")
        btn_logout.setObjectName("dangerButton")
        btn_logout.clicked.connect(self.on_logout)
        sidebar_layout.addWidget(btn_logout)
        
        self.menu_buttons = [self.btn_pos, self.btn_returns, self.btn_purchases, self.btn_inventory, self.btn_suppliers, self.btn_hr, self.btn_reports, self.btn_sync, self.btn_settings]
        
        # 2. حاوي الصفحات الرئيسي (مستجيب وقابل للتمدد)
        self.container = QStackedWidget()
        self.container.setStyleSheet("padding: 15px;")
        
        self.page_pos = POSPage(self.user)
        self.page_returns = ReturnsPage()
        self.page_purchases = PurchasesPage()
        self.page_inventory = InventoryPage()
        self.page_suppliers = SuppliersPage()
        self.page_hr = HRPage()
        self.page_reports = ReportsPage()
        self.page_sync = SyncPage()
        self.page_settings = SettingsPage()
        
        self.container.addWidget(self.page_pos)
        self.container.addWidget(self.page_returns)
        self.container.addWidget(self.page_purchases)
        self.container.addWidget(self.page_inventory)
        self.container.addWidget(self.page_suppliers)
        self.container.addWidget(self.page_hr)
        self.container.addWidget(self.page_reports)
        self.container.addWidget(self.page_sync)
        self.container.addWidget(self.page_settings)
        
        # ترتيب العناصر في Layout الرئيسي
        main_layout.addWidget(self.container, 1) # المحتوى يأخذ المساحة المتبقية
        main_layout.addWidget(self.sidebar)       # الشريط الجانبي في اليمين (نظام عربي)
        
        self.setLayout(main_layout)

    def switch_page(self, index):
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)
        self.container.setCurrentIndex(index)
        
        if index == 0:
            self.page_pos.load_delivery_employees()
        elif index == 1:
            self.page_returns.clear_page()
        elif index == 2:
            self.page_purchases.load_suppliers()
        elif index == 3:
            self.page_inventory.load_products()
        elif index == 4:
            self.page_suppliers.load_suppliers()
        elif index == 5:
            self.page_hr.load_employees()
        elif index == 6:
            self.page_reports.load_reports()
        elif index == 8:
            self.page_settings.load_settings()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        
        import os
        theme_file = "styles_dark.qss" if self.dark_mode else "styles_light.qss"
        style_path = os.path.join(os.path.dirname(__file__), theme_file)
        
        from PyQt6.QtWidgets import QApplication
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())
                
        self.btn_theme.setText("☀️" if self.dark_mode else "🌙")
        self.btn_theme.setToolTip("تفعيل المود المضيء" if self.dark_mode else "تفعيل المود الليلي")


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
        from database import ProductBarcode
        products = session.query(Product).join(Product.barcodes, isouter=True).filter(
            (Product.name.like(f"%{query}%")) | 
            (Product.barcode.like(f"%{query}%")) | 
            (ProductBarcode.barcode.like(f"%{query}%"))
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
        
        self.combo_delivery = QComboBox()
        self.combo_delivery.setPlaceholderText("طيار الديلفري")
        self.load_delivery_employees()
        
        cust_layout.addWidget(self.cust_name)
        cust_layout.addWidget(self.cust_phone)
        cust_layout.addWidget(self.cust_address)
        cust_layout.addWidget(self.combo_delivery)
        
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

    def load_delivery_employees(self):
        self.combo_delivery.clear()
        self.combo_delivery.addItem("بدون ديلفري (سفري)", None)
        session = get_session()
        from database import Employee
        delivery_boys = session.query(Employee).filter_by(role='delivery').all()
        for emp in delivery_boys:
            self.combo_delivery.addItem(emp.name, emp.id)
        session.close()

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
            
        from database import ProductBarcode
        session = get_session()
        
        # 1. البحث أولاً في الباركود الرئيسي لجدول المنتجات
        product = session.query(Product).filter_by(barcode=barcode).first()
        
        # 2. إذا لم يعثر عليه، نبحث في جدول الباركودات الفرعية البديلة
        if not product:
            barcode_entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
            if barcode_entry:
                product = barcode_entry.product
                
        # 3. إذا لم يعثر عليه، نبحث بالاسم كخيار أخير
        if not product:
            product = session.query(Product).filter_by(name=barcode).first()
            
        if product:
            # تحديد الكمية المتاحة (سواء له أو لمنتجه الأب إذا كان علبة)
            available_qty = product.quantity
            if product.parent_id:
                parent_prod = session.query(Product).get(product.parent_id)
                if parent_prod:
                    available_qty = parent_prod.quantity / product.units_in_box
            
            if available_qty <= 0:
                QMessageBox.warning(self, "تنبيه", "هذا المنتج غير متوفر في المخزن")
                session.close()
                return
                
            cart_key = f"prod_{product.id}"
            
            if cart_key in self.cart:
                step = 0.1 if product.is_weighted else 1.0
                if self.cart[cart_key]['qty'] + step <= available_qty:
                    self.cart[cart_key]['qty'] += step
                else:
                    QMessageBox.warning(self, "تنبيه", "الكمية المطلوبة تتجاوز المتاح في المخزن")
            else:
                self.cart[cart_key] = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'qty': 1.0 if product.is_weighted else 1.0,
                    'is_weighted': product.is_weighted,
                    'parent_id': product.parent_id,
                    'units_in_box': product.units_in_box,
                    'barcode': barcode
                }
            self.barcode_input.clear()
            self.update_cart_table()
        else:
            # إذا لم يجد بالباركود نبحث بحث جزئي بالاسم
            self.open_search_dialog()
        session.close()

    def update_cart_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        total = 0.0
        for cart_key, item in self.cart.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            subtotal = item['price'] * item['qty']
            total += subtotal
            
            b_item = QTableWidgetItem(item['barcode'])
            b_item.setFlags(b_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            n_item = QTableWidgetItem(item['name'])
            n_item.setFlags(n_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            p_item = QTableWidgetItem(f"{item['price']:.2f}") # قابل للتعديل
            
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
        
        target_item = None
        for key, item in self.cart.items():
            if item['barcode'] == barcode:
                target_item = item
                break
                
        if not target_item:
            self.table.blockSignals(False)
            return
            
        session = get_session()
        db_product = session.query(Product).get(target_item['id'])
        session.close()
        
        if column == 2: # تعديل السعر
            try:
                new_price = float(self.table.item(row, column).text())
                if db_product and new_price < db_product.price:
                    QMessageBox.warning(self, "تنبيه", f"لا يمكن بيع المنتج بسعر أقل من سعر البيع الأساسي ({db_product.price:.2f} ل.س)")
                    new_price = db_product.price
                target_item['price'] = new_price
            except ValueError:
                pass
                
        elif column == 3: # تعديل الكمية / الوزن
            try:
                new_qty = float(self.table.item(row, column).text())
                if db_product:
                    max_qty = db_product.quantity
                    if db_product.parent_id:
                        session = get_session()
                        parent_prod = session.query(Product).get(db_product.parent_id)
                        session.close()
                        if parent_prod:
                            max_qty = parent_prod.quantity / db_product.units_in_box
                            
                    if not db_product.is_weighted:
                        new_qty = int(new_qty)
                    if new_qty > max_qty:
                        QMessageBox.warning(self, "تنبيه", f"الكمية المتاحة في المخزن فقط: {max_qty}")
                        new_qty = max_qty
                    if new_qty <= 0:
                        new_qty = 1
                target_item['qty'] = new_qty
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
            from database import Invoice, InvoiceItem
            
            # حساب إجمالي الفاتورة
            total_amount = sum(item['price'] * item['qty'] for item in self.cart.values())
            
            # تسجيل الفاتورة الرئيسية
            cust_name = self.cust_name.text().strip()
            cust_phone = self.cust_phone.text().strip()
            delivery_emp_id = self.combo_delivery.currentData()
            
            new_inv = Invoice(
                total=total_amount,
                payment_method=self.payment_method.currentText(),
                customer_name=cust_name if cust_name else None,
                customer_phone=cust_phone if cust_phone else None,
                delivery_employee_id=delivery_emp_id
            )
            session.add(new_inv)
            session.commit() # الحفظ للحصول على رقم الفاتورة (new_inv.id)
            
            # تسجيل محتويات الفاتورة وخصم المخزون
            for key, item in self.cart.items():
                prod = session.query(Product).get(item['id'])
                if prod:
                    # خصم المخزون
                    if prod.parent_id:
                        parent_prod = session.query(Product).get(prod.parent_id)
                        if parent_prod:
                            parent_prod.quantity -= (item['qty'] * prod.units_in_box)
                    else:
                        prod.quantity -= item['qty']
                        
                    # إنشاء تفصيل الفاتورة مع تثبيت سعر التكلفة الحالي لحساب الأرباح بدقة لاحقاً
                    inv_item = InvoiceItem(
                        invoice_id=new_inv.id,
                        product_id=prod.id,
                        quantity=item['qty'],
                        price=item['price'],
                        cost_price=prod.cost_price if prod.cost_price else 0.0
                    )
                    session.add(inv_item)
                    
            session.commit()
            
            # عرض الريسيت الحراري التفاعلي
            dialog = ReceiptDialog(new_inv.id, self)
            dialog.exec()
            
            # تنظيف البيانات
            self.clear_cart()
            self.cust_name.clear()
            self.cust_phone.clear()
            self.cust_address.clear()
            self.load_delivery_employees()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل إتمام العملية: {str(e)}")
        finally:
            session.close()


# ==================== RECEIPT DIALOG ====================
class ReceiptDialog(QDialog):
    def __init__(self, invoice_id, parent=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        self.setWindowTitle("فاتورة البيع - ريسيت الكاشير")
        self.resize(380, 550)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier New", 10))
        layout.addWidget(self.text_edit)
        
        buttons = QHBoxLayout()
        btn_print = QPushButton("طباعة 🖨️")
        btn_print.clicked.connect(self.print_receipt)
        btn_print.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        
        btn_close = QPushButton("إغلاق")
        btn_close.clicked.connect(self.accept)
        
        buttons.addWidget(btn_print)
        buttons.addWidget(btn_close)
        layout.addLayout(buttons)
        self.setLayout(layout)
        
        self.generate_receipt_content()

    def generate_receipt_content(self):
        session = get_session()
        from database import Invoice, AppSetting
        
        # الاستعلام عن معلومات المحل من الإعدادات
        name_set = session.query(AppSetting).filter_by(key='shop_name').first()
        addr_set = session.query(AppSetting).filter_by(key='shop_address').first()
        phone_set = session.query(AppSetting).filter_by(key='shop_phone').first()
        
        shop_name = name_set.value if name_set else "سوبر ماركت المنزل السوري"
        shop_address = addr_set.value if addr_set else "دمشق"
        shop_phone = phone_set.value if phone_set else "0999999999"
        
        inv = session.query(Invoice).get(self.invoice_id)
        if not inv:
            session.close()
            return
            
        border = "--------------------------------------\n"
        html = f"<div style='text-align: center; font-family: monospace;'>"
        html += f"<h2>{shop_name}</h2>"
        html += f"<p>{shop_address}</p>"
        html += f"<p>هاتف: {shop_phone}</p>"
        html += f"<p><b>رقم الفاتورة: #{inv.id}</b></p>"
        html += f"<p>التاريخ: {inv.date.strftime('%Y-%m-%d %H:%M')}</p>"
        html += f"</div>"
        
        html += f"<pre>{border}"
        html += f"{'الصنف':<15} | {'الكمية':<6} | {'السعر':<7} | {'الإجمالي':<8}\n"
        html += f"{border}"
        
        for item in inv.items:
            name_truncated = item.product.name[:13]
            subtotal = item.price * item.quantity
            html += f"{name_truncated:<15} | {item.quantity:<6} | {item.price:<7.1f} | {subtotal:<8.1f}\n"
            
        html += f"{border}</pre>"
        
        html += f"<div style='text-align: right; font-family: monospace; margin-top: 10px;'>"
        html += f"<p><b>إجمالي الحساب: {inv.total:.2f} ل.س</b></p>"
        html += f"<p>طريقة الدفع: {inv.payment_method}</p>"
        if inv.customer_name:
            html += f"<p>العميل: {inv.customer_name}</p>"
            if inv.customer_phone:
                html += f"<p>الهاتف: {inv.customer_phone}</p>"
        html += f"</div>"
        
        html += f"<div style='text-align: center; margin-top: 20px; font-family: monospace;'>"
        html += f"<p>شكراً لزيارتكم وسعداء بخدمتكم!</p>"
        html += f"</div>"
        
        self.text_edit.setHtml(html)
        session.close()

    def print_receipt(self):
        from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.text_edit.print(printer)


# ==================== QUICK PRODUCT DIALOG (FLOATING) ====================
class QuickProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة/تعديل صنف سريع")
        self.resize(450, 400)
        self.init_ui()

    def init_ui(self):
        form_layout = QFormLayout()
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("أدخل الباركود الرئيسي...")
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("اسم المنتج...")
        
        self.input_cost = QDoubleSpinBox()
        self.input_cost.setMaximum(999999.0)
        self.input_cost.setPrefix("سعر الشراء: ")
        
        self.input_price = QDoubleSpinBox()
        self.input_price.setMaximum(999999.0)
        self.input_price.setPrefix("سعر البيع: ")
        
        self.combo_subcat = QComboBox()
        self.load_subcategories()
        
        self.check_weighted = QCheckBox("هذا الصنف بالوزن / جرامات")
        
        form_layout.addRow("الباركود:", self.input_barcode)
        form_layout.addRow("اسم المنتج:", self.input_name)
        form_layout.addRow("سعر التكلفة:", self.input_cost)
        form_layout.addRow("سعر البيع:", self.input_price)
        form_layout.addRow("التصنيف الفرعي:", self.combo_subcat)
        form_layout.addRow("", self.check_weighted)
        
        # ربط زر إنتر بالانتقال للخانة التالية لتسريع الإدخال
        self.input_barcode.returnPressed.connect(self.focusNextChild)
        self.input_name.returnPressed.connect(self.focusNextChild)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_product)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        
        # ربط الباركود بحدث تغيير النص للبحث التلقائي وتحميل البيانات للتعديل السريع
        self.input_barcode.textChanged.connect(self.check_existing_barcode)

    def load_subcategories(self):
        session = get_session()
        from database import Subcategory
        subcats = session.query(Subcategory).all()
        for sc in subcats:
            self.combo_subcat.addItem(f"{sc.category.name} -> {sc.name}", sc.id)
        session.close()

    def check_existing_barcode(self, text):
        barcode = text.strip()
        if not barcode:
            return
            
        session = get_session()
        from database import ProductBarcode
        
        # 1. التحقق من الباركود الرئيسي
        prod = session.query(Product).filter_by(barcode=barcode).first()
        
        # 2. التحقق من الباركودات البديلة
        if not prod:
            entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
            if entry:
                prod = entry.product
                
        if prod:
            self.input_name.setText(prod.name)
            self.input_cost.setValue(prod.cost_price if prod.cost_price else 0.0)
            self.input_price.setValue(prod.price)
            self.check_weighted.setChecked(prod.is_weighted)
            idx = self.combo_subcat.findData(prod.subcategory_id)
            if idx >= 0:
                self.combo_subcat.setCurrentIndex(idx)
        session.close()

    def save_product(self):
        barcode = self.input_barcode.text().strip()
        name = self.input_name.text().strip()
        cost = self.input_cost.value()
        price = self.input_price.value()
        is_weighted = self.check_weighted.isChecked()
        subcat_id = self.combo_subcat.currentData()
        
        if not barcode or not name or not subcat_id:
            QMessageBox.warning(self, "تنبيه", "يرجى تعبئة جميع الحقول المطلوبة")
            return
            
        session = get_session()
        from database import ProductBarcode
        
        # 1. البحث في الباركود الرئيسي
        prod = session.query(Product).filter_by(barcode=barcode).first()
        
        # 2. البحث في الباركودات البديلة
        if not prod:
            entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
            if entry:
                prod = entry.product
                
        if prod:
            prod.name = name
            prod.cost_price = cost
            prod.price = price
            prod.is_weighted = is_weighted
            prod.subcategory_id = subcat_id
            # تحديث الباركود الرئيسي في حال كان الباركود الحالي هو الأساسي
            if prod.barcode == barcode:
                pass
        else:
            prod = Product(
                name=name, 
                price=price, 
                cost_price=cost, 
                quantity=0.0, 
                is_weighted=is_weighted, 
                subcategory_id=subcat_id,
                barcode=barcode
            )
            session.add(prod)
            
        session.commit()
        session.close()
        QMessageBox.information(self, "نجاح", "تم حفظ المنتج بنجاح!")
        self.accept()

    def keyPressEvent(self, event):
        # منع إغلاق الديالوج بإنتر والانتقال للخانة التالية
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            focused = self.focusWidget()
            if not isinstance(focused, QPushButton):
                self.focusNextChild()
                event.accept()
                return
        super().keyPressEvent(event)


# ==================== PURCHASES PAGE ====================
class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = {}
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # العنوان والبحث العلوي والسريع
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        
        header = QLabel("📥 فاتورة شراء وتوريد جديدة")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("أدخل الباركود أو امسح بالجهاز للبدء... (F1)")
        self.barcode_input.returnPressed.connect(self.add_by_barcode)
        
        btn_search = QPushButton("🔍 بحث")
        btn_search.clicked.connect(self.open_search_dialog)
        
        btn_quick_add = QPushButton("➕ إضافة/تعديل صنف سريع (F6)")
        btn_quick_add.clicked.connect(self.open_quick_add_dialog)
        btn_quick_add.setStyleSheet("background-color: #2c3e50; color: white;")
        
        top_layout.addWidget(header, 2)
        top_layout.addWidget(self.barcode_input, 4)
        top_layout.addWidget(btn_search, 1)
        top_layout.addWidget(btn_quick_add, 2)
        layout.addWidget(top_widget)
        
        # جدول المنتجات بمنتصف الشاشة
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "سعر الشراء (التكلفة)", "الكمية المشتراة", "البونص (الهدايا)", "الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellChanged.connect(self.on_cell_changed)
        layout.addWidget(self.table)
        
        # الشريط السفلي (المورد، نوع الدفع، رصيد المورد، الإجمالي)
        bottom_layout = QHBoxLayout()
        
        # مجموعة المورد
        sup_group = QGroupBox("بيانات المورد")
        sup_layout = QHBoxLayout(sup_group)
        self.combo_supplier = QComboBox()
        self.combo_supplier.addItem("لا شيء (مشتريات بدون مورد)", None)
        self.load_suppliers()
        self.combo_supplier.currentIndexChanged.connect(self.on_supplier_changed)
        
        # صندوق عرض الرصيد قبل الفاتورة
        self.lbl_supplier_balance = QLabel("الرصيد المستحق قبل الفاتورة: 0.00 ل.س")
        self.lbl_supplier_balance.setStyleSheet("font-weight: bold; color: #e74c3c;")
        
        sup_layout.addWidget(self.combo_supplier)
        sup_layout.addWidget(self.lbl_supplier_balance)
        
        # مجموعة الدفع
        pay_group = QGroupBox("طريقة الدفع")
        pay_layout = QHBoxLayout(pay_group)
        self.combo_pay_type = QComboBox()
        self.combo_pay_type.addItems(["نقدي", "آجل (دين للمورد)"])
        pay_layout.addWidget(self.combo_pay_type)
        
        # مجموعة الإجمالي والحفظ
        sum_group = QGroupBox("ملخص الشراء")
        sum_layout = QVBoxLayout(sum_group)
        self.total_label = QLabel("إجمالي الفاتورة: 0.00 ل.س")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ecc71;")
        
        btn_save = QPushButton("💾 حفظ وتأكيد فاتورة الشراء (F5)")
        btn_save.setProperty("styleSheetClass", "primary")
        btn_save.clicked.connect(self.checkout_purchase)
        
        sum_layout.addWidget(self.total_label)
        sum_layout.addWidget(btn_save)
        
        bottom_layout.addWidget(sup_group, 4)
        bottom_layout.addWidget(pay_group, 2)
        bottom_layout.addWidget(sum_group, 3)
        
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def setup_shortcuts(self):
        self.sh_focus = QShortcut(QKeySequence("F1"), self)
        self.sh_focus.activated.connect(self.barcode_input.setFocus)
        
        self.sh_quick = QShortcut(QKeySequence("F6"), self)
        self.sh_quick.activated.connect(self.open_quick_add_dialog)
        
        self.sh_save = QShortcut(QKeySequence("F5"), self)
        self.sh_save.activated.connect(self.checkout_purchase)

    def load_suppliers(self):
        curr_idx = self.combo_supplier.currentIndex()
        self.combo_supplier.clear()
        self.combo_supplier.addItem("لا شيء (مشتريات بدون مورد)", None)
        
        session = get_session()
        suppliers = session.query(Supplier).all()
        session.close()
        for sup in suppliers:
            self.combo_supplier.addItem(f"{sup.name} ({sup.phone if sup.phone else ''})", sup.id)
            
        if curr_idx >= 0 and curr_idx < self.combo_supplier.count():
            self.combo_supplier.setCurrentIndex(curr_idx)

    def on_supplier_changed(self):
        supplier_id = self.combo_supplier.currentData()
        if not supplier_id:
            self.lbl_supplier_balance.setText("الرصيد المستحق قبل الفاتورة: 0.00 ل.س")
            return
            
        session = get_session()
        sup = session.query(Supplier).get(supplier_id)
        if sup:
            self.lbl_supplier_balance.setText(f"الرصيد المستحق قبل الفاتورة: {sup.balance:.2f} ل.س")
        session.close()

    def open_search_dialog(self):
        dialog = ProductSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.add_by_barcode()

    def open_quick_add_dialog(self):
        dialog = QuickProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pass

    def add_by_barcode(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        session = get_session()
        from database import ProductBarcode
        
        # 1. البحث في الباركود الرئيسي للمنتج
        product = session.query(Product).filter_by(barcode=barcode).first()
        
        # 2. البحث في الباركودات البديلة
        if not product:
            entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
            if entry:
                product = entry.product
                
        # 3. البحث بالاسم
        if not product:
            product = session.query(Product).filter_by(name=barcode).first()
            
        if product:
            cart_key = f"prod_{product.id}"
            if cart_key in self.cart:
                self.cart[cart_key]['qty'] += 1.0
            else:
                self.cart[cart_key] = {
                    'id': product.id,
                    'name': product.name,
                    'cost_price': product.cost_price if product.cost_price else 0.0,
                    'qty': 1.0,
                    'bonus': 0.0,
                    'is_weighted': product.is_weighted,
                    'barcode': barcode
                }
            self.barcode_input.clear()
            self.update_table()
        else:
            # لو لم يجد، يفتح نافذة الإضافة السريعة ويعبئ الباركود تلقائياً
            dialog = QuickProductDialog(self)
            dialog.input_barcode.setText(barcode)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.add_by_barcode()
        session.close()

    def update_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        total = 0.0
        for key, item in self.cart.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            subtotal = item['cost_price'] * item['qty']
            total += subtotal
            
            b_item = QTableWidgetItem(item['barcode'])
            b_item.setFlags(b_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            n_item = QTableWidgetItem(item['name'])
            n_item.setFlags(n_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            c_item = QTableWidgetItem(f"{item['cost_price']:.2f}")
            
            qty_str = f"{item['qty']:.3f}" if item['is_weighted'] else str(int(item['qty']))
            q_item = QTableWidgetItem(qty_str)
            
            bon_str = f"{item['bonus']:.3f}" if item['is_weighted'] else str(int(item['bonus']))
            bon_item = QTableWidgetItem(bon_str)
            
            s_item = QTableWidgetItem(f"{subtotal:.2f}")
            s_item.setFlags(s_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.table.setItem(row, 0, b_item)
            self.table.setItem(row, 1, n_item)
            self.table.setItem(row, 2, c_item)
            self.table.setItem(row, 3, q_item)
            self.table.setItem(row, 4, bon_item)
            self.table.setItem(row, 5, s_item)
            
        self.total_label.setText(f"إجمالي الفاتورة: {total:.2f} ل.س")
        self.table.blockSignals(False)

    def on_cell_changed(self, row, column):
        self.table.blockSignals(True)
        barcode = self.table.item(row, 0).text()
        
        target_item = None
        for key, item in self.cart.items():
            if item['barcode'] == barcode:
                target_item = item
                break
                
        if not target_item:
            self.table.blockSignals(False)
            return
            
        if column == 2: # سعر الشراء
            try:
                target_item['cost_price'] = float(self.table.item(row, column).text())
            except ValueError:
                pass
        elif column == 3: # الكمية
            try:
                target_item['qty'] = float(self.table.item(row, column).text())
            except ValueError:
                pass
        elif column == 4: # البونص
            try:
                target_item['bonus'] = float(self.table.item(row, column).text())
            except ValueError:
                pass
                
        self.table.blockSignals(False)
        self.update_table()

    def checkout_purchase(self):
        if not self.cart:
            QMessageBox.warning(self, "الفاتورة فارغة", "الرجاء إضافة أصناف أولاً")
            return
            
        total = sum(item['cost_price'] * item['qty'] for item in self.cart.values())
        supplier_id = self.combo_supplier.currentData()
        pay_type = self.combo_pay_type.currentText()
        
        session = get_session()
        try:
            for key, item in self.cart.items():
                prod = session.query(Product).get(item['id'])
                if prod:
                    prod.quantity += (item['qty'] + item['bonus'])
                    prod.cost_price = item['cost_price']
            
            if pay_type == "آجل (دين للمورد)" and supplier_id:
                sup = session.query(Supplier).get(supplier_id)
                if sup:
                    sup.balance += total
                    
                    from database import SupplierTransaction
                    tx = SupplierTransaction(supplier_id=supplier_id, amount=total, type="purchase_in", note="شراء بضاعة بالآجل - فاتورة شراء")
                    session.add(tx)
                    
            session.commit()
            QMessageBox.information(self, "تم الحفظ", "تم حفظ الفاتورة وتحديث المخازن والديون بنجاح!")
            self.cart.clear()
            self.update_table()
            self.on_supplier_changed()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل حفظ الفاتورة: {str(e)}")
        finally:
            session.close()


# ==================== EDIT DIALOG FOR INVENTORY ====================
class EditProductDialog(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("تعديل الصنف")
        self.resize(500, 450)
        self.init_ui()

    def init_ui(self):
        form_layout = QFormLayout()
        
        self.input_name = QLineEdit()
        self.input_price = QDoubleSpinBox()
        self.input_price.setMaximum(999999.0)
        self.input_qty = QDoubleSpinBox()
        self.input_qty.setMaximum(999999.0)
        self.check_weighted = QCheckBox("منتج بالوزن / جرامات")
        
        self.input_barcodes = QLineEdit()
        self.input_barcodes.setPlaceholderText("مثال: barcode1, barcode2, barcode3")
        
        self.combo_subcategory = QComboBox()
        self.combo_parent = QComboBox()
        self.check_is_box = QCheckBox("هذا الصنف عبارة عن علبة لمنتج آخر")
        self.input_units_in_box = QSpinBox()
        self.input_units_in_box.setValue(1)
        self.input_units_in_box.setEnabled(False)
        
        self.check_is_box.toggled.connect(self.input_units_in_box.setEnabled)
        self.check_is_box.toggled.connect(self.combo_parent.setEnabled)
        
        form_layout.addRow("اسم المنتج:", self.input_name)
        form_layout.addRow("سعر المنتج:", self.input_price)
        form_layout.addRow("الكمية المتاحة:", self.input_qty)
        form_layout.addRow("الباركودات (افصل بـ ,):", self.input_barcodes)
        form_layout.addRow("التصنيف الفرعي:", self.combo_subcategory)
        form_layout.addRow("", self.check_weighted)
        form_layout.addRow("", self.check_is_box)
        form_layout.addRow("المنتج الفردي الأب:", self.combo_parent)
        form_layout.addRow("عدد القطع بالعلبة:", self.input_units_in_box)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_changes)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)
        
        self.load_relations()
        self.load_product_data()

    def load_relations(self):
        session = get_session()
        # التصنيفات الفرعية
        from database import Subcategory
        subcats = session.query(Subcategory).all()
        for sc in subcats:
            self.combo_subcategory.addItem(f"{sc.category.name} ➔ {sc.name}", sc.id)
            
        # المنتجات للأبوة
        products = session.query(Product).filter(Product.id != self.product_id).all()
        self.combo_parent.addItem("لا يوجد (منتج فردي)", None)
        for p in products:
            self.combo_parent.addItem(p.name, p.id)
        session.close()

    def load_product_data(self):
        session = get_session()
        prod = session.query(Product).get(self.product_id)
        if prod:
            self.input_name.setText(prod.name)
            self.input_price.setValue(prod.price)
            self.input_qty.setValue(prod.quantity)
            self.check_weighted.setChecked(prod.is_weighted)
            
            barcodes = [b.barcode for b in prod.barcodes]
            self.input_barcodes.setText(", ".join(barcodes))
            
            idx = self.combo_subcategory.findData(prod.subcategory_id)
            if idx >= 0:
                self.combo_subcategory.setCurrentIndex(idx)
                
            if prod.parent_id:
                self.check_is_box.setChecked(True)
                p_idx = self.combo_parent.findData(prod.parent_id)
                if p_idx >= 0:
                    self.combo_parent.setCurrentIndex(p_idx)
                self.input_units_in_box.setValue(prod.units_in_box)
            else:
                self.check_is_box.setChecked(False)
                self.combo_parent.setEnabled(False)
                self.input_units_in_box.setEnabled(False)
        session.close()

    def save_changes(self):
        name = self.input_name.text().strip()
        price = self.input_price.value()
        qty = self.input_qty.value()
        is_weighted = self.check_weighted.isChecked()
        subcat_id = self.combo_subcategory.currentData()
        
        is_box = self.check_is_box.isChecked()
        parent_id = self.combo_parent.currentData() if is_box else None
        units_in_box = self.input_units_in_box.value() if is_box else 1
        
        barcodes_raw = self.input_barcodes.text().split(",")
        barcodes_list = [b.strip() for b in barcodes_raw if b.strip()]
        
        if not name or not subcat_id:
            QMessageBox.warning(self, "خطأ", "الرجاء تحديد الاسم والتصنيف الفرعي")
            return
            
        session = get_session()
        from database import ProductBarcode
        prod = session.query(Product).get(self.product_id)
        if prod:
            prod.name = name
            prod.price = price
            prod.quantity = qty
            prod.is_weighted = is_weighted
            prod.subcategory_id = subcat_id
            prod.parent_id = parent_id
            prod.units_in_box = units_in_box
            
            # تحديث الباركودات: حذف القديم وإضافة الجديد لتجنب التعارض
            session.query(ProductBarcode).filter_by(product_id=self.product_id).delete()
            for bc in barcodes_list:
                # التحقق من عدم وجوده في منتج آخر
                existing = session.query(ProductBarcode).filter_by(barcode=bc).first()
                if existing:
                    continue
                new_bc = ProductBarcode(product_id=prod.id, barcode=bc)
                session.add(new_bc)
                
            session.commit()
            QMessageBox.information(self, "نجاح", "تم تعديل الصنف بنجاح!")
            self.accept()
        session.close()


# ==================== PAGE 2: INVENTORY / PRODUCTS ====================
class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("📦 نظام إدارة الأصناف والتصنيفات")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # نظام التبويبات للأصناف
        self.tabs = QTabWidget()
        
        self.tab_create = QWidget()
        self.tab_edit = QWidget()
        self.tab_categories = QWidget()
        
        self.tabs.addTab(self.tab_create, "➕ إنشاء صنف جديد")
        self.tabs.addTab(self.tab_edit, "✏️ عرض وتعديل الأصناف")
        self.tabs.addTab(self.tab_categories, "📂 الأقسام والتصنيفات الفرعية")
        
        self.setup_create_tab()
        self.setup_edit_tab()
        self.setup_categories_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 0:
            self.load_relations_create()
        elif index == 1:
            self.load_products()
        elif index == 2:
            self.load_categories_lists()

    # --- التبويب الأول: إنشاء صنف جديد ---
    def setup_create_tab(self):
        layout = QFormLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.input_c_name = QLineEdit()
        self.input_c_price = QDoubleSpinBox()
        self.input_c_price.setMaximum(999999.0)
        
        self.input_c_qty = QDoubleSpinBox()
        self.input_c_qty.setMaximum(999999.0)
        
        self.check_c_weighted = QCheckBox("منتج بالوزن / جرامات (مثلاً خضروات، أجبان)")
        
        self.input_c_barcodes = QLineEdit()
        self.input_c_barcodes.setPlaceholderText("أدخل الباركودات مفصولة بفاصلة مثل: 123456, 789012")
        
        self.combo_c_subcategory = QComboBox()
        
        self.check_c_is_box = QCheckBox("هذا الصنف عبارة عن علبة / كرتونة لمنتج آخر")
        self.combo_c_parent = QComboBox()
        self.combo_c_parent.setEnabled(False)
        self.input_c_units_in_box = QSpinBox()
        self.input_c_units_in_box.setValue(1)
        self.input_c_units_in_box.setEnabled(False)
        
        self.check_c_is_box.toggled.connect(self.combo_c_parent.setEnabled)
        self.check_c_is_box.toggled.connect(self.input_c_units_in_box.setEnabled)
        
        btn_save = QPushButton("إنشاء صنف جديد")
        btn_save.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.create_product)
        
        layout.addRow("اسم المنتج:", self.input_c_name)
        layout.addRow("سعر المنتج:", self.input_c_price)
        layout.addRow("الكمية الابتدائية بالمخزن:", self.input_c_qty)
        layout.addRow("الباركودات (مفصولة بـ ,):", self.input_c_barcodes)
        layout.addRow("التصنيف الفرعي (إجباري):", self.combo_c_subcategory)
        layout.addRow("", self.check_c_weighted)
        layout.addRow("", self.check_c_is_box)
        layout.addRow("المنتج الفردي الأب:", self.combo_c_parent)
        layout.addRow("عدد القطع بالعلبة:", self.input_c_units_in_box)
        layout.addRow("", btn_save)
        
        self.tab_create.setLayout(layout)
        self.load_relations_create()

    def load_relations_create(self):
        self.combo_c_subcategory.clear()
        self.combo_c_parent.clear()
        
        session = get_session()
        # تحميل التصنيفات الفرعية
        from database import Subcategory
        subcats = session.query(Subcategory).all()
        for sc in subcats:
            self.combo_c_subcategory.addItem(f"{sc.category.name} ➔ {sc.name}", sc.id)
            
        # تحميل المنتجات الفردية
        products = session.query(Product).all()
        self.combo_c_parent.addItem("لا يوجد (منتج فردي)", None)
        for p in products:
            self.combo_c_parent.addItem(p.name, p.id)
        session.close()

    def create_product(self):
        name = self.input_c_name.text().strip()
        price = self.input_c_price.value()
        qty = self.input_c_qty.value()
        is_weighted = self.check_c_weighted.isChecked()
        subcat_id = self.combo_c_subcategory.currentData()
        
        is_box = self.check_c_is_box.isChecked()
        parent_id = self.combo_c_parent.currentData() if is_box else None
        units_in_box = self.input_c_units_in_box.value() if is_box else 1
        
        barcodes_raw = self.input_c_barcodes.text().split(",")
        barcodes_list = [b.strip() for b in barcodes_raw if b.strip()]
        
        if not name or not subcat_id:
            QMessageBox.warning(self, "تنبيه", "الرجاء تعبئة حقل الاسم والتصنيف الفرعي")
            return
            
        if not barcodes_list:
            QMessageBox.warning(self, "تنبيه", "يرجى إضافة باركود واحد على الأقل")
            return
            
        session = get_session()
        # التأكد من عدم وجود باركود مكرر بالسجلات
        from database import ProductBarcode
        for bc in barcodes_list:
            exists = session.query(ProductBarcode).filter_by(barcode=bc).first()
            if exists:
                QMessageBox.warning(self, "تنبيه", f"الباركود {bc} مستخدم بالفعل لصنف آخر")
                session.close()
                return
                
        # إنشاء الصنف
        new_prod = Product(name=name, price=price, quantity=qty, is_weighted=is_weighted, subcategory_id=subcat_id, parent_id=parent_id, units_in_box=units_in_box)
        session.add(new_prod)
        session.commit()
        
        # إضافة الباركودات
        for bc in barcodes_list:
            new_bc = ProductBarcode(product_id=new_prod.id, barcode=bc)
            session.add(new_bc)
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "نجاح", "تم إنشاء الصنف بنجاح!")
        self.input_c_name.clear()
        self.input_c_price.setValue(0.0)
        self.input_c_qty.setValue(0.0)
        self.input_c_barcodes.clear()
        self.check_c_weighted.setChecked(False)
        self.check_c_is_box.setChecked(False)
        self.load_relations_create()

    # --- التبويب الثاني: عرض وتعديل الأصناف ---
    def setup_edit_tab(self):
        layout = QVBoxLayout()
        
        self.table_edit = QTableWidget()
        self.table_edit.setColumnCount(6)
        self.table_edit.setHorizontalHeaderLabels(["المعرف", "اسم الصنف", "السعر", "الكمية المتاحة", "التصنيف الفرعي", "النوع"])
        self.table_edit.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        btn_modify = QPushButton("✏️ تعديل الصنف المحدد")
        btn_modify.clicked.connect(self.open_edit_dialog)
        btn_modify.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        
        layout.addWidget(self.table_edit)
        layout.addWidget(btn_modify)
        self.tab_edit.setLayout(layout)
        self.load_products()

    def load_products(self):
        self.table_edit.setRowCount(0)
        session = get_session()
        products = session.query(Product).all()
        
        for p in products:
            row = self.table_edit.rowCount()
            self.table_edit.insertRow(row)
            self.table_edit.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table_edit.setItem(row, 1, QTableWidgetItem(p.name))
            self.table_edit.setItem(row, 2, QTableWidgetItem(f"{p.price:.2f}"))
            
            qty_str = f"{p.quantity:.3f}" if p.is_weighted else str(int(p.quantity))
            self.table_edit.setItem(row, 3, QTableWidgetItem(qty_str))
            
            subcat_name = p.subcategory.name if p.subcategory else "غير محدد"
            self.table_edit.setItem(row, 4, QTableWidgetItem(subcat_name))
            
            type_str = "علبة" if p.parent_id else ("بالوزن" if p.is_weighted else "بالقطعة")
            self.table_edit.setItem(row, 5, QTableWidgetItem(type_str))
        session.close()

    def open_edit_dialog(self):
        row = self.table_edit.currentRow()
        if row >= 0:
            product_id = int(self.table_edit.item(row, 0).text())
            dialog = EditProductDialog(product_id, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_products()
        else:
            QMessageBox.warning(self, "تنبيه", "يرجى تحديد صنف لتعديله من الجدول أولاً")

    # --- التبويب الثالث: الأقسام والتصنيفات الفرعية ---
    def setup_categories_tab(self):
        main_layout = QHBoxLayout()
        
        # الجانب الأيمن: الأقسام الرئيسية
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("📂 الأقسام الرئيسية"))
        
        form_cat = QHBoxLayout()
        self.input_cat_name = QLineEdit()
        self.input_cat_name.setPlaceholderText("اسم القسم الرئيسي")
        btn_add_cat = QPushButton("إضافة قسم")
        btn_add_cat.clicked.connect(self.create_category)
        form_cat.addWidget(self.input_cat_name)
        form_cat.addWidget(btn_add_cat)
        left_layout.addLayout(form_cat)
        
        self.table_cats = QTableWidget()
        self.table_cats.setColumnCount(1)
        self.table_cats.setHorizontalHeaderLabels(["القسم"])
        self.table_cats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.table_cats)
        
        # الجانب الأيسر: الأقسام الفرعية
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("🏷️ التصنيفات الفرعية"))
        
        form_sub = QHBoxLayout()
        self.input_sub_name = QLineEdit()
        self.input_sub_name.setPlaceholderText("اسم التصنيف الفرعي")
        self.combo_main_cat = QComboBox()
        btn_add_sub = QPushButton("إضافة فرعي")
        btn_add_sub.clicked.connect(self.create_subcategory)
        
        form_sub.addWidget(self.input_sub_name)
        form_sub.addWidget(self.combo_main_cat)
        form_sub.addWidget(btn_add_sub)
        right_layout.addLayout(form_sub)
        
        self.table_subcats = QTableWidget()
        self.table_subcats.setColumnCount(2)
        self.table_subcats.setHorizontalHeaderLabels(["التصنيف الفرعي", "القسم الرئيسي"])
        self.table_subcats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.table_subcats)
        
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        self.tab_categories.setLayout(main_layout)
        self.load_categories_lists()

    def load_categories_lists(self):
        self.table_cats.setRowCount(0)
        self.table_subcats.setRowCount(0)
        self.combo_main_cat.clear()
        
        session = get_session()
        cats = session.query(Category).all()
        for c in cats:
            row = self.table_cats.rowCount()
            self.table_cats.insertRow(row)
            self.table_cats.setItem(row, 0, QTableWidgetItem(c.name))
            self.combo_main_cat.addItem(c.name, c.id)
            
        from database import Subcategory
        subcats = session.query(Subcategory).all()
        for sc in subcats:
            row = self.table_subcats.rowCount()
            self.table_subcats.insertRow(row)
            self.table_subcats.setItem(row, 0, QTableWidgetItem(sc.name))
            self.table_subcats.setItem(row, 1, QTableWidgetItem(sc.category.name if sc.category else ""))
        session.close()

    def create_category(self):
        name = self.input_cat_name.text().strip()
        if not name:
            return
        session = get_session()
        cat = Category(name=name)
        session.add(cat)
        session.commit()
        session.close()
        self.input_cat_name.clear()
        self.load_categories_lists()

    def create_subcategory(self):
        name = self.input_sub_name.text().strip()
        cat_id = self.combo_main_cat.currentData()
        if not name or not cat_id:
            return
        session = get_session()
        from database import Subcategory
        sub = Subcategory(name=name, category_id=cat_id)
        session.add(sub)
        session.commit()
        session.close()
        self.input_sub_name.clear()
        self.load_categories_lists()


# ==================== PAGE 3: SUPPLIERS ====================
class SuppliersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("👥 نظام إدارة الموردين المتكامل")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # إنشاء نظام التبويبات
        self.tabs = QTabWidget()
        
        # تجهيز صفحات التبويبات
        self.tab_manage = QWidget()
        self.tab_payments = QWidget()
        self.tab_smart_orders = QWidget()
        
        self.tabs.addTab(self.tab_manage, "👤 إضافة وإدارة الموردين")
        self.tabs.addTab(self.tab_payments, "💰 دفعات وحسابات الموردين")
        self.tabs.addTab(self.tab_smart_orders, "🤖 مولد الطلبات الذكي (واتساب)")
        
        # إعداد التبويبات بالتفصيل
        self.setup_manage_tab()
        self.setup_payments_tab()
        self.setup_smart_orders_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # ربط حدث تغيير التبويب لتحديث البيانات
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 0:
            self.load_suppliers()
        elif index == 1:
            self.load_suppliers_combo()
            self.load_transactions()
        elif index == 2:
            self.load_suppliers_order_combo()

    # --- التبويب الأول: إضافة وإدارة الموردين ---
    def setup_manage_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("اسم المورد الجديد")
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("رقم الهاتف (الواتساب)")
        
        self.input_balance = QDoubleSpinBox()
        self.input_balance.setMaximum(9999999.0)
        self.input_balance.setPrefix("الرصيد الابتدائي: ")
        
        btn_add = QPushButton("إضافة مورد")
        btn_add.clicked.connect(self.save_supplier)
        btn_add.setStyleSheet("background-color: #2c3e50;")
        
        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_phone)
        form_layout.addWidget(self.input_balance)
        form_layout.addWidget(btn_add)
        
        layout.addWidget(form_widget)
        
        self.table_suppliers = QTableWidget()
        self.table_suppliers.setColumnCount(3)
        self.table_suppliers.setHorizontalHeaderLabels(["اسم المورد", "رقم الهاتف", "الرصيد الحالي المستحق"])
        self.table_suppliers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_suppliers)
        
        self.tab_manage.setLayout(layout)
        self.load_suppliers()

    def load_suppliers(self):
        self.table_suppliers.setRowCount(0)
        session = get_session()
        suppliers = session.query(Supplier).all()
        session.close()
        
        for sup in suppliers:
            row = self.table_suppliers.rowCount()
            self.table_suppliers.insertRow(row)
            self.table_suppliers.setItem(row, 0, QTableWidgetItem(sup.name))
            self.table_suppliers.setItem(row, 1, QTableWidgetItem(sup.phone if sup.phone else ""))
            self.table_suppliers.setItem(row, 2, QTableWidgetItem(f"{sup.balance:.2f}"))

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

    # --- التبويب الثاني: دفعات الموردين ---
    def setup_payments_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.combo_suppliers = QComboBox()
        self.load_suppliers_combo()
        
        self.input_pay_amount = QDoubleSpinBox()
        self.input_pay_amount.setMaximum(9999999.0)
        self.input_pay_amount.setPrefix("المبلغ: ")
        
        self.combo_pay_type = QComboBox()
        self.combo_pay_type.addItems(["دفعة مسددة له (Pay Out)", "دين بضاعة جديدة (Purchase)"])
        
        self.input_pay_note = QLineEdit()
        self.input_pay_note.setPlaceholderText("ملاحظات / رقم الفاتورة")
        
        btn_pay = QPushButton("سجل الحركة المالية")
        btn_pay.clicked.connect(self.save_transaction)
        btn_pay.setStyleSheet("background-color: #27ae60;")
        
        form_layout.addWidget(self.combo_suppliers)
        form_layout.addWidget(self.input_pay_amount)
        form_layout.addWidget(self.combo_pay_type)
        form_layout.addWidget(self.input_pay_note)
        form_layout.addWidget(btn_pay)
        
        layout.addWidget(form_widget)
        
        self.table_transactions = QTableWidget()
        self.table_transactions.setColumnCount(5)
        self.table_transactions.setHorizontalHeaderLabels(["المورد", "المبلغ", "النوع", "التاريخ والوقت", "الملاحظات"])
        self.table_transactions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_transactions)
        
        self.tab_payments.setLayout(layout)
        self.load_transactions()

    def load_suppliers_combo(self):
        self.combo_suppliers.clear()
        session = get_session()
        suppliers = session.query(Supplier).all()
        session.close()
        for sup in suppliers:
            self.combo_suppliers.addItem(sup.name, sup.id)

    def load_transactions(self):
        self.table_transactions.setRowCount(0)
        from database import SupplierTransaction
        session = get_session()
        txs = session.query(SupplierTransaction).order_by(SupplierTransaction.date.desc()).all()
        
        for t in txs:
            row = self.table_transactions.rowCount()
            self.table_transactions.insertRow(row)
            self.table_transactions.setItem(row, 0, QTableWidgetItem(t.supplier.name if t.supplier else "غير معروف"))
            self.table_transactions.setItem(row, 1, QTableWidgetItem(f"{t.amount:.2f}"))
            
            type_str = "مسدد له ⬇️" if t.type == "pay_out" else "شراء بالدين ⬆️"
            self.table_transactions.setItem(row, 2, QTableWidgetItem(type_str))
            self.table_transactions.setItem(row, 3, QTableWidgetItem(t.date.strftime("%Y-%m-%d %H:%M")))
            self.table_transactions.setItem(row, 4, QTableWidgetItem(t.note if t.note else ""))
        session.close()

    def save_transaction(self):
        supplier_id = self.combo_suppliers.currentData()
        amount = self.input_pay_amount.value()
        type_index = self.combo_pay_type.currentIndex()
        note = self.input_pay_note.text().strip()
        
        if not supplier_id or amount <= 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار المورد وتحديد مبلغ صحيح")
            return
            
        type_code = "pay_out" if type_index == 0 else "purchase_in"
        
        from database import SupplierTransaction
        session = get_session()
        sup = session.query(Supplier).get(supplier_id)
        if not sup:
            session.close()
            return
            
        # تحديث رصيد المورد
        if type_code == "pay_out":
            sup.balance -= amount # قمنا بتسديد الدين فقل رصيده لدينا
        else:
            sup.balance += amount # اشترينا بضاعة جديدة بالدين فزاد رصيده
            
        tx = SupplierTransaction(supplier_id=supplier_id, amount=amount, type=type_code, note=note)
        session.add(tx)
        session.commit()
        session.close()
        
        QMessageBox.information(self, "نجاح", "تم تسجيل الحركة وتحديث رصيد المورد بنجاح!")
        self.input_pay_amount.setValue(0.0)
        self.input_pay_note.clear()
        self.load_transactions()

    # --- التبويب الثالث: نظام الطلبات الذكي ---
    def setup_smart_orders_tab(self):
        layout = QVBoxLayout()
        
        controls = QHBoxLayout()
        self.input_threshold = QSpinBox()
        self.input_threshold.setPrefix("حد التنبيه للكمية المتاحة: ")
        self.input_threshold.setValue(5)
        
        btn_generate = QPushButton("🤖 توليد طلبية ذكية")
        btn_generate.setStyleSheet("background-color: #e67e22; color: white;")
        btn_generate.clicked.connect(self.generate_smart_order)
        
        self.combo_order_suppliers = QComboBox()
        self.load_suppliers_order_combo()
        
        btn_whatsapp = QPushButton("💬 مشاركة الطلب عبر واتساب")
        btn_whatsapp.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_whatsapp.clicked.connect(self.share_via_whatsapp)
        
        controls.addWidget(self.input_threshold, 1)
        controls.addWidget(btn_generate, 1)
        controls.addWidget(self.combo_order_suppliers, 2)
        controls.addWidget(btn_whatsapp, 2)
        
        layout.addLayout(controls)
        
        self.table_order = QTableWidget()
        self.table_order.setColumnCount(4)
        self.table_order.setHorizontalHeaderLabels(["اسم الصنف", "الكمية المتاحة", "الحد الأدنى", "الكمية المقترحة لطلبها"])
        self.table_order.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_order)
        
        self.tab_smart_orders.setLayout(layout)

    def load_suppliers_order_combo(self):
        self.combo_order_suppliers.clear()
        session = get_session()
        suppliers = session.query(Supplier).all()
        session.close()
        for sup in suppliers:
            # تخزين رقم الهاتف كبيانات إضافية
            phone = sup.phone if sup.phone else ""
            self.combo_order_suppliers.addItem(f"{sup.name} ({phone})", phone)

    def generate_smart_order(self):
        threshold = self.input_threshold.value()
        self.table_order.setRowCount(0)
        
        session = get_session()
        # جلب المنتجات التي كميتها تساوي أو تقل عن الحد المطلوب
        low_stock_products = session.query(Product).filter(Product.quantity <= threshold).all()
        session.close()
        
        if not low_stock_products:
            QMessageBox.information(self, "حالة جيدة", "لا توجد بضائع ناقصة في المتجر حالياً!")
            return
            
        for prod in low_stock_products:
            row = self.table_order.rowCount()
            self.table_order.insertRow(row)
            self.table_order.setItem(row, 0, QTableWidgetItem(prod.name))
            self.table_order.setItem(row, 1, QTableWidgetItem(f"{prod.quantity:.2f}" if prod.is_weighted else str(int(prod.quantity))))
            self.table_order.setItem(row, 2, QTableWidgetItem(str(threshold)))
            
            # حساب الكمية المقترحة لطلبها لإكمال النقص (مثلاً 20 قطعة أو 20 كجم كافتراضي)
            suggested = max(20.0 - prod.quantity, 5.0)
            suggested_str = f"{suggested:.2f}" if prod.is_weighted else str(int(suggested))
            self.table_order.setItem(row, 3, QTableWidgetItem(suggested_str))

    def share_via_whatsapp(self):
        row_count = self.table_order.rowCount()
        if row_count == 0:
            QMessageBox.warning(self, "تنبيه", "يرجى توليد الطلبية أولاً!")
            return
            
        supplier_phone = self.combo_order_suppliers.currentData()
        supplier_name = self.combo_order_suppliers.currentText().split(" (")[0]
        
        # تكوين رسالة نصية مرتبة لطلب البضائع
        message = f"السلام عليكم ورحمة الله وبركاته،\n"
        message += f"طلب بضاعة جديد لـ *سوبر ماركت المنزل السوري*.\n"
        message += f"المورد المحترم: *{supplier_name}*\n"
        message += f"يرجى توفير وتجهيز الأصناف الناقصة التالية:\n\n"
        
        for row in range(row_count):
            prod_name = self.table_order.item(row, 0).text()
            qty_needed = self.table_order.item(row, 3).text()
            message += f"▫️ *{prod_name}* -> الكمية المطلوبة: {qty_needed}\n"
            
        message += f"\nوشكراً جزيلاً لكم."
        
        # تشفير الرسالة لفتح رابط واتساب
        import urllib.parse
        import webbrowser
        
        encoded_msg = urllib.parse.quote(message)
        
        if supplier_phone:
            # تنظيف رقم الهاتف من الرموز والمسافات
            clean_phone = "".join(filter(str.isdigit, supplier_phone))
            url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        else:
            url = f"https://api.whatsapp.com/send?text={encoded_msg}"
            
        webbrowser.open(url)


# ==================== PAGE 4: REPORTS & SALES (ADMIN ONLY) ====================
# ==================== ANALYTICS CHART WIDGET ====================
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen

class AnalyticsChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sales = 0.0
        self.purchases = 0.0
        self.expenses = 0.0
        self.salaries = 0.0
        self.profits = 0.0
        self.setMinimumHeight(250)

    def set_data(self, sales, purchases, expenses, salaries, profits):
        self.sales = sales
        self.purchases = purchases
        self.expenses = expenses
        self.salaries = salaries
        self.profits = profits
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_dark = self.parent().parent().parent().parent().dark_mode if (hasattr(self.parent().parent().parent().parent(), 'dark_mode')) else True
        
        # Background
        painter.fillRect(self.rect(), QColor("#1e293b") if is_dark else QColor("#ffffff"))
        
        labels = ["المبيعات", "المشتريات", "المصاريف", "الرواتب", "الأرباح"]
        values = [self.sales, self.purchases, self.expenses, self.salaries, self.profits]
        colors = [
            QColor("#10b981"),
            QColor("#3b82f6"),
            QColor("#ef4444"),
            QColor("#f59e0b"),
            QColor("#8b5cf6")
        ]
        
        max_val = max(max(values), 1.0)
        
        width = self.width()
        height = self.height()
        
        margin_left = 70
        margin_bottom = 40
        margin_top = 25
        margin_right = 20
        
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom
        
        # Draw Y-Axis lines
        pen = QPen(QColor("#475569") if is_dark else QColor("#cbd5e1"), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for i in range(5):
            y = margin_top + plot_height * (i / 4)
            painter.drawLine(margin_left, int(y), width - margin_right, int(y))
            val_label = max_val * (1.0 - i / 4)
            painter.drawText(15, int(y) + 5, f"{val_label:.0f}")
            
        # Draw Bars
        bar_count = len(labels)
        bar_width = int(plot_width / (bar_count * 1.8))
        gap = int((plot_width - bar_width * bar_count) / (bar_count + 1))
        
        for i in range(bar_count):
            val = values[i]
            bar_height = int(plot_height * (max(val, 0.0) / max_val))
            
            x = margin_left + gap + i * (bar_width + gap)
            y = margin_top + plot_height - bar_height
            
            # Fill Bar
            painter.setBrush(QBrush(colors[i]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 6, 6)
            
            # Draw Value Label on top of Bar
            painter.setPen(QColor("#cbd5e1") if is_dark else QColor("#1e293b"))
            painter.drawText(x + 5, y - 5, f"{val:.0f}")
            
            # Draw Label at bottom of Bar
            painter.drawText(x + 5, margin_top + plot_height + 22, labels[i])


# ==================== PAGE 4: REPORTS & SALES (ADMIN ONLY) ====================
class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        top_layout = QHBoxLayout()
        header = QLabel("📈 التقارير المالية والتحليلات")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        
        filter_group = QGroupBox("تصفية بالتواريخ")
        filter_layout = QHBoxLayout(filter_group)
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        import datetime
        today = datetime.date.today()
        self.date_from.setDate(today.replace(day=1))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(today)
        
        btn_refresh = QPushButton("تحديث البيانات 🔄")
        btn_refresh.clicked.connect(self.load_reports)
        btn_refresh.setStyleSheet("background-color: #2c3e50; color: white;")
        
        btn_export = QPushButton("تصدير للتميز Excel 📥")
        btn_export.clicked.connect(self.export_to_csv)
        btn_export.setStyleSheet("background-color: #10b981; color: white; font-weight: bold;")
        
        filter_layout.addWidget(QLabel("من:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("إلى:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_export)
        
        top_layout.addWidget(header, 2)
        top_layout.addWidget(filter_group, 3)
        layout.addLayout(top_layout)
        
        self.tabs = QTabWidget()
        self.tab_dashboard = QWidget()
        self.tab_sales = QWidget()
        self.tab_purchases = QWidget()
        self.tab_expenses = QWidget()
        
        self.tabs.addTab(self.tab_dashboard, "📊 لوحة الأرباح والرسوم البيانية")
        self.tabs.addTab(self.tab_sales, "🛒 سجل المبيعات والفواتير")
        self.tabs.addTab(self.tab_purchases, "📥 سجل حركات المشتريات")
        self.tabs.addTab(self.tab_expenses, "💸 إدارة وتسجيل المصاريف")
        
        self.setup_dashboard_tab()
        self.setup_sales_tab()
        self.setup_purchases_tab()
        self.setup_expenses_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def setup_dashboard_tab(self):
        layout = QVBoxLayout()
        
        cards_layout = QHBoxLayout()
        
        self.card_sales = QLabel("إجمالي المبيعات\n0.00 ل.س")
        self.card_sales.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_sales.setStyleSheet("background-color: #10b981; color: white; font-size: 15px; font-weight: bold; padding: 15px; border-radius: 8px;")
        
        self.card_purchases = QLabel("إجمالي المشتريات\n0.00 ل.س")
        self.card_purchases.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_purchases.setStyleSheet("background-color: #3b82f6; color: white; font-size: 15px; font-weight: bold; padding: 15px; border-radius: 8px;")
        
        self.card_expenses = QLabel("إجمالي المصاريف\n0.00 ل.س")
        self.card_expenses.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_expenses.setStyleSheet("background-color: #ef4444; color: white; font-size: 15px; font-weight: bold; padding: 15px; border-radius: 8px;")
        
        self.card_salaries = QLabel("رواتب الموظفين\n0.00 ل.س")
        self.card_salaries.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_salaries.setStyleSheet("background-color: #f59e0b; color: white; font-size: 15px; font-weight: bold; padding: 15px; border-radius: 8px;")
        
        self.card_profits = QLabel("الأرباح الصافية\n0.00 ل.س")
        self.card_profits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_profits.setStyleSheet("background-color: #8b5cf6; color: white; font-size: 15px; font-weight: bold; padding: 15px; border-radius: 8px;")
        
        cards_layout.addWidget(self.card_sales)
        cards_layout.addWidget(self.card_purchases)
        cards_layout.addWidget(self.card_expenses)
        cards_layout.addWidget(self.card_salaries)
        cards_layout.addWidget(self.card_profits)
        layout.addLayout(cards_layout)
        
        layout.addWidget(QLabel("📈 رسم بياني للمقارنة المالية:"))
        self.chart = AnalyticsChartWidget(self)
        layout.addWidget(self.chart)
        
        self.tab_dashboard.setLayout(layout)

    def setup_sales_tab(self):
        layout = QVBoxLayout()
        self.table_sales = QTableWidget()
        self.table_sales.setColumnCount(5)
        self.table_sales.setHorizontalHeaderLabels(["رقم الفاتورة", "التاريخ والوقت", "العميل", "طريقة الدفع", "الإجمالي"])
        self.table_sales.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_sales.doubleClicked.connect(self.show_sales_invoice_details)
        layout.addWidget(self.table_sales)
        self.tab_sales.setLayout(layout)

    def show_sales_invoice_details(self):
        row = self.table_sales.currentRow()
        if row >= 0:
            inv_id = int(self.table_sales.item(row, 0).text().replace("#", ""))
            dialog = ReceiptDialog(inv_id, self)
            dialog.exec()

    def setup_purchases_tab(self):
        layout = QVBoxLayout()
        self.table_purchases = QTableWidget()
        self.table_purchases.setColumnCount(5)
        self.table_purchases.setHorizontalHeaderLabels(["المورد", "المبلغ", "النوع", "التاريخ والوقت", "الملاحظات"])
        self.table_purchases.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_purchases)
        self.tab_purchases.setLayout(layout)

    def setup_expenses_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_exp_amount = QDoubleSpinBox()
        self.input_exp_amount.setMaximum(999999.0)
        self.input_exp_amount.setPrefix("قيمة المصروف: ")
        
        self.combo_exp_cat = QComboBox()
        self.combo_exp_cat.addItems(["كهرباء ومياه", "إيجار المحل", "صيانة وإصلاحات", "نقل وتوصيل", "رواتب طارئة", "أخرى"])
        
        self.input_exp_note = QLineEdit()
        self.input_exp_note.setPlaceholderText("ملاحظات / فواتير المصاريف...")
        
        btn_add_exp = QPushButton("سجل المصروف 💸")
        btn_add_exp.clicked.connect(self.save_expense)
        btn_add_exp.setStyleSheet("background-color: #ef4444; color: white;")
        
        form_layout.addWidget(self.input_exp_amount)
        form_layout.addWidget(self.combo_exp_cat)
        form_layout.addWidget(self.input_exp_note)
        form_layout.addWidget(btn_add_exp)
        layout.addWidget(form_widget)
        
        self.table_expenses = QTableWidget()
        self.table_expenses.setColumnCount(4)
        self.table_expenses.setHorizontalHeaderLabels(["القيمة", "التصنيف", "التاريخ والوقت", "الملاحظات"])
        self.table_expenses.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_expenses)
        
        self.tab_expenses.setLayout(layout)

    def save_expense(self):
        amount = self.input_exp_amount.value()
        category = self.combo_exp_cat.currentText()
        note = self.input_exp_note.text().strip()
        
        if amount <= 0:
            QMessageBox.warning(self, "تنبيه", "يرجى تحديد مبلغ مصروف صحيح")
            return
            
        session = get_session()
        from database import Expense
        exp = Expense(amount=amount, category=category, note=note)
        session.add(exp)
        session.commit()
        session.close()
        
        QMessageBox.information(self, "نجاح", "تم تسجيل المصروف بنجاح!")
        self.input_exp_amount.setValue(0.0)
        self.input_exp_note.clear()
        self.load_reports()

    def load_reports(self):
        dt_from = self.date_from.date().toPyDate()
        dt_to = self.date_to.date().toPyDate()
        
        import datetime
        datetime_from = datetime.datetime.combine(dt_from, datetime.time.min)
        datetime_to = datetime.datetime.combine(dt_to, datetime.time.max)
        
        session = get_session()
        from database import Invoice, SupplierTransaction, Expense, EmployeeTransaction, InvoiceItem
        
        sales_query = session.query(Invoice).filter(Invoice.date >= datetime_from, Invoice.date <= datetime_to).all()
        total_sales = sum(inv.total for inv in sales_query)
        
        purchases_query = session.query(SupplierTransaction).filter(
            SupplierTransaction.type == 'purchase_in',
            SupplierTransaction.date >= datetime_from,
            SupplierTransaction.date <= datetime_to
        ).all()
        total_purchases = sum(p.amount for p in purchases_query)
        
        expenses_query = session.query(Expense).filter(Expense.date >= datetime_from, Expense.date <= datetime_to).all()
        total_expenses = sum(exp.amount for exp in expenses_query)
        
        salaries_query = session.query(EmployeeTransaction).filter(
            EmployeeTransaction.type == 'salary_payment',
            EmployeeTransaction.date >= datetime_from,
            EmployeeTransaction.date <= datetime_to
        ).all()
        total_salaries = sum(s.amount for s in salaries_query)
        
        total_cost_of_goods = 0.0
        invoice_ids = [inv.id for inv in sales_query]
        if invoice_ids:
            items_query = session.query(InvoiceItem).filter(InvoiceItem.invoice_id.in_(invoice_ids)).all()
            total_cost_of_goods = sum(item.cost_price * item.quantity for item in items_query)
            
        net_profits = total_sales - total_cost_of_goods - total_expenses - total_salaries
        
        self.card_sales.setText(f"إجمالي المبيعات\n{total_sales:.2f} ل.س")
        self.card_purchases.setText(f"إجمالي المشتريات\n{total_purchases:.2f} ل.س")
        self.card_expenses.setText(f"إجمالي المصاريف\n{total_expenses:.2f} ل.س")
        self.card_salaries.setText(f"رواتب الموظفين\n{total_salaries:.2f} ل.س")
        self.card_profits.setText(f"الأرباح الصافية\n{net_profits:.2f} ل.س")
        
        self.chart.set_data(total_sales, total_purchases, total_expenses, total_salaries, net_profits)
        
        self.table_sales.setRowCount(0)
        for inv in sales_query:
            row = self.table_sales.rowCount()
            self.table_sales.insertRow(row)
            self.table_sales.setItem(row, 0, QTableWidgetItem(f"#{inv.id}"))
            self.table_sales.setItem(row, 1, QTableWidgetItem(inv.date.strftime("%Y-%m-%d %H:%M")))
            self.table_sales.setItem(row, 2, QTableWidgetItem(inv.customer_name if inv.customer_name else "عميل سفري"))
            self.table_sales.setItem(row, 3, QTableWidgetItem(inv.payment_method))
            self.table_sales.setItem(row, 4, QTableWidgetItem(f"{inv.total:.2f}"))
            
        self.table_purchases.setRowCount(0)
        for p in purchases_query:
            row = self.table_purchases.rowCount()
            self.table_purchases.insertRow(row)
            self.table_purchases.setItem(row, 0, QTableWidgetItem(p.supplier.name if p.supplier else "مورد غير معروف"))
            self.table_purchases.setItem(row, 1, QTableWidgetItem(f"{p.amount:.2f}"))
            self.table_purchases.setItem(row, 2, QTableWidgetItem("شراء بالدين"))
            self.table_purchases.setItem(row, 3, QTableWidgetItem(p.date.strftime("%Y-%m-%d %H:%M")))
            self.table_purchases.setItem(row, 4, QTableWidgetItem(p.note if p.note else ""))
            
        self.table_expenses.setRowCount(0)
        for exp in expenses_query:
            row = self.table_expenses.rowCount()
            self.table_expenses.insertRow(row)
            self.table_expenses.setItem(row, 0, QTableWidgetItem(f"{exp.amount:.2f}"))
            self.table_expenses.setItem(row, 1, QTableWidgetItem(exp.category))
            self.table_expenses.setItem(row, 2, QTableWidgetItem(exp.date.strftime("%Y-%m-%d %H:%M")))
            self.table_expenses.setItem(row, 3, QTableWidgetItem(exp.note if exp.note else ""))
            
        session.close()

    def export_to_csv(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "حفظ التقرير كـ CSV", "", "CSV Files (*.csv)")
        if not filename:
            return
            
        import csv
        session = get_session()
        from database import Invoice, SupplierTransaction, Expense, EmployeeTransaction, InvoiceItem
        
        dt_from = self.date_from.date().toPyDate()
        dt_to = self.date_to.date().toPyDate()
        import datetime
        datetime_from = datetime.datetime.combine(dt_from, datetime.time.min)
        datetime_to = datetime.datetime.combine(dt_to, datetime.time.max)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["تقرير مالي شامل لـ كاشير المنزل السوري"])
                writer.writerow([f"الفترة من: {dt_from} إلى: {dt_to}"])
                writer.writerow([])
                
                sales_query = session.query(Invoice).filter(Invoice.date >= datetime_from, Invoice.date <= datetime_to).all()
                total_sales = sum(inv.total for inv in sales_query)
                
                purchases_query = session.query(SupplierTransaction).filter(SupplierTransaction.type == 'purchase_in', SupplierTransaction.date >= datetime_from, SupplierTransaction.date <= datetime_to).all()
                total_purchases = sum(p.amount for p in purchases_query)
                
                expenses_query = session.query(Expense).filter(Expense.date >= datetime_from, Expense.date <= datetime_to).all()
                total_expenses = sum(exp.amount for exp in expenses_query)
                
                salaries_query = session.query(EmployeeTransaction).filter(EmployeeTransaction.type == 'salary_payment', EmployeeTransaction.date >= datetime_from, EmployeeTransaction.date <= datetime_to).all()
                total_salaries = sum(s.amount for s in salaries_query)
                
                total_cost_of_goods = 0.0
                invoice_ids = [inv.id for inv in sales_query]
                if invoice_ids:
                    items_query = session.query(InvoiceItem).filter(InvoiceItem.invoice_id.in_(invoice_ids)).all()
                    total_cost_of_goods = sum(item.cost_price * item.quantity for item in items_query)
                net_profits = total_sales - total_cost_of_goods - total_expenses - total_salaries
                
                writer.writerow(["--- ملخص الميزانية والأرباح ---"])
                writer.writerow(["إجمالي المبيعات", f"{total_sales:.2f} ل.س"])
                writer.writerow(["إجمالي تكلفة المبيعات", f"{total_cost_of_goods:.2f} ل.س"])
                writer.writerow(["إجمالي مشتريات البضاعة", f"{total_purchases:.2f} ل.س"])
                writer.writerow(["إجمالي المصاريف والتشغيل", f"{total_expenses:.2f} ل.س"])
                writer.writerow(["رواتب الموظفين", f"{total_salaries:.2f} ل.س"])
                writer.writerow(["الأرباح الصافية (Net Profit)", f"{net_profits:.2f} ل.س"])
                writer.writerow([])
                
                writer.writerow(["--- سجل الفواتير والمبيعات ---"])
                writer.writerow(["رقم الفاتورة", "التاريخ", "العميل", "طريقة الدفع", "الإجمالي"])
                for inv in sales_query:
                    writer.writerow([inv.id, inv.date.strftime("%Y-%m-%d %H:%M"), inv.customer_name if inv.customer_name else "عميل سفري", inv.payment_method, inv.total])
                
            QMessageBox.information(self, "نجاح التصدير", "تم تصدير التقرير المالي كملف CSV لـ Excel بنجاح!")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تصدير الملف: {str(e)}")
        finally:
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


# ==================== PAGE 6: HR / EMPLOYEES ====================
class HRPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("👤 إدارة الموارد البشرية وشؤون الموظفين (HR)")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # إنشاء نظام التبويبات
        self.tabs = QTabWidget()
        
        self.tab_employees = QWidget()
        self.tab_payments = QWidget()
        
        self.tabs.addTab(self.tab_employees, "👥 ملفات الموظفين")
        self.tabs.addTab(self.tab_payments, "💰 الرواتب والخصومات والمكافآت")
        
        self.setup_employees_tab()
        self.setup_payments_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 0:
            self.load_employees()
        elif index == 1:
            self.load_employees_combo()
            self.load_transactions()

    # --- التبويب الأول: ملفات الموظفين ---
    def setup_employees_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_emp_name = QLineEdit()
        self.input_emp_name.setPlaceholderText("اسم الموظف الجديد")
        self.input_emp_phone = QLineEdit()
        self.input_emp_phone.setPlaceholderText("رقم الهاتف")
        
        self.combo_emp_role = QComboBox()
        self.combo_emp_role.addItem("ديلفري (طيار)", "delivery")
        self.combo_emp_role.addItem("كاشير", "cashier")
        self.combo_emp_role.addItem("أخرى", "other")
        
        self.input_emp_salary = QDoubleSpinBox()
        self.input_emp_salary.setMaximum(999999.0)
        self.input_emp_salary.setPrefix("الراتب الأساسي: ")
        
        btn_add = QPushButton("حفظ الموظف")
        btn_add.clicked.connect(self.save_employee)
        btn_add.setStyleSheet("background-color: #2c3e50;")
        
        form_layout.addWidget(self.input_emp_name)
        form_layout.addWidget(self.input_emp_phone)
        form_layout.addWidget(self.combo_emp_role)
        form_layout.addWidget(self.input_emp_salary)
        form_layout.addWidget(btn_add)
        
        layout.addWidget(form_widget)
        
        self.table_employees = QTableWidget()
        self.table_employees.setColumnCount(5)
        self.table_employees.setHorizontalHeaderLabels(["المعرف", "الاسم", "رقم الهاتف", "الوظيفة", "الراتب"])
        self.table_employees.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_employees.doubleClicked.connect(self.load_row_to_emp_form)
        layout.addWidget(self.table_employees)
        
        # أزرار التعديل والحذف
        buttons_layout = QHBoxLayout()
        
        btn_delete = QPushButton("❌ حذف الموظف المحدد")
        btn_delete.clicked.connect(self.delete_employee)
        btn_delete.setObjectName("dangerButton")
        
        buttons_layout.addWidget(btn_delete)
        layout.addLayout(buttons_layout)
        
        self.tab_employees.setLayout(layout)
        self.load_employees()

    def load_employees(self):
        self.table_employees.setRowCount(0)
        session = get_session()
        from database import Employee
        employees = session.query(Employee).all()
        session.close()
        
        for emp in employees:
            row = self.table_employees.rowCount()
            self.table_employees.insertRow(row)
            self.table_employees.setItem(row, 0, QTableWidgetItem(str(emp.id)))
            self.table_employees.setItem(row, 1, QTableWidgetItem(emp.name))
            self.table_employees.setItem(row, 2, QTableWidgetItem(emp.phone if emp.phone else ""))
            
            role_map = {"delivery": "ديلفري (طيار)", "cashier": "كاشير", "other": "أخرى"}
            self.table_employees.setItem(row, 3, QTableWidgetItem(role_map.get(emp.role, emp.role)))
            self.table_employees.setItem(row, 4, QTableWidgetItem(f"{emp.salary:.2f}"))

    def save_employee(self):
        name = self.input_emp_name.text().strip()
        phone = self.input_emp_phone.text().strip()
        role = self.combo_emp_role.currentData()
        salary = self.input_emp_salary.value()
        
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم الموظف")
            return
            
        session = get_session()
        from database import Employee
        emp = session.query(Employee).filter_by(name=name).first()
        if emp:
            emp.phone = phone
            emp.role = role
            emp.salary = salary
        else:
            emp = Employee(name=name, phone=phone, role=role, salary=salary)
            session.add(emp)
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "تم الحفظ", "تم حفظ بيانات الموظف بنجاح!")
        self.input_emp_name.clear()
        self.input_emp_phone.clear()
        self.input_emp_salary.setValue(0.0)
        self.load_employees()

    def load_row_to_emp_form(self):
        row = self.table_employees.currentRow()
        if row >= 0:
            self.input_emp_name.setText(self.table_employees.item(row, 1).text())
            self.input_emp_phone.setText(self.table_employees.item(row, 2).text())
            
            role_text = self.table_employees.item(row, 3).text()
            role_map_rev = {"ديلفري (طيار)": "delivery", "كاشير": "cashier", "أخرى": "other"}
            idx = self.combo_emp_role.findData(role_map_rev.get(role_text, "other"))
            if idx >= 0:
                self.combo_emp_role.setCurrentIndex(idx)
                
            self.input_emp_salary.setValue(float(self.table_employees.item(row, 4).text()))

    def delete_employee(self):
        row = self.table_employees.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار موظف لحذفه أولاً")
            return
            
        emp_id = int(self.table_employees.item(row, 0).text())
        emp_name = self.table_employees.item(row, 1).text()
        
        reply = QMessageBox.question(self, "تأكيد الحذف", f"هل أنت متأكد من حذف الموظف: {emp_name}؟",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            from database import Employee
            emp = session.query(Employee).get(emp_id)
            if emp:
                session.delete(emp)
                session.commit()
            session.close()
            
            QMessageBox.information(self, "تم الحذف", "تم حذف الموظف بنجاح!")
            self.load_employees()

    # --- التبويب الثاني: الحركات المالية ---
    def setup_payments_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.combo_pay_employees = QComboBox()
        self.load_employees_combo()
        
        self.input_trans_amount = QDoubleSpinBox()
        self.input_trans_amount.setMaximum(999999.0)
        self.input_trans_amount.setPrefix("المبلغ: ")
        
        self.combo_trans_type = QComboBox()
        self.combo_trans_type.addItem("دفع راتب", "salary_payment")
        self.combo_trans_type.addItem("تسجيل خصم/جزاء", "deduction")
        self.combo_trans_type.addItem("مكافأة/جائزة", "reward")
        
        self.input_trans_note = QLineEdit()
        self.input_trans_note.setPlaceholderText("ملاحظات / سبب الخصم أو الجائزة")
        
        btn_trans_save = QPushButton("سجل المعاملة المالية")
        btn_trans_save.clicked.connect(self.save_employee_transaction)
        btn_trans_save.setStyleSheet("background-color: #27ae60;")
        
        form_layout.addWidget(self.combo_pay_employees)
        form_layout.addWidget(self.input_trans_amount)
        form_layout.addWidget(self.combo_trans_type)
        form_layout.addWidget(self.input_trans_note)
        form_layout.addWidget(btn_trans_save)
        
        layout.addWidget(form_widget)
        
        self.table_emp_transactions = QTableWidget()
        self.table_emp_transactions.setColumnCount(5)
        self.table_emp_transactions.setHorizontalHeaderLabels(["الموظف", "المبلغ", "النوع", "التاريخ والوقت", "الملاحظات"])
        self.table_emp_transactions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_emp_transactions)
        
        self.tab_payments.setLayout(layout)
        self.load_transactions()

    def load_employees_combo(self):
        self.combo_pay_employees.clear()
        session = get_session()
        from database import Employee
        employees = session.query(Employee).all()
        session.close()
        for emp in employees:
            self.combo_pay_employees.addItem(emp.name, emp.id)

    def load_transactions(self):
        self.table_emp_transactions.setRowCount(0)
        session = get_session()
        from database import EmployeeTransaction
        txs = session.query(EmployeeTransaction).order_by(EmployeeTransaction.date.desc()).all()
        
        for t in txs:
            row = self.table_emp_transactions.rowCount()
            self.table_emp_transactions.insertRow(row)
            self.table_emp_transactions.setItem(row, 0, QTableWidgetItem(t.employee.name if t.employee else "غير معروف"))
            self.table_emp_transactions.setItem(row, 1, QTableWidgetItem(f"{t.amount:.2f}"))
            
            type_map = {"salary_payment": "دفع راتب 💵", "deduction": "خصم/جزاء 📉", "reward": "مكافأة/جائزة 📈"}
            self.table_emp_transactions.setItem(row, 2, QTableWidgetItem(type_map.get(t.type, t.type)))
            self.table_emp_transactions.setItem(row, 3, QTableWidgetItem(t.date.strftime("%Y-%m-%d %H:%M")))
            self.table_emp_transactions.setItem(row, 4, QTableWidgetItem(t.note if t.note else ""))
        session.close()

    def save_employee_transaction(self):
        emp_id = self.combo_pay_employees.currentData()
        amount = self.input_trans_amount.value()
        trans_type = self.combo_trans_type.currentData()
        note = self.input_trans_note.text().strip()
        
        if not emp_id or amount <= 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار موظف وتحديد مبلغ صحيح")
            return
            
        session = get_session()
        from database import EmployeeTransaction
        tx = EmployeeTransaction(employee_id=emp_id, amount=amount, type=trans_type, note=note)
        session.add(tx)
        session.commit()
        session.close()
        
        QMessageBox.information(self, "نجاح", "تم تسجيل المعاملة المالية للموظف بنجاح!")
        self.input_trans_amount.setValue(0.0)
        self.input_trans_note.clear()
        self.load_transactions()


# ==================== INVOICE ARCHIVE DIALOG ====================
class InvoiceArchiveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("أرشيف فواتير المبيعات 📜")
        self.resize(700, 500)
        self.selected_invoice_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث برقم الفاتورة أو اسم العميل...")
        self.search_input.textChanged.connect(self.load_invoices)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "التاريخ والوقت", "العميل", "طريقة الدفع", "الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.select_invoice)
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_select = QPushButton("تحميل الفاتورة للمرتجع ↩️")
        btn_select.clicked.connect(self.select_invoice)
        btn_select.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        
        btn_cancel = QPushButton("إغلاق")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_select)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_invoices()

    def load_invoices(self):
        self.table.setRowCount(0)
        search_txt = self.search_input.text().strip()
        
        session = get_session()
        from database import Invoice
        query = session.query(Invoice)
        if search_txt:
            if search_txt.isdigit():
                query = query.filter(Invoice.id == int(search_txt))
            else:
                query = query.filter(Invoice.customer_name.like(f"%{search_txt}%"))
                
        invoices = query.order_by(Invoice.date.desc()).all()
        
        for inv in invoices:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"#{inv.id}"))
            self.table.setItem(row, 1, QTableWidgetItem(inv.date.strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(row, 2, QTableWidgetItem(inv.customer_name if inv.customer_name else "عميل سفري"))
            self.table.setItem(row, 3, QTableWidgetItem(inv.payment_method))
            self.table.setItem(row, 4, QTableWidgetItem(f"{inv.total:.2f}"))
            
        session.close()

    def select_invoice(self):
        row = self.table.currentRow()
        if row >= 0:
            inv_id_txt = self.table.item(row, 0).text()
            self.selected_invoice_id = int(inv_id_txt.replace("#", ""))
            self.accept()
        else:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار فاتورة من الجدول أولاً")


# ==================== RETURNS PAGE ====================
class ReturnsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.return_items = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("↩️ مرتجع المبيعات")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #c0392b; margin-bottom: 10px;")
        layout.addWidget(header)
        
        top_bar = QHBoxLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("امسح باركود المنتج لإرجاعه أو اكتب اسمه...")
        self.barcode_input.setMinimumHeight(40)
        self.barcode_input.setStyleSheet("font-size: 16px;")
        self.barcode_input.returnPressed.connect(self.handle_barcode_search)
        
        btn_search = QPushButton("بحث 🔍")
        btn_search.clicked.connect(self.handle_barcode_search)
        btn_search.setMinimumHeight(40)
        
        btn_archive = QPushButton("أرشيف الفواتير 📜")
        btn_archive.clicked.connect(self.open_invoice_archive)
        btn_archive.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        btn_archive.setMinimumHeight(40)
        
        top_bar.addWidget(self.barcode_input, 4)
        top_bar.addWidget(btn_search, 1)
        top_bar.addWidget(btn_archive, 2)
        layout.addLayout(top_bar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "سعر البيع", "الكمية المرتجعة", "الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellChanged.connect(self.handle_cell_changed)
        layout.addWidget(self.table)
        
        bottom_bar = QHBoxLayout()
        self.lbl_refund = QLabel("إجمالي المبلغ المسترجع: 0.00 ل.س")
        self.lbl_refund.setStyleSheet("font-size: 18px; font-weight: bold; color: #c0392b;")
        
        btn_confirm = QPushButton("تأكيد المرتجع وإرجاع المال 🔄")
        btn_confirm.clicked.connect(self.confirm_return)
        btn_confirm.setStyleSheet("background-color: #e74c3c; color: white; font-size: 16px; font-weight: bold; padding: 10px 20px;")
        
        btn_clear = QPushButton("تنظيف 🧹")
        btn_clear.clicked.connect(self.clear_page)
        
        bottom_bar.addWidget(self.lbl_refund)
        bottom_bar.addStretch()
        bottom_bar.addWidget(btn_clear)
        bottom_bar.addWidget(btn_confirm)
        layout.addLayout(bottom_bar)
        
        self.setLayout(layout)

    def handle_barcode_search(self):
        txt = self.barcode_input.text().strip()
        if not txt:
            return
            
        session = get_session()
        from database import Product, ProductBarcode
        
        prod = session.query(Product).filter_by(barcode=txt).first()
        if not prod:
            sub_bar = session.query(ProductBarcode).filter_by(barcode=txt).first()
            if sub_bar:
                prod = sub_bar.product
                
        if not prod:
            prod = session.query(Product).filter(Product.name.like(f"%{txt}%")).first()
            
        if prod:
            barcode = prod.barcode if prod.barcode else str(prod.id)
            if barcode in self.return_items:
                self.return_items[barcode]['qty_to_return'] += 1
            else:
                self.return_items[barcode] = {
                    'id': prod.id,
                    'name': prod.name,
                    'price': prod.price,
                    'qty_to_return': 1.0,
                    'max_qty': 99999.0
                }
            self.update_table()
            self.barcode_input.clear()
        else:
            QMessageBox.warning(self, "غير موجود", "لم يتم العثور على المنتج المطلوب")
            
        session.close()

    def open_invoice_archive(self):
        dialog = InvoiceArchiveDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            inv_id = dialog.selected_invoice_id
            if inv_id:
                self.load_invoice_to_return(inv_id)

    def load_invoice_to_return(self, invoice_id):
        self.clear_page()
        session = get_session()
        from database import Invoice
        inv = session.query(Invoice).get(invoice_id)
        if inv:
            for item in inv.items:
                barcode = item.product.barcode if item.product.barcode else str(item.product.id)
                self.return_items[barcode] = {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': item.price,
                    'qty_to_return': item.quantity,
                    'max_qty': item.quantity
                }
            self.update_table()
        session.close()

    def update_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        for barcode, item in self.return_items.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.item(row, 0).setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            self.table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.table.item(row, 1).setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            self.table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.table.item(row, 2).setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            self.table.setItem(row, 3, QTableWidgetItem(str(item['qty_to_return'])))
            
            subtotal = item['price'] * item['qty_to_return']
            self.table.setItem(row, 4, QTableWidgetItem(f"{subtotal:.2f}"))
            self.table.item(row, 4).setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
        self.table.blockSignals(False)
        self.calculate_total()

    def handle_cell_changed(self, row, col):
        if col == 3:
            barcode = self.table.item(row, 0).text()
            qty_txt = self.table.item(row, 3).text()
            try:
                qty = float(qty_txt)
                if qty < 0:
                    raise ValueError
            except ValueError:
                qty = 1.0
                
            item = self.return_items.get(barcode)
            if item:
                if qty > item['max_qty']:
                    QMessageBox.warning(self, "تنبيه", f"الحد الأقصى للكمية المرتجعة لهذا الصنف هو: {item['max_qty']}")
                    qty = item['max_qty']
                item['qty_to_return'] = qty
                
            self.update_table()

    def calculate_total(self):
        total = sum(item['price'] * item['qty_to_return'] for item in self.return_items.values())
        self.lbl_refund.setText(f"إجمالي المبلغ المسترجع: {total:.2f} ل.س")

    def confirm_return(self):
        if not self.return_items:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد أصناف لإرجاعها أولاً")
            return
            
        reply = QMessageBox.question(self, "تأكيد المرتجع", "هل أنت متأكد من إتمام عملية المرتجع وإعادة الأموال؟",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            try:
                from database import Product
                for barcode, item in self.return_items.items():
                    prod = session.query(Product).get(item['id'])
                    if prod:
                        if prod.parent_id:
                            parent_prod = session.query(Product).get(prod.parent_id)
                            if parent_prod:
                                parent_prod.quantity += (item['qty_to_return'] * prod.units_in_box)
                        else:
                            prod.quantity += item['qty_to_return']
                            
                session.commit()
                QMessageBox.information(self, "نجاح العملية", "تمت عملية المرتجع بنجاح وزيادة المخزون وإرجاع المال!")
                self.clear_page()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "خطأ", f"فشل إرجاع المرتجع: {str(e)}")
            finally:
                session.close()

    def clear_page(self):
        self.return_items.clear()
        self.update_table()
        self.barcode_input.clear()


# ==================== SETTINGS & PARTNERS PAGE ====================
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("⚙️ الإعدادات وإدارة الشركاء والمسحوبات")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        self.tabs = QTabWidget()
        self.tab_info = QWidget()
        self.tab_partners = QWidget()
        self.tab_withdrawals = QWidget()
        
        self.tabs.addTab(self.tab_info, "🏡 معلومات وإعدادات المحل")
        self.tabs.addTab(self.tab_partners, "👥 إدارة شركاء المحل")
        self.tabs.addTab(self.tab_withdrawals, "💸 تسجيل مسحوب نقدية للشركاء")
        
        self.setup_info_tab()
        self.setup_partners_tab()
        self.setup_withdrawals_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.load_settings()

    def on_tab_changed(self, index):
        if index == 0:
            self.load_settings()
        elif index == 1:
            self.load_partners()
        elif index == 2:
            self.load_partners_combo()
            self.load_withdrawals()

    # --- التبويب الأول: معلومات المحل ---
    def setup_info_tab(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.input_shop_name = QLineEdit()
        self.input_shop_name.setPlaceholderText("اسم السوبر ماركت...")
        self.input_shop_name.setMinimumHeight(35)
        
        self.input_shop_address = QLineEdit()
        self.input_shop_address.setPlaceholderText("عنوان الفرع...")
        self.input_shop_address.setMinimumHeight(35)
        
        self.input_shop_phone = QLineEdit()
        self.input_shop_phone.setPlaceholderText("رقم الهاتف للتواصل...")
        self.input_shop_phone.setMinimumHeight(35)
        
        btn_save = QPushButton("حفظ إعدادات المتجر 💾")
        btn_save.clicked.connect(self.save_settings)
        btn_save.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        
        layout.addRow("اسم المحل (في الريسيت):", self.input_shop_name)
        layout.addRow("عنوان المحل:", self.input_shop_address)
        layout.addRow("رقم الهاتف:", self.input_shop_phone)
        layout.addRow("", btn_save)
        
        self.tab_info.setLayout(layout)

    def load_settings(self):
        session = get_session()
        from database import AppSetting
        
        name = session.query(AppSetting).filter_by(key='shop_name').first()
        addr = session.query(AppSetting).filter_by(key='shop_address').first()
        phone = session.query(AppSetting).filter_by(key='shop_phone').first()
        
        if name: self.input_shop_name.setText(name.value)
        if addr: self.input_shop_address.setText(addr.value)
        if phone: self.input_shop_phone.setText(phone.value)
        session.close()

    def save_settings(self):
        name = self.input_shop_name.text().strip()
        addr = self.input_shop_address.text().strip()
        phone = self.input_shop_phone.text().strip()
        
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم المحل")
            return
            
        session = get_session()
        from database import AppSetting
        
        n_set = session.query(AppSetting).filter_by(key='shop_name').first()
        if not n_set:
            n_set = AppSetting(key='shop_name', value=name)
            session.add(n_set)
        else:
            n_set.value = name
            
        a_set = session.query(AppSetting).filter_by(key='shop_address').first()
        if not a_set:
            a_set = AppSetting(key='shop_address', value=addr)
            session.add(a_set)
        else:
            a_set.value = addr
            
        p_set = session.query(AppSetting).filter_by(key='shop_phone').first()
        if not p_set:
            p_set = AppSetting(key='shop_phone', value=phone)
            session.add(p_set)
        else:
            p_set.value = phone
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "تم الحفظ", "تم حفظ معلومات المحل بنجاح وتحديث الفواتير والريسيت!")

    # --- التبويب الثاني: إدارة الشركاء ---
    def setup_partners_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.input_partner_name = QLineEdit()
        self.input_partner_name.setPlaceholderText("اسم الشريك الجديد")
        
        self.input_partner_share = QDoubleSpinBox()
        self.input_partner_share.setMaximum(100.0)
        self.input_partner_share.setSuffix(" %")
        self.input_partner_share.setPrefix("نسبة الشراكة: ")
        
        btn_add = QPushButton("حفظ الشريك")
        btn_add.clicked.connect(self.save_partner)
        btn_add.setStyleSheet("background-color: #2c3e50;")
        
        form_layout.addWidget(self.input_partner_name)
        form_layout.addWidget(self.input_partner_share)
        form_layout.addWidget(btn_add)
        layout.addWidget(form_widget)
        
        self.table_partners = QTableWidget()
        self.table_partners.setColumnCount(4)
        self.table_partners.setHorizontalHeaderLabels(["المعرف", "الاسم", "النسبة مئوية", "إجمالي المسحوبات"])
        self.table_partners.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_partners.doubleClicked.connect(self.load_row_to_partner_form)
        layout.addWidget(self.table_partners)
        
        buttons_layout = QHBoxLayout()
        btn_delete = QPushButton("❌ حذف الشريك المحدد")
        btn_delete.clicked.connect(self.delete_partner)
        btn_delete.setObjectName("dangerButton")
        buttons_layout.addWidget(btn_delete)
        layout.addLayout(buttons_layout)
        
        self.tab_partners.setLayout(layout)
        self.load_partners()

    def load_partners(self):
        self.table_partners.setRowCount(0)
        session = get_session()
        from database import Partner
        partners = session.query(Partner).all()
        
        for p in partners:
            row = self.table_partners.rowCount()
            self.table_partners.insertRow(row)
            self.table_partners.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table_partners.setItem(row, 1, QTableWidgetItem(p.name))
            self.table_partners.setItem(row, 2, QTableWidgetItem(f"{p.share_percentage:.1f} %"))
            
            # حساب إجمالي المسحوبات للشريك
            tot_w = sum(w.amount for w in p.withdrawals)
            self.table_partners.setItem(row, 3, QTableWidgetItem(f"{tot_w:.2f} ل.س"))
            
        session.close()

    def save_partner(self):
        name = self.input_partner_name.text().strip()
        share = self.input_partner_share.value()
        
        if not name:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال اسم الشريك")
            return
            
        session = get_session()
        from database import Partner
        p = session.query(Partner).filter_by(name=name).first()
        if p:
            p.share_percentage = share
        else:
            p = Partner(name=name, share_percentage=share)
            session.add(p)
            
        session.commit()
        session.close()
        
        QMessageBox.information(self, "تم الحفظ", "تم حفظ بيانات الشريك بنجاح!")
        self.input_partner_name.clear()
        self.input_partner_share.setValue(0.0)
        self.load_partners()

    def load_row_to_partner_form(self):
        row = self.table_partners.currentRow()
        if row >= 0:
            self.input_partner_name.setText(self.table_partners.item(row, 1).text())
            share_txt = self.table_partners.item(row, 2).text().replace(" %", "")
            self.input_partner_share.setValue(float(share_txt))

    def delete_partner(self):
        row = self.table_partners.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد شريك لحذفه")
            return
            
        p_id = int(self.table_partners.item(row, 0).text())
        p_name = self.table_partners.item(row, 1).text()
        
        reply = QMessageBox.question(self, "تأكيد الحذف", f"هل أنت متأكد من حذف الشريك: {p_name}؟",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            session = get_session()
            from database import Partner
            p = session.query(Partner).get(p_id)
            if p:
                session.delete(p)
                session.commit()
            session.close()
            QMessageBox.information(self, "تم الحذف", "تم حذف الشريك بنجاح!")
            self.load_partners()

    # --- التبويب الثالث: مسحوبات الشركاء ---
    def setup_withdrawals_tab(self):
        layout = QVBoxLayout()
        
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        self.combo_with_partners = QComboBox()
        self.load_partners_combo()
        
        self.input_with_amount = QDoubleSpinBox()
        self.input_with_amount.setMaximum(999999.0)
        self.input_with_amount.setPrefix("المبلغ المسحوب: ")
        
        self.input_with_note = QLineEdit()
        self.input_with_note.setPlaceholderText("ملاحظات / سبب السحب من الصندوق...")
        
        btn_save = QPushButton("تسجيل مسحوب نقدية 💸")
        btn_save.clicked.connect(self.save_withdrawal)
        btn_save.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold;")
        
        form_layout.addWidget(self.combo_with_partners)
        form_layout.addWidget(self.input_with_amount)
        form_layout.addWidget(self.input_with_note)
        form_layout.addWidget(btn_save)
        layout.addWidget(form_widget)
        
        self.table_withdrawals = QTableWidget()
        self.table_withdrawals.setColumnCount(4)
        self.table_withdrawals.setHorizontalHeaderLabels(["الشريك", "المبلغ", "التاريخ والوقت", "الملاحظات"])
        self.table_withdrawals.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_withdrawals)
        
        self.tab_withdrawals.setLayout(layout)
        self.load_withdrawals()

    def load_partners_combo(self):
        self.combo_with_partners.clear()
        session = get_session()
        from database import Partner
        partners = session.query(Partner).all()
        for p in partners:
            self.combo_with_partners.addItem(p.name, p.id)
        session.close()

    def load_withdrawals(self):
        self.table_withdrawals.setRowCount(0)
        session = get_session()
        from database import PartnerWithdrawal
        withdrawals = session.query(PartnerWithdrawal).order_by(PartnerWithdrawal.date.desc()).all()
        
        for w in withdrawals:
            row = self.table_withdrawals.rowCount()
            self.table_withdrawals.insertRow(row)
            self.table_withdrawals.setItem(row, 0, QTableWidgetItem(w.partner.name if w.partner else "غير معروف"))
            self.table_withdrawals.setItem(row, 1, QTableWidgetItem(f"{w.amount:.2f}"))
            self.table_withdrawals.setItem(row, 2, QTableWidgetItem(w.date.strftime("%Y-%m-%d %H:%M")))
            self.table_withdrawals.setItem(row, 3, QTableWidgetItem(w.note if w.note else ""))
            
        session.close()

    def save_withdrawal(self):
        p_id = self.combo_with_partners.currentData()
        amount = self.input_with_amount.value()
        note = self.input_with_note.text().strip()
        
        if not p_id or amount <= 0:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار شريك وتحديد مبلغ صحيح")
            return
            
        session = get_session()
        from database import PartnerWithdrawal
        w = PartnerWithdrawal(partner_id=p_id, amount=amount, note=note)
        session.add(w)
        session.commit()
        session.close()
        
        QMessageBox.information(self, "نجاح", "تم تسجيل المسحوب النقدي للشريك بنجاح من الخزينة!")
        self.input_with_amount.setValue(0.0)
        self.input_with_note.clear()
        self.load_withdrawals()
