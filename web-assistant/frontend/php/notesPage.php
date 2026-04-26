<?php
session_start();

header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

// Require BOTH username + user_id (stable numeric id)
if (!isset($_SESSION['username']) || !isset($_SESSION['user_id'])) {
    header("Location: loginPage.php");
    exit;
}

$userId = intval($_SESSION['user_id']);
$noteFile = __DIR__ . DIRECTORY_SEPARATOR . "notes_" . $userId . ".txt";
$currentNote = "";

// Load the saved notes (if any)
if (file_exists($noteFile)) {
    $currentNote = trim(file_get_contents($noteFile));
}

// Save notes when form is submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $newNote = trim($_POST['noteContent'] ?? '');
    $bytes = file_put_contents($noteFile, $newNote);

    if ($bytes === false) {
        echo "<script>alert('ERROR: Could not write notes file. Check permissions.');</script>";
    } else {
        $currentNote = $newNote;
        echo "<script>alert('Notes saved!');</script>";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Notes - ECLIPSE</title>
<link rel="stylesheet" href="StyleSheets/mainStyleSheet.css">
</head>
<body>

<header>Notes</header>

<form method="post">
    <textarea name="noteContent" placeholder="Type your mission notes here..."><?php echo htmlspecialchars($currentNote); ?></textarea><br>
    <button type="submit">Save Notes</button>
</form>

</body>
</html>
