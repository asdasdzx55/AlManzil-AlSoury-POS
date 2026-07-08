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
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    barcode = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, default=0.0) # يدعم الكسور للوزن
    is_weighted = Column(Boolean, default=False) # هل المنتج يباع بالوزن؟
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="products")

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    balance = Column(Float, default=0.0)

# Setup SQLite DB
from sqlalchemy import text
engine = create_engine('sqlite:///supermarket.db', echo=False)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT is_weighted FROM products LIMIT 1"))
except Exception:
    # في حال لم يكن الحقل موجوداً، نقوم بحذف الجداول وإعادة إنشائها بالبنية الجديدة
    Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()

# Seed default admin user if none exists
def seed_admin():
    session = get_session()
    if session.query(User).count() == 0:
        admin = User(username='admin', password='123', role='admin')
        session.add(admin)
        session.commit()
    session.close()

seed_admin()
