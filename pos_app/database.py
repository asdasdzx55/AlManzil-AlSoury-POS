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

# Setup SQLite DB
from sqlalchemy import text
engine = create_engine('sqlite:///supermarket.db', echo=False)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT id FROM invoices LIMIT 1"))
except Exception:
    # في حال عدم وجود الجداول الجديدة، نقوم بإعادة بناء قاعدة البيانات بالكامل
    Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()

# Seed default admin user and default categories/subcategories if empty
def seed_initial_data():
    session = get_session()
    if session.query(User).count() == 0:
        admin = User(username='admin', password='123', role='admin')
        session.add(admin)
        session.commit()
        
    if session.query(Category).count() == 0:
        cat1 = Category(name="المواد الغذائية")
        session.add(cat1)
        session.commit()
        
        sub1 = Subcategory(name="الأرز والمعلبات", category_id=cat1.id)
        session.add(sub1)
        session.commit()
    session.close()

seed_initial_data()
