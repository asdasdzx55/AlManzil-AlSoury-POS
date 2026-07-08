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

# Setup SQLite DB
from sqlalchemy import text
engine = create_engine('sqlite:///supermarket.db', echo=False)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT cost_price FROM products LIMIT 1"))
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
