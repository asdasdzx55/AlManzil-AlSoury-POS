<?php
require_once 'config.php';

// Fetch products
$products = [];
try {
    $stmt = $pdo->query("SELECT * FROM products ORDER BY id DESC");
    $products = $stmt->fetchAll();
} catch (PDOException $e) {
    // Handle error silently or show error
}
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر المنزل السوري الإلكتروني</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
        }
        body {
            background-color: #f8f9fb;
            color: #2c3e50;
        }
        /* Top Navigation */
        nav {
            background-color: #ffffff;
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        nav .logo {
            font-size: 20px;
            font-weight: 700;
            color: #1abc9c;
            text-decoration: none;
        }
        nav .nav-links a {
            color: #7f8c8d;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            margin-right: 20px;
        }
        nav .nav-links a:hover {
            color: #1abc9c;
        }
        /* Banner Section */
        .hero-banner {
            width: 100%;
            height: 300px;
            background-color: #2c3e50;
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            margin-bottom: 40px;
            position: relative;
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            top:0; left:0; right:0; bottom:0;
            background: rgba(0,0,0,0.4);
        }
        .hero-text {
            z-index: 1;
        }
        .hero-text h1 {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .hero-text p {
            font-size: 18px;
            font-weight: 300;
        }
        /* Shop Layout */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px 50px 20px;
        }
        .section-title {
            font-size: 24px;
            margin-bottom: 30px;
            border-right: 4px solid #1abc9c;
            padding-right: 15px;
        }
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 25px;
        }
        .product-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.02);
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid #f1f2f6;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.06);
        }
        .img-container {
            width: 100%;
            height: 200px;
            background-color: #f1f2f6;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .img-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .product-info {
            padding: 20px;
        }
        .product-name {
            font-size: 16px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .product-price {
            font-size: 18px;
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 15px;
        }
        .btn-add-cart {
            display: block;
            width: 100%;
            background-color: #1abc9c;
            color: white;
            text-align: center;
            padding: 10px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: background-color 0.3s;
            border: none;
            cursor: pointer;
        }
        .btn-add-cart:hover {
            background-color: #16a085;
        }
        .out-of-stock {
            color: #e74c3c;
            font-size: 13px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<!-- Navigation -->
<nav>
    <a class="logo" href="#">المنزل السوري</a>
    <div class="nav-links">
        <a href="#">الرئيسية</a>
        <a href="#">عن المتجر</a>
        <a href="login.php">⚙️ لوحة الإدارة</a>
    </div>
</nav>

<!-- Hero / Shop Banner -->
<?php 
    $banner_style = "";
    if (file_exists('uploads/store_banner.jpg')) {
        $banner_style = "style='background-image: url(\"uploads/store_banner.jpg\");'";
    }
?>
<div class="hero-banner" <?php echo $banner_style; ?>>
    <div class="hero-text">
        <h1>سوبر ماركت المنزل السوري</h1>
        <p>تسوق جميع مستلزماتك المنزلية بأفضل جودة وأسعار منافسة</p>
    </div>
</div>

<div class="container">
    <h2 class="section-title">🛒 تسوق من أصنافنا المميزة</h2>
    
    <div class="products-grid">
        <?php if (empty($products)): ?>
            <p style="grid-column: 1/-1; text-align: center; color: #7f8c8d;">لا توجد أصناف معروضة حالياً.</p>
        <?php else: ?>
            <?php foreach ($products as $prod): ?>
                <div class="product-card">
                    <div class="img-container">
                        <?php if (!empty($prod['image_url'])): ?>
                            <img src="<?php echo htmlspecialchars($prod['image_url']); ?>" alt="<?php echo htmlspecialchars($prod['name']); ?>">
                        <?php else: ?>
                            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#bdc3c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                        <?php endif; ?>
                    </div>
                    <div class="product-info">
                        <h3 class="product-name"><?php echo htmlspecialchars($prod['name']); ?></h3>
                        <p class="product-price"><?php echo number_format($prod['price'], 2); ?> ل.س</p>
                        
                        <?php if ($prod['quantity'] > 0): ?>
                            <button class="btn-add-cart" onclick="alert('تمت إضافة المنتج للسلة')">إضافة للسلة</button>
                        <?php else: ?>
                            <p class="out-of-stock">نفد من المخزن ⚠️</p>
                        <?php endif; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</div>

</body>
</html>
