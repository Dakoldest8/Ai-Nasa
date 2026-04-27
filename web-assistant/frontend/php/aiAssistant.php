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
        font-family: Arial, sans-serif;
        color: white;
        margin: 0;
        padding: 0;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }

    header {
        font-size: 24px;
        margin-bottom: 10px;
        padding: 20px;
        text-align: center;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }

    #navigation {
        text-align: center;
        padding: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    #navigation button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
        margin: 5px;
    }

    #navigation button:hover {
        background-color: #218838;
    }

    #navigation button.active {
        background-color: #007bff;
    }

    .main-container {
        display: flex;
        flex: 1;
        gap: 0;
        overflow: hidden;
    }

    .panel {
        display: none;
        flex: 1;
        overflow: auto;
        padding: 20px;
    }

    .panel.active {
        display: flex;
        flex-direction: column;
    }

    #chat-panel {
        align-items: center;
    }

    #epub-panel {
        align-items: stretch;
        padding: 0;
    }

    #epub-reader-container {
        width: 100%;
        height: 100%;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 0;
    }

    #epub-reader-container iframe {
        width: 100%;
        height: 100%;
        border: none;
    }

    .chat-content {
        max-width: 600px;
        width: 100%;
    }

    #chat {
        background: white;
        padding: 20px;
        border-radius: 10px;
        color: black;
        height: 300px;
        overflow-y: auto;
        text-align: left;
        margin-bottom: 10px;
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
        margin-top: 10px;
        display: flex;
        gap: 10px;
        justify-content: center;
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
    }

    button:hover {
        background-color: rgb(200, 50, 10);
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
</style>
</head>
<body>

<header>AI Assistant - ECLIPSE</header>

<div id="navigation">
    <button class="nav-btn active" onclick="switchPanel('chat')">💬 Chat</button>
    <button class="nav-btn" onclick="switchPanel('epub')">📖 EPUB Reader</button>
    <button class="nav-btn" onclick="openFederatedDashboard()" style="background-color: #007bff;">📊 FL Dashboard</button>
</div>

<div class="main-container">
    <!-- Chat Panel -->
    <div id="chat-panel" class="panel active">
        <div class="chat-content">
            <div id="chat">
                <div class="msg bot">Hello, astronaut! How can I assist your mission today?</div>
            </div>

            <div id="input-box">
                <input type="text" id="input" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') send();">
                <button onclick="send()">Send</button>
            </div>

            <div id="privacy-controls">
                <label>
                    <input type="checkbox" id="recommendations-toggle">
                    Enable personalized recommendations
                </label>
                <span id="recommendations-status"></span>
            </div>
        </div>
    </div>

    <!-- EPUB Reader Panel -->
    <div id="epub-panel" class="panel">
        <div id="epub-reader-container">
            <iframe id="epub-reader-iframe" src="http://localhost:3000"></iframe>
        </div>
    </div>
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

// Panel switching functionality
function switchPanel(panelName) {
    // Hide all panels
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // Deactivate all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected panel
    document.getElementById(panelName + '-panel').classList.add('active');

    // Activate corresponding nav button
    event.target.classList.add('active');

    // Refresh EPUB reader iframe if switching to it
    if (panelName === 'epub') {
        const iframe = document.getElementById('epub-reader-iframe');
        if (iframe.src) {
            // Force refresh
            iframe.src = iframe.src;
        }
    }
}

function openFederatedDashboard() {
    window.location.href = 'federatedDashboard.php';
}

function toggleEPUBReader() {
    const container = document.getElementById('epub-reader-container');
    const isVisible = container.style.display !== 'none';
    container.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) {
        // Refresh the iframe when showing
        const iframe = document.getElementById('epub-reader-iframe');
        iframe.src = iframe.src;
    }
}

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
