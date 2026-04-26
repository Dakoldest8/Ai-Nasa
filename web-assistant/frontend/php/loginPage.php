<?php
session_start(); // Start the session
$error = "";

if (isset($_SESSION['username'])) {
    // If logged in, send back to index page
    header("Location: index.php");
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    // Validate credentials via the Python auth server (MySQL users table)
    $payload = json_encode([
        'username' => $username,
        'password' => $password
    ]);

    $ch = curl_init('http://localhost:7000/login');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

    $resp = curl_exec($ch);
    $http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $data = json_decode($resp, true);

    if ($http === 200 && isset($data['status']) && $data['status'] === 'ok') {
        session_regenerate_id(true);
        // Store both username + numeric user_id so AI memory never mixes
        $_SESSION['username'] = $data['username'] ?? $username;
        $_SESSION['user_id'] = $data['user_id'];
        header("Location: index.php");
        exit;
    }

    $error = "Invalid Credentials.";
}

?>


<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Login - ECLIPSE</title>
<style>
    body {
        background-color: rgb(11, 61, 145);
        color: white;
        font-family: 'Segoe UI', sans-serif;
        margin: 0;
        padding: 0;
        text-align: center;
        overflow: hidden;
    }

    h1 {
        margin-top: 60px;
        font-size: 2.5em;
        text-shadow: 0 0 12px rgba(0, 0, 0, 0.6);
    }

    h3 {
        margin-top: 10px;
        font-size: 1.3em;
        opacity: 0.9;
    }

    /* Login container styled similar to the menu box */
    .login-box {
        background: rgba(0, 0, 0, 0.25);
        width: 380px;
        margin: 60px auto;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.15);
    }

    input {
        width: 80%;
        padding: 14px;
        margin: 12px 0;
        border: none;
        border-radius: 8px;
        font-size: 1em;
    }

    button {
        width: 85%;
        padding: 14px;
        margin-top: 20px;
        border: none;
        border-radius: 8px;
        font-size: 1.1em;
        letter-spacing: 1px;
        cursor: pointer;
        background-color: rgb(226, 62, 13);
        color: white;
        transition: 0.3s;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.4);
    }

    button:hover {
        background-color: rgb(226, 62, 13);
        transform: translateY(-3px);
    }
</style>
</head>
<body>

<h1>Project Operation: Biggie Smalls</h1>
<h3>Login Box</h3>

<?php if ($error): ?>
    <p style="color:red; font-weight:bold;"><?php echo $error; ?></p>
<?php endif; ?>

<form method="POST" action="loginPage.php">
    <div class="input-group">
        <label for="username">Username:</label>
        <input type="text" name="username" required>
    </div>

    <div class="input-group">
        <label for="password">Password:</label>
        <input type="password" name="password" required>
    </div>

    <button type="submit">Sign In</button>

</form>
<img src="nasa_icon.png" alt="NASA HUNCH Logo" class="nasa-logo">
<style>
    .nasa-logo {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 200px;
        opacity: 0.8;
    }

</body>
</html>
