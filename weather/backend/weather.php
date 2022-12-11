<?php
declare(strict_types=1);

error_reporting(E_ALL);
ini_set('display_errors', '1');

if ($_SERVER['REQUEST_METHOD'] != 'POST') {
    echo '<h1>IoT API</h1> <p>This page is for robots only</p>';
    die();
}

$json = file_get_contents('php://input');
$payload = json_decode($json, true);

if (!is_array($payload) || !count($payload)) {
    echo '<h1>IoT API</h1> <p>JSON playload required</p>';
    die();
}

$db_config = [
    'dsn' => 'mysql:host=localhost;dbname=home_iot',
    'username' => '...',
    'password' => '...',
    'options' => [
        \PDO::ATTR_PERSISTENT => true,
    ],
];

// For PHP 8:
// $dbh = new \PDO(...$db_config);

// For PHP 7.4:
$dbh = new PDO(
    $db_config['dsn'],
    $db_config['username'],
    $db_config['password'],
    $db_config['options'],
);

$sth = $dbh->prepare('INSERT INTO `weather`'
    . ' (`station`, `temperature`, `pressure`, `humidity`) '
    . ' VALUES (:station, :temperature, :pressure, :humidity)');

$keys = ['station', 'temperature', 'pressure', 'humidity'];
foreach ($keys as $key) {
    if (array_key_exists($key, $payload)) {
        $sth->bindValue($key, $payload[$key]);
    } else {
        $sth->bindValue($key, null, PDO::PARAM_NULL);
    }
}

$sth->execute();

if ($sth->rowCount()) {
    echo '<h1>IoT API</h1> <p>OK</p>';
} else {
    echo '<h1>IoT API</h1> <p>Error</p>';
}
