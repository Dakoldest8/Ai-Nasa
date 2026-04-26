<?php
session_start();

header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");
header("Content-Type: application/json");

if (!isset($_SESSION['username']) || !isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(["error" => "not logged in"]);
    exit;
}

$userId = intval($_SESSION['user_id']);
$notesFile = __DIR__ . DIRECTORY_SEPARATOR . "notes_" . $userId . ".txt";

$text = "";
if (file_exists($notesFile)) {
    $text = trim(file_get_contents($notesFile));
}

echo json_encode(["notes" => $text]);
