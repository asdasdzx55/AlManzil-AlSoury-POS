<?php
// Database config configuration
define('DB_HOST', 'localhost');
define('DB_USER', 'root'); // Replace with Hostinger MySQL user
define('DB_PASS', '');     // Replace with Hostinger MySQL password
define('DB_NAME', 'supermarket_almanzil');

try {
    $pdo = new PDO("mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4", DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}
?>
