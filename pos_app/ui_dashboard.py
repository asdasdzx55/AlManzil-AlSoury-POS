from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, 
                             QFormLayout, QComboBox, QMessageBox, QDoubleSpinBox, QSpinBox,
                             QGroupBox, QCheckBox, QDialog, QListWidget, QListWidgetItem, QDialogButtonBox,
                             QTabWidget)
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
        
        self.btn_purchases = QPushButton("📥")
        self.btn_purchases.setToolTip("فاتورة المشتريات والتوريد")
        self.btn_purchases.setCheckable(True)
        self.btn_purchases.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.btn_purchases)
        
        self.btn_inventory = QPushButton("📦")
        self.btn_inventory.setToolTip("إدارة الأصناف")
        self.btn_inventory.setCheckable(True)
        self.btn_inventory.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.btn_inventory)
        
        self.btn_suppliers = QPushButton("👥")
        self.btn_suppliers.setToolTip("إدارة الموردين")
        self.btn_suppliers.setCheckable(True)
        self.btn_suppliers.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.btn_suppliers)
        
        self.btn_reports = QPushButton("📈")
        self.btn_reports.setToolTip("التقارير والمبيعات")
        self.btn_reports.setCheckable(True)
        if self.user.role != 'admin':
            self.btn_reports.setEnabled(False)
            self.btn_reports.setToolTip("هذه الصفحة متاحة للمدير فقط")
            self.btn_reports.setStyleSheet("color: #7f8c8d; font-size: 24px;")
        self.btn_reports.clicked.connect(lambda: self.switch_page(4))
        sidebar_layout.addWidget(self.btn_reports)
        
        self.btn_sync = QPushButton("🔄")
        self.btn_sync.setToolTip("المزامنة السحابية")
        self.btn_sync.setCheckable(True)
        self.btn_sync.clicked.connect(lambda: self.switch_page(5))
        sidebar_layout.addWidget(self.btn_sync)
        
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
        
        self.menu_buttons = [self.btn_pos, self.btn_purchases, self.btn_inventory, self.btn_suppliers, self.btn_reports, self.btn_sync]
        
        # 2. حاوي الصفحات الرئيسي (مستجيب وقابل للتمدد)
        self.container = QStackedWidget()
        self.container.setStyleSheet("padding: 15px;")
        
        self.page_pos = POSPage(self.user)
        self.page_purchases = PurchasesPage()
        self.page_inventory = InventoryPage()
        self.page_suppliers = SuppliersPage()
        self.page_reports = ReportsPage()
        self.page_sync = SyncPage()
        
        self.container.addWidget(self.page_pos)
        self.container.addWidget(self.page_purchases)
        self.container.addWidget(self.page_inventory)
        self.container.addWidget(self.page_suppliers)
        self.container.addWidget(self.page_reports)
        self.container.addWidget(self.page_sync)
        
        # ترتيب العناصر في Layout الرئيسي
        main_layout.addWidget(self.container, 1) # المحتوى يأخذ المساحة المتبقية
        main_layout.addWidget(self.sidebar)       # الشريط الجانبي في اليمين (نظام عربي)
        
        self.setLayout(main_layout)

    def switch_page(self, index):
        for i, btn in enumerate(self.menu_buttons):
            btn.setChecked(i == index)
        self.container.setCurrentIndex(index)
        
        if index == 1:
            self.page_purchases.load_suppliers()
        elif index == 2:
            self.page_inventory.load_products()
        elif index == 3:
            self.page_suppliers.load_suppliers()
        elif index == 4:
            self.page_reports.load_reports()

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
            
        from database import ProductBarcode
        session = get_session()
        
        # البحث عن الباركود في جدول باركودات المنتجات
        barcode_entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
        product = None
        if barcode_entry:
            product = barcode_entry.product
        else:
            # أو البحث بالاسم مباشرة
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
            for key, item in self.cart.items():
                prod = session.query(Product).get(item['id'])
                if prod:
                    if prod.parent_id:
                        parent_prod = session.query(Product).get(prod.parent_id)
                        if parent_prod:
                            parent_prod.quantity -= (item['qty'] * prod.units_in_box)
                    else:
                        prod.quantity -= item['qty']
            session.commit()
            
            QMessageBox.information(self, "تمت العملية", f"تم تسجيل الفاتورة بنجاح ودفعها عن طريق ({self.payment_method.currentText()})")
            self.clear_cart()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "خطأ", f"فشل إتمام العملية: {str(e)}")
        finally:
            session.close()


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
        entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
        if entry:
            prod = entry.product
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
        entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
        if entry:
            prod = entry.product
            prod.name = name
            prod.cost_price = cost
            prod.price = price
            prod.is_weighted = is_weighted
            prod.subcategory_id = subcat_id
        else:
            prod = Product(name=name, price=price, cost_price=cost, quantity=0.0, is_weighted=is_weighted, subcategory_id=subcat_id)
            session.add(prod)
            session.commit()
            
            new_bc = ProductBarcode(product_id=prod.id, barcode=barcode)
            session.add(new_bc)
            
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
        entry = session.query(ProductBarcode).filter_by(barcode=barcode).first()
        product = None
        if entry:
            product = entry.product
        else:
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
        session.close()
        
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
