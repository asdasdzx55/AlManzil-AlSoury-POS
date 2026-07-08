from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default='pos') # 'admin' or 'pos'

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")

class Subcategory(Base):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0.0) # سعر التكلفة الشراء
    quantity = Column(Float, default=0.0) # الكمية المتاحة
    is_weighted = Column(Boolean, default=False) # هل بالوزن؟
    
    # علاقة التصنيف الفرعي (إجباري)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False)
    subcategory = relationship("Subcategory", back_populates="products")
    
    # علاقة العلبة بالمنتج الفردي (علبة تحتوي على عدد قطع من منتج أب)
    parent_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    units_in_box = Column(Integer, default=1) # عدد القطع داخل العلبة
    
    barcode = Column(String(50), unique=True, nullable=True) # الباركود الأساسي
    barcodes = relationship("ProductBarcode", back_populates="product", cascade="all, delete-orphan")

class ProductBarcode(Base):
    __tablename__ = 'product_barcodes'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    barcode = Column(String(50), unique=True, nullable=False)
    product = relationship("Product", back_populates="barcodes")

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    balance = Column(Float, default=0.0)
    transactions = relationship("SupplierTransaction", back_populates="supplier")

class SupplierTransaction(Base):
    __tablename__ = 'supplier_transactions'
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False) # 'pay_out' (دفعة له) or 'purchase_in' (شراء بضاعة بالدين)
    date = Column(DateTime, default=datetime.datetime.now)
    note = Column(String(255))
    supplier = relationship("Supplier", back_populates="transactions")

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False) # 'delivery' (ديلفري), 'cashier' (كاشير), 'other' (أخرى)
    phone = Column(String(20))
    salary = Column(Float, default=0.0)
    transactions = relationship("EmployeeTransaction", back_populates="employee", cascade="all, delete-orphan")

class EmployeeTransaction(Base):
    __tablename__ = 'employee_transactions'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(50), nullable=False) # 'salary_payment', 'deduction', 'reward'
    date = Column(DateTime, default=datetime.datetime.now)
    note = Column(String(255))
    employee = relationship("Employee", back_populates="transactions")

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False) # 'إيجار', 'كهرباء', 'صيانة', 'أخرى'
    date = Column(DateTime, default=datetime.datetime.now)
    note = Column(String(255))

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    total = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False) # 'نقدي', 'فيزا', 'إنستا باي', 'فودافون كاش'
    date = Column(DateTime, default=datetime.datetime.now)
    customer_name = Column(String(100))
    customer_phone = Column(String(50))
    delivery_employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False) # سعر البيع وقت الحركة
    cost_price = Column(Float, nullable=False) # سعر التكلفة وقت الحركة
    
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")

class AppSetting(Base):
    __tablename__ = 'app_settings'
    key = Column(String(100), primary_key=True)
    value = Column(String(255))

class Partner(Base):
    __tablename__ = 'partners'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    share_percentage = Column(Float, default=0.0)
    withdrawals = relationship("PartnerWithdrawal", back_populates="partner", cascade="all, delete-orphan")

class PartnerWithdrawal(Base):
    __tablename__ = 'partner_withdrawals'
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)
    note = Column(String(255))
    partner = relationship("Partner", back_populates="withdrawals")

# Setup SQLite DB
from sqlalchemy import text
engine = create_engine('sqlite:///supermarket.db', echo=False)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT key FROM app_settings LIMIT 1"))
except Exception:
    # في حال عدم وجود الجداول الجديدة، نقوم بإعادة بناء قاعدة البيانات بالكامل
    Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()

