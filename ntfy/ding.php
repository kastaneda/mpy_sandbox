<?php
declare(strict_types=1);

error_reporting(E_ALL);
ini_set('display_errors', '1');

if (!isset($_REQUEST['from'])) {
    echo '<h1>IoT API</h1> <p>This page is for robots only</p>';
    die();
}

$priority = 'default';
if ($_REQUEST['from'] == 'Some special name') {
    $priority = 'high';
}

file_get_contents('https://ntfy.sh/YOUR_CHANNEL_NAME', false, stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' =>
            "Content-Type: text/plain\r\n" .
            "Priority: $priority\r\n",
        'content' => 'Ding from ' . $_REQUEST['from'],
    ],
]));

echo 'OK';
