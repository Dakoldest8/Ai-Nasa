<?php
session_start();

header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

if (!isset($_SESSION['username']) || !isset($_SESSION['user_id'])) {
    header("Location: loginPage.php");
    exit;
}

$piWebUrl = getenv('PI_WEB_URL') ?: "http://127.0.0.1:8090";
$status = "offline";
$error = "";
$showIframe = false;

$ch = curl_init($piWebUrl . "/api/status");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 2);
$resp = curl_exec($ch);
if ($resp !== false) {
    $http = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    if ($http === 200) {
        $data = json_decode($resp, true);
        if (is_array($data) && isset($data['status'])) {
            $status = $data['status'];
          $showIframe = ($status === 'online' || $status === 'model-missing');
        } else {
            $status = "unknown";
        }
    } else {
        $error = "HTTP " . $http;
    }
} else {
    $error = curl_error($ch);
}
curl_close($ch);
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Pi Voice Console</title>
<style>
  body {
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    background: #081734;
    color: #f0f4ff;
  }

  .bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(0, 0, 0, 0.35);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .pill {
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.15);
    font-size: 0.9em;
  }

  .ok {
    background: rgba(16, 185, 129, 0.35);
  }

  .warn {
    background: rgba(245, 158, 11, 0.35);
  }

  .box {
    padding: 12px 16px;
    font-size: 0.95em;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  }

  iframe {
    width: 100%;
    height: calc(100vh - 110px);
    border: none;
    background: #fff;
  }

  a {
    color: #93c5fd;
  }
</style>
</head>
<body>
  <div class="bar">
    <div><strong>Pi Voice Console</strong></div>
    <div class="pill <?php echo ($status === 'online' ? 'ok' : 'warn'); ?>">
      Service: <?php echo htmlspecialchars($status); ?>
    </div>
  </div>

  <div class="box">
    Backend URL: <code><?php echo htmlspecialchars($piWebUrl); ?></code>
    <?php if (!$showIframe): ?>
      <br>
      Pi integration is optional. The web assistant continues to work even when the Pi node is offline or unreachable.
      <br>
      Start the Pi locally on the Raspberry Pi with <code>bash start_web.sh</code> or use the VS Code task <code>Start Pi Robot Web</code> when you are running it from this repository.
      <?php if (!empty($error)): ?>
        <br>
        Last error: <?php echo htmlspecialchars($error); ?>
      <?php endif; ?>
    <?php endif; ?>
  </div>

  <?php if ($showIframe): ?>
    <iframe src="<?php echo htmlspecialchars($piWebUrl); ?>" allow="microphone; autoplay"></iframe>
  <?php else: ?>
    <div class="box">
      Pi voice console is currently unavailable. Core web-assistant features remain available without the Pi connection.
    </div>
  <?php endif; ?>
</body>
</html>