# Seed default admin user and default categories/subcategories/products if empty
def seed_initial_data():
    session = get_session()
    
    # 1. إعدادات البرنامج
    if session.query(AppSetting).count() == 0:
        session.add(AppSetting(key='shop_name', value='سوبر ماركت المنزل السوري'))
        session.add(AppSetting(key='shop_address', value='دمشق - شارع الميدان الرئيسي'))
        session.add(AppSetting(key='shop_phone', value='0999888777'))
        session.commit()

    # 2. مستخدم المدير
    if session.query(User).count() == 0:
        admin = User(username='admin', password='123', role='admin')
        session.add(admin)
        session.commit()
        
    # 3. تصنيفات ومنتجات تجريبية
    if session.query(Category).count() == 0:
        cat1 = Category(name="المواد الغذائية")
        cat2 = Category(name="المنظفات")
        session.add(cat1)
        session.add(cat2)
        session.commit()
        
        sub1 = Subcategory(name="الأرز والمعلبات", category_id=cat1.id)
        sub2 = Subcategory(name="شامبو ومستحضرات", category_id=cat2.id)
        session.add(sub1)
        session.add(sub2)
        session.commit()
        
        # منتجات وهمية (أصناف عادية، علب/كراتين، باركودات متعددة)
        p1 = Product(name="أرز بسمتي الشعلان 1 كغ", price=25000.0, cost_price=20000.0, quantity=50.0, barcode="1111", subcategory_id=sub1.id)
        p2 = Product(name="علبة تونة الميناء", price=9500.0, cost_price=7500.0, quantity=120.0, barcode="2222", subcategory_id=sub1.id)
        
        # كرتونة تونة (منتج ابن لعلبة تونة يحتوي على 24 قطعة)
        p3 = Product(name="كرتونة تونة الميناء (24 علبة)", price=220000.0, cost_price=170000.0, quantity=5.0, barcode="3333", subcategory_id=sub1.id, parent_id=None, units_in_box=24)
        
        p4 = Product(name="شامبو هيد آند شولدرز 400 مل", price=32000.0, cost_price=26000.0, quantity=30.0, barcode="4444", subcategory_id=sub2.id)
        
        session.add_all([p1, p2, p3, p4])
        session.commit()
        
        # ربط كرتونة التونة بالعلبة
        p3.parent_id = p2.id
        session.commit()
        
        # إضافة باركودات فرعية متعددة لأرز البسمتي
        from database import ProductBarcode
        session.add(ProductBarcode(product_id=p1.id, barcode="11112222"))
        session.add(ProductBarcode(product_id=p1.id, barcode="11113333"))
        
        # 4. شركاء تجريبيين
        partner1 = Partner(name="أحمد عقاب", share_percentage=60.0)
        partner2 = Partner(name="الشريك السوري", share_percentage=40.0)
        session.add_all([partner1, partner2])
        session.commit()
        
        # 5. معاملات مالية تجريبية للتقارير والأرباح
        # مصروفات تجريبية
        from database import Expense, Employee, EmployeeTransaction, Supplier, SupplierTransaction, Invoice, InvoiceItem
        session.add(Expense(amount=150000.0, category="كهرباء ومياه", note="فاتورة كهرباء شهر 6"))
        session.add(Expense(amount=450000.0, category="إيجار المحل", note="إيجار شهر يوليو"))
        
        # موظف ودفع راتب
        emp = Employee(name="وسيم ديلفري", role="delivery", phone="0955666777", salary=180000.0)
        session.add(emp)
        session.commit()
        session.add(EmployeeTransaction(employee_id=emp.id, amount=180000.0, type="salary_payment", note="صرف راتب وسيم"))
        
        # مورد وفاتورة مشتريات دين
        sup = Supplier(name="شركة الخير للصناعات الغذائية", contact_person="أبو الخير", phone="0944333222", balance=0.0)
        session.add(sup)
        session.commit()
        
        tx_sup = SupplierTransaction(supplier_id=sup.id, amount=1200000.0, type="purchase_in", note="شراء بضاعة بالدين")
        sup.balance = 1200000.0
        session.add(tx_sup)
        
        # تسجيل مبيعات فواتير وهمية للأرباح
        # فاتورة 1
        inv1 = Invoice(total=59500.0, payment_method="نقدي (Cash)", customer_name="عميل كريم", customer_phone="0911222333")
        session.add(inv1)
        session.commit()
        session.add(InvoiceItem(invoice_id=inv1.id, product_id=p1.id, quantity=2.0, price=25000.0, cost_price=20000.0))
        session.add(InvoiceItem(invoice_id=inv1.id, product_id=p2.id, quantity=1.0, price=9500.0, cost_price=7500.0))
        
        # فاتورة 2
        inv2 = Invoice(total=32000.0, payment_method="فيزا (Visa)")
        session.add(inv2)
        session.commit()
        session.add(InvoiceItem(invoice_id=inv2.id, product_id=p4.id, quantity=1.0, price=32000.0, cost_price=26000.0))
        
        session.commit()
        
    session.close()

seed_initial_data()
