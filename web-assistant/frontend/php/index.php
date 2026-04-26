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

// Per-user reminder + notes files
$reminderFile = __DIR__ . DIRECTORY_SEPARATOR . 'reminder_' . $userId . '.txt';
$notesFile    = __DIR__ . DIRECTORY_SEPARATOR . 'notes_' . $userId . '.txt';

$currentReminder = "";
$currentNotes = "";

// Load reminder
if (file_exists($reminderFile)) {
    $currentReminder = trim(file_get_contents($reminderFile));
}

// Load notes
if (file_exists($notesFile)) {
    $currentNotes = trim(file_get_contents($notesFile));
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Main Menu - Operation Biggie Smalls</title>
<style>
  body {
    background-color: rgb(11, 61, 145);
    color: white;
    font-family: 'Segoe UI', sans-serif;
    text-align: center;
    margin: 0;
    padding: 0;
    overflow: hidden;
  }

  header {
    margin-top: 40px;
    font-size: 2.2em;
    letter-spacing: 1px;
    text-shadow: 0 0 10px rgba(0, 0, 0, 0.6);
  }

  .username-banner {
    position: absolute;
    top: 20px;
    left: 20px;
    background: rgba(0, 0, 0, 0.3);
    padding: 8px 15px;
    border-radius: 8px;
    font-size: 1em;
    color: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
  }

  .hamburger-wrap {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 25;
  }

  .hamburger-btn {
    width: 46px;
    height: 40px;
    border: none;
    border-radius: 10px;
    background: rgba(0, 0, 0, 0.35);
    color: white;
    font-size: 22px;
    cursor: pointer;
    box-shadow: 0 0 12px rgba(0, 0, 0, 0.35);
  }

  .hamburger-menu {
    margin-top: 8px;
    min-width: 220px;
    background: rgba(0, 0, 0, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    overflow: hidden;
    display: none;
  }

  .hamburger-menu button,
  .hamburger-menu a {
    width: 100%;
    display: block;
    text-align: left;
    background: transparent;
    border: none;
    color: white;
    text-decoration: none;
    font-size: 0.95em;
    padding: 12px 14px;
    cursor: pointer;
  }

  .hamburger-menu button:hover,
  .hamburger-menu a:hover {
    background: rgba(77, 184, 255, 0.3);
  }

  .menu-box {
    background: rgba(0, 0, 0, 0.3);
    width: 380px;
    margin: 30px auto 60px auto;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 0 25px rgba(255, 255, 255, 0.15);
    transition: opacity 0.5s ease;
  }

  .menu-button {
    width: 85%;
    padding: 16px;
    margin: 15px 0;
    border: none;
    border-radius: 8px;
    font-size: 1.1em;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.3s;
    background-color: rgb(0, 128, 255);
    color: white;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.4);
  }

  .menu-button:hover {
    background-color: rgb(77, 184, 255);
    transform: translateY(-3px);
  }

  .logout-btn {
    background-color: rgb(182, 17, 17);
  }

  .logout-btn:hover {
    background-color: rgb(211, 49, 49);
  }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    display: none;
    justify-content: center;
    align-items: center;
    z-index: 10;
  }

  iframe {
    width: 80%;
    height: 80%;
    border: none;
    border-radius: 15px;
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.6);
  }

  .closeBtn {
    position: absolute;
    top: 40px;
    right: 60px;
    background-color: rgb(182, 17, 17);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    z-index: 20;
  }

  .closeBtn:hover {
    background-color: rgb(211, 49, 49);
  }

  .info-display {
    background: rgba(0, 0, 0, 0.35);
    width: 500px;
    margin: 25px auto 10px auto;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.15);
    font-size: 1.05em;
    line-height: 1.5em;
  }

  .info-title {
    font-weight: bold;
    margin-bottom: 10px;
    color: rgb(77, 184, 255);
  }

  .nasa-logo {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 120px;
    opacity: 0.9;
    pointer-events: none;
    filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
  }
</style>
</head>
<body>

<div class="username-banner">
  Logged in as: <strong><?php echo htmlspecialchars($_SESSION['username']); ?></strong>
</div>

<div class="hamburger-wrap">
  <button type="button" class="hamburger-btn" onclick="toggleMenu()">☰</button>
  <div class="hamburger-menu" id="hamburgerMenu">
    <button type="button" onclick="openAIFromMenu()">AI Assistant</button>
    <button type="button" onclick="openNotesFromMenu()">Notes</button>
    <button type="button" onclick="openReminderFromMenu()">Daily Reminder</button>
    <button type="button" onclick="openPiVoiceFromMenu()">Pi Voice Console</button>
    <a href="logout.php">Log Out</a>
  </div>
</div>

<header>Operation: Biggie Smalls</header>

<!-- Daily Reminder preview -->
<div class="info-display">
  <div class="info-title">Daily Reminder</div>
  <div id="reminderText">
    <?php
      if (!empty($currentReminder)) {
        echo nl2br(htmlspecialchars($currentReminder));
      } else {
        echo "<em>No reminder set.</em>";
      }
    ?>
  </div>
</div>

