<?php
session_start();

header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

if (!isset($_SESSION['username']) || !isset($_SESSION['user_id'])) {
    header("Location: loginPage.php");
    exit;
}

$USER_ID = $_SESSION['user_id'];
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI Assistant - ECLIPSE</title>
<style>
       body {
        background-color: rgb(11, 61, 145);
        text-align: center;
        padding: 40px;
        font-family: Arial, sans-serif;
        color: white;
        margin: 0;
        overflow: hidden;
    }

    header {
        font-size: 24px;
        margin-bottom: 20px;
    }

    #chat {
        max-width: 600px;
        margin: 0 auto;
        background: white;
        padding: 20px;
        border-radius: 10px;
        color: black;
        height: 300px;
        overflow-y: auto;
        text-align: left;
    }

    .msg {
        margin: 10px 0;
        word-wrap: break-word;
    }

    .bot {
        color: rgb(0, 0, 255);
    }

    .user {
        color: rgb(128, 0, 255);
        text-align: right;
    }

    #input-box {
        margin-top: 15px;
    }

    #input {
        width: 70%;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid rgb(192, 192, 192);
    }

    button {
        background-color: rgb(226, 62, 13);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        margin-left: 10px;
    }

    button:hover {
        background-color: rgb(226, 62, 13);
    }

    #privacy-controls {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 10px 0;
        color: #fff;
    }

    #privacy-controls label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
    }

    #recommendations-status {
        margin-left: 12px;
        font-size: 0.9rem;
        color: #d4d4d4;
    }

    #navigation {
        text-align: center;
        margin: 10px 0;
    }

    #navigation button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
    }

    #navigation button:hover {
        background-color: #218838;
    }
</style>
</head>
<body>

<header>AI Assistant</header>

<div id="navigation">
    <button onclick="window.open('http://localhost:3000', '_blank')">Open EPUB Reader</button>
</div>

<div id="privacy-controls">
    <label>
        <input type="checkbox" id="recommendations-toggle">
        Enable personalized recommendations
    </label>
    <span id="recommendations-status"></span>
</div>

<div id="chat">
    <div class="msg bot">Hello, astronaut! How can I assist your mission today?</div>
</div>

<div id="input-box">
    <input type="text" id="input" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') send();">
    <button onclick="send()">Send</button>
</div>

<script>
const chat = document.getElementById("chat");
const USER_ID = <?php echo json_encode($USER_ID); ?>;
const recommendationsToggle = document.getElementById("recommendations-toggle");
const recommendationsStatus = document.getElementById("recommendations-status");
let recommendationsEnabled = true;

function loadRecommendationPreference() {
    const storedValue = localStorage.getItem("recommendations_enabled");
    recommendationsEnabled = storedValue !== "false";
    recommendationsToggle.checked = recommendationsEnabled;
    updateRecommendationStatus();
}

function updateRecommendationStatus() {
    recommendationsStatus.textContent = recommendationsEnabled
        ? "Personalized recommendations are enabled."
        : "Recommendations are disabled for privacy.";
}

recommendationsToggle.addEventListener("change", () => {
    recommendationsEnabled = recommendationsToggle.checked;
    localStorage.setItem("recommendations_enabled", recommendationsEnabled ? "true" : "false");
    updateRecommendationStatus();
});

loadRecommendationPreference();

async function send() {
    const input = document.getElementById("input");
    const msg = input.value.trim();
    if (msg === "") return;

    // Display user message
    chat.innerHTML += `<div class="msg user">${msg}</div>`;
    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    try {
        // Call Flask AI backend
        const response = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // Send user_id so memory stays tied to the correct logged-in user
            body: JSON.stringify({
                user_id: USER_ID,
                message: msg,
                recommendations_enabled: recommendationsEnabled
            })
        });

        if (!response.ok) throw new Error("Network error");

        const data = await response.json();
        chat.innerHTML += `<div class="msg bot">${data.reply}</div>`;

        if (data.ml_analysis && data.ml_analysis.recommended_actions && data.ml_analysis.recommended_actions.length > 0) {
            chat.innerHTML += `<div class="msg bot"><strong>Recommended actions:</strong><ul>${data.ml_analysis.recommended_actions.map(a => `<li>${a}</li>`).join('')}</ul></div>`;
        }

    } 
    catch (error) {
        console.error(error);
        chat.innerHTML += `<div class="msg bot">Unable to reach AI backend. Make sure the Python server is running.</div>`;
    }

    chat.scrollTop = chat.scrollHeight;
}
</script>

</body>
</html>
