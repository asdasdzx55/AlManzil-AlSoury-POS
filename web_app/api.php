<?php
header('Content-Type: application/json');
require_once 'config.php';

$action = isset($_GET['action']) ? $_GET['action'] : '';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // 1. Get all products from online MySQL
    if ($action === 'get_products') {
        try {
            $stmt = $pdo->query("SELECT * FROM products");
            $products = $stmt->fetchAll();
            echo json_encode(['success' => true, 'products' => $products]);
        } catch (PDOException $e) {
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);

    // 2. Upload sales from POS
    if ($action === 'upload_sales') {
        if (!isset($input['sales']) || !is_array($input['sales'])) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid sales data']);
            exit;
        }

        try {
            $pdo->beginTransaction();
            $stmt = $pdo->prepare("INSERT INTO sales (total_amount, sale_date) VALUES (?, ?)");
            foreach ($input['sales'] as $sale) {
                $stmt->execute([$sale['total_amount'], $sale['sale_date']]);
            }
            $pdo->commit();
            echo json_encode(['success' => true, 'message' => 'Sales uploaded successfully']);
        } catch (PDOException $e) {
            $pdo->rollBack();
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }

    // 3. Sync products (update database with POS additions/modifications)
    if ($action === 'sync_products') {
        if (!isset($input['products']) || !is_array($input['products'])) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Invalid products data']);
            exit;
        }

        try {
            $pdo->beginTransaction();
            $stmt = $pdo->prepare("INSERT INTO products (barcode, name, price, quantity) 
                                   VALUES (:barcode, :name, :price, :quantity) 
                                   ON DUPLICATE KEY UPDATE name = :name, price = :price, quantity = :quantity");
            foreach ($input['products'] as $prod) {
                $stmt->execute([
                    ':barcode' => $prod['barcode'],
                    ':name' => $prod['name'],
                    ':price' => $prod['price'],
                    ':quantity' => $prod['quantity']
                ]);
            }
            $pdo->commit();
            echo json_encode(['success' => true, 'message' => 'Products synced successfully']);
        } catch (PDOException $e) {
            $pdo->rollBack();
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }
}

http_response_code(400);
echo json_encode(['success' => false, 'error' => 'Invalid action']);
?>
