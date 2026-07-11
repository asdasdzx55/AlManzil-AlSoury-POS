<?php
session_start();
require_once 'config.php';

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

// Handle product image uploads
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['product_image']) && isset($_POST['product_id'])) {
    $product_id = intval($_POST['product_id']);
    $upload_dir = 'uploads/';
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0755, true);
    }
    
    $file_extension = pathinfo($_FILES['product_image']['name'], PATHINFO_EXTENSION);
    $new_filename = 'prod_' . $product_id . '_' . time() . '.' . $file_extension;
    $target_file = $upload_dir . $new_filename;
    
    if (move_uploaded_file($_FILES['product_image']['tmp_name'], $target_file)) {
        $stmt = $pdo->prepare("UPDATE products SET image_url = ? WHERE id = ?");
        $stmt->execute([$target_file, $product_id]);
    }
    header("Location: dashboard.php");
    exit;
}

// Handle store banner/logo upload
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['store_banner'])) {
    $upload_dir = 'uploads/';
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir, 0755, true);
    }
    
    $target_file = $upload_dir . 'store_banner.jpg';
    move_uploaded_file($_FILES['store_banner']['tmp_name'], $target_file);
    header("Location: dashboard.php");
    exit;
}

// Fetch stats
$total_sales = $pdo->query("SELECT SUM(total_amount) FROM sales")->fetchColumn() ?: 0.00;
$total_products = $pdo->query("SELECT COUNT(*) FROM products")->fetchColumn();
$recent_sales = $pdo->query("SELECT * FROM sales ORDER BY sale_date DESC LIMIT 5")->fetchAll();
$products = $pdo->query("SELECT * FROM products ORDER BY id DESC")->fetchAll();
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - المنزل السوري</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
        }
        body {
            background-color: #f5f7fb;
            color: #333;
        }
        header {
            background-color: #2c3e50;
            color: white;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        header h1 {
            font-size: 20px;
            color: #1abc9c;
        }
        header a {
            color: #ecf0f1;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.02);
            border-right: 5px solid #1abc9c;
        }
        .stat-card.sales {
            border-right-color: #2ecc71;
        }
        .stat-card h3 {
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .stat-card p {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        /* Main Layout */
        .layout-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 30px;
        }
        @media(min-width: 992px) {
            .layout-grid {
                grid-template-columns: 2fr 1fr;
            }
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.02);
            margin-bottom: 30px;
        }
        .card h2 {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 20px;
            border-bottom: 2px solid #f5f7fb;
            padding-bottom: 10px;
        }
        /* Table styles */
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            margin-top: 10px;
        }
        table th, table td {
            padding: 12px 15px;
            border-bottom: 1px solid #f1f2f6;
            font-size: 14px;
        }
        table th {
            background-color: #f8f9fa;
            color: #2c3e50;
            font-weight: bold;
        }
        .product-img {
            width: 50px;
            height: 50px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #ddd;
        }
        /* Forms */
        .form-inline {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .form-inline input[type="file"] {
            font-size: 12px;
        }
        .btn {
            background-color: #1abc9c;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
        }
        .btn:hover {
            background-color: #16a085;
        }
    </style>
</head>
<body>

<header>
    <h1>المنزل السوري - لوحة المالك والتقارير</h1>
    <div>
        <a href="index.php" target="_blank" style="margin-left: 20px;">🌐 زيارة المتجر</a>
        <a href="logout.php" style="color: #e74c3c;">🚪 خروج</a>
    </div>
</header>

<div class="container">
    <!-- Stats -->
    <div class="stats-grid">
        <div class="stat-card sales">
            <h3>إجمالي المبيعات المحققة</h3>
            <p><?php echo number_format($total_sales, 2); ?> ج.م</p>
        </div>
        <div class="stat-card">
            <h3>إجمالي الأصناف المتاحة</h3>
            <p><?php echo $total_products; ?> صنف</p>
        </div>
    </div>
    
    <div class="layout-grid">
        <!-- Products Management -->
        <div>
            <div class="card">
                <h2>📦 الأصناف ورفع صور المنتجات</h2>
                <table>
                    <thead>
                        <tr>
                            <th>الصورة</th>
                            <th>الاسم</th>
                            <th>السعر</th>
                            <th>الكمية بالرف</th>
                            <th>تحديث الصورة</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($products as $prod): ?>
                            <tr>
                                <td>
                                    <?php if (!empty($prod['image_url'])): ?>
                                        <img src="<?php echo htmlspecialchars($prod['image_url']); ?>" class="product-img">
                                    <?php else: ?>
                                        <div style="width:50px; height:50px; background:#ddd; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:10px; color:#888;">بدون صورة</div>
                                    <?php endif; ?>
                                </td>
                                <td><?php echo htmlspecialchars($prod['name']); ?></td>
                                <td><?php echo number_format($prod['price'], 2); ?> ج.م</td>
                                <td><?php echo $prod['quantity']; ?></td>
                                <td>
                                    <form class="form-inline" method="POST" enctype="multipart/form-data" action="dashboard.php">
                                        <input type="hidden" name="product_id" value="<?php echo $prod['id']; ?>">
                                        <input type="file" name="product_image" accept="image/*" required>
                                        <button type="submit" class="btn">رفع</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Sidebar Options (Banner upload / Recent sales) -->
        <div>
            <div class="card">
                <h2>🖼️ تخصيص المتجر (واجهة المحل)</h2>
                <p style="font-size:13px; color:#7f8c8d; margin-bottom: 15px;">ارفع صورة رئيسية أو لافتة المحل لتظهر في واجهة المتجر الإلكتروني للزبائن.</p>
                <form method="POST" enctype="multipart/form-data" action="dashboard.php">
                    <div style="margin-bottom: 15px;">
                        <input type="file" name="store_banner" accept="image/*" required>
                    </div>
                    <button type="submit" class="btn" style="width: 100%; padding: 10px;">حفظ لافتة المحل</button>
                </form>
                
                <?php if (file_exists('uploads/store_banner.jpg')): ?>
                    <div style="margin-top: 15px;">
                        <p style="font-size:12px; font-weight:bold; margin-bottom:5px;">اللافتة الحالية:</p>
                        <img src="uploads/store_banner.jpg" style="width: 100%; border-radius: 8px; border: 1px solid #ddd;">
                    </div>
                <?php endif; ?>
            </div>
            
            <div class="card">
                <h2>🧾 مبيعات الكاشير الأخيرة</h2>
                <table>
                    <thead>
                        <tr>
                            <th>قيمة الفاتورة</th>
                            <th>التاريخ والوقت</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($recent_sales as $sale): ?>
                            <tr>
                                <td><?php echo number_format($sale['total_amount'], 2); ?> ج.م</td>
                                <td style="font-size: 11px; color:#7f8c8d;"><?php echo $sale['sale_date']; ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

</body>
</html>
