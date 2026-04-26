<?php
session_start();

header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

if (!isset($_SESSION['username']) || !isset($_SESSION['user_id'])) {
    header("Location: loginPage.php");
    exit;
}

$userId = intval($_SESSION['user_id']);
$reminderFile = __DIR__ . DIRECTORY_SEPARATOR . 'reminder_' . $userId . '.txt';
$currentReminder = "";

// Load existing reminder
if (file_exists($reminderFile)) {
    $currentReminder = trim(file_get_contents($reminderFile));
}

// Save new reminder
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $newReminder = trim($_POST['reminderText'] ?? '');
    $bytes = file_put_contents($reminderFile, $newReminder);

    if ($bytes === false) {
        echo "<script>alert('ERROR: Could not write reminder file. Check permissions.');</script>";
    } else {
        $currentReminder = $newReminder;
        echo "<script>
            alert('Reminder saved!');
            if (window.parent && typeof window.parent.refreshReminderPreview === 'function') {
                window.parent.refreshReminderPreview(false);
            }
        </script>";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Daily Reminder - ECLIPSE</title>
<link rel="stylesheet" href="StyleSheets/mainStyleSheet.css">
</head>

<body>

<h2>Daily Reminder</h2>

<form method="post">
    <textarea name="reminderText" placeholder="Write your daily reminder..."><?php echo htmlspecialchars($currentReminder); ?></textarea>
    <br>
    <button type="submit">Save Reminder</button>
</form>

</body>
</html>
