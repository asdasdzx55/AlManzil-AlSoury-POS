import requests
from database import get_session, Product, User

API_URL = "http://localhost/web_app/api.php" # Adjust this to your Hostinger domain (e.g., http://yourdomain.com/api.php)

def sync_products_to_online():
    """
    Sends local SQLite products to online MySQL database
    """
    session = get_session()
    products = session.query(Product).all()
    session.close()
    
    product_list = []
    for p in products:
        product_list.append({
            'barcode': p.barcode,
            'name': p.name,
            'price': p.price,
            'quantity': p.quantity
        })
        
    if not product_list:
        return True, "لا توجد منتجات محلياً للمزامنة"
        
    try:
        response = requests.post(f"{API_URL}?action=sync_products", json={'products': product_list}, timeout=5)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('success'):
                return True, "تم رفع وتحديث الأصناف على السيرفر بنجاح!"
        return False, f"فشل رفع البيانات: {response.text}"
    except Exception as e:
        return False, f"خطأ في الاتصال بالشبكة: {str(e)}"

def sync_products_from_online():
    """
    Downloads products from online MySQL and updates local SQLite
    """
    try:
        response = requests.get(f"{API_URL}?action=get_products", timeout=5)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('success'):
                online_products = res_data.get('products', [])
                
                session = get_session()
                for op in online_products:
                    # check if product exists locally
                    local_p = session.query(Product).filter_by(barcode=op['barcode']).first()
                    if local_p:
                        local_p.name = op['name']
                        local_p.price = float(op['price'])
                        local_p.quantity = int(op['quantity'])
                    else:
                        new_p = Product(barcode=op['barcode'], name=op['name'], price=float(op['price']), quantity=int(op['quantity']))
                        session.add(new_p)
                session.commit()
                session.close()
                return True, "تم تحميل وتحديث الأصناف من السيرفر بنجاح!"
        return False, f"فشل تحميل البيانات: {response.text}"
    except Exception as e:
        return False, f"خطأ في الاتصال بالشبكة: {str(e)}"
