<?php
session_start(); // Start the session

// Destroy all session data
session_unset();
session_destroy();

// Redirect back to login page
header("Location: loginPage.php");
exit;
?>