<!-- Notes preview -->
<div class="info-display">
  <div class="info-title">Notes Preview</div>
  <div id="notesText">
    <?php
      if (!empty($currentNotes)) {
        echo nl2br(htmlspecialchars($currentNotes));
      } else {
        echo "<em>No notes yet.</em>";
      }
    ?>
  </div>
</div>

<div class="menu-box" id="menu">
  <button type="button" class="menu-button" onclick="openAI()">AI Assistant</button>
  <button type="button" class="menu-button" onclick="openNotes()">Notes</button>
  <button type="button" class="menu-button" onclick="openReminder()">Daily Reminder</button>
  <button type="button" class="menu-button" onclick="openPiVoice()">Pi Voice Console</button>

  <form action="logout.php">
    <button type="submit" class="menu-button logout-btn">Log Out</button>
  </form>
</div>

<div class="overlay" id="aiOverlay">
  <button class="closeBtn" onclick="closeAI()">✖ Close</button>
  <iframe src="aiAssistant.php"></iframe>
</div>

<div class="overlay" id="notesOverlay">
  <button class="closeBtn" onclick="closeNotes()">✖ Close</button>
  <iframe src="notesPage.php"></iframe>
</div>

<div class="overlay" id="reminderOverlay">
  <button class="closeBtn" onclick="closeReminderAndRefreshText()">✖ Close</button>
  <iframe id="reminderFrame" src="dailyReminder.php"></iframe>
</div>

<div class="overlay" id="piVoiceOverlay">
  <button class="closeBtn" onclick="closePiVoice()">✖ Close</button>
  <iframe src="piVoiceConsole.php"></iframe>
</div>

<img src="nasa_icon.png" alt="NASA HUNCH Logo" class="nasa-logo">

<script>
function toggleMenu() {
  const menu = document.getElementById("hamburgerMenu");
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function closeHamburgerMenu() {
  const menu = document.getElementById("hamburgerMenu");
  if (menu) menu.style.display = "none";
}

document.addEventListener("click", function (event) {
  const wrap = document.querySelector(".hamburger-wrap");
  if (wrap && !wrap.contains(event.target)) {
    closeHamburgerMenu();
  }
});

function openAI() {
  closeHamburgerMenu();
  document.getElementById("aiOverlay").style.display = "flex";
  document.getElementById("menu").style.opacity = "0.3";
}
function closeAI() {
  document.getElementById("aiOverlay").style.display = "none";
  document.getElementById("menu").style.opacity = "1";
}

function openAIFromMenu() { openAI(); }

function openNotes() {
  closeHamburgerMenu();
  document.getElementById("notesOverlay").style.display = "flex";
  document.getElementById("menu").style.opacity = "0.3";
}

function openNotesFromMenu() { openNotes(); }

async function closeNotes() {
  document.getElementById("notesOverlay").style.display = "none";
  document.getElementById("menu").style.opacity = "1";

  try {
    // cache-bust so it always pulls newest
    const res = await fetch("getNotes.php?t=" + Date.now(), { cache: "no-store" });
    if (!res.ok) {
      console.log("getNotes.php status:", res.status);
      return;
    }

    const data = await res.json();
    const box = document.getElementById("notesText");
    if (!box) return;

    const notes = (data.notes ?? "").trim();

    if (notes !== "") {
      box.innerHTML = notes
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>");
    } else {
      box.innerHTML = "<em>No notes yet.</em>";
    }
  } catch (e) {
    console.error("Notes update failed:", e);
  }
}

function openReminder() {
  closeHamburgerMenu();
  document.getElementById("reminderOverlay").style.display = "flex";
  document.getElementById("menu").style.opacity = "0.3";

  // ensure the iframe loads fresh each open (helps if browser is caching)
  const frame = document.getElementById("reminderFrame");
  if (frame) frame.src = "dailyReminder.php?t=" + Date.now();
}

function openReminderFromMenu() { openReminder(); }

function openPiVoice() {
  closeHamburgerMenu();
  document.getElementById("piVoiceOverlay").style.display = "flex";
  document.getElementById("menu").style.opacity = "0.3";
}

function closePiVoice() {
  document.getElementById("piVoiceOverlay").style.display = "none";
  document.getElementById("menu").style.opacity = "1";
}

function openPiVoiceFromMenu() { openPiVoice(); }

async function refreshReminderPreview(closeOverlay = false) {
  if (closeOverlay) {
    document.getElementById("reminderOverlay").style.display = "none";
    document.getElementById("menu").style.opacity = "1";
  }

  const box = document.getElementById("reminderText");
  if (!box) {
    alert("BUG: reminderText element not found");
    return;
  }

  try {
    // cache-bust so it always pulls newest
    const res = await fetch("getReminder.php?t=" + Date.now(), { cache: "no-store" });
    if (!res.ok) {
      console.log("getReminder.php status:", res.status);
      return;
    }

    const data = await res.json();
    console.log("Reminder fetch returned:", data);

    const reminder = (data.reminder ?? "").trim();

    if (reminder !== "") {
      box.innerHTML = reminder
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>");
    } else {
      box.innerHTML = "<em>No reminder set.</em>";
    }
  } catch (e) {
    console.error("Reminder update failed:", e);
  }
}

async function closeReminderAndRefreshText() {
  await refreshReminderPreview(true);
}
</script>

</body>
</html>
