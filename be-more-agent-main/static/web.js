const chatLog = document.getElementById('chatLog');
const textInput = document.getElementById('textInput');
const holdTalk = document.getElementById('holdTalk');
const sendText = document.getElementById('sendText');
const replyAudio = document.getElementById('replyAudio');
const llmStatus = document.getElementById('llmStatus');
const handsFree = document.getElementById('handsFree');
const piAudio = document.getElementById('piAudio');
const debugBox = document.getElementById('debugBox');
const refreshDebug = document.getElementById('refreshDebug');
const savePronounce = document.getElementById('savePronounce');
const pronounceMap = document.getElementById('pronounceMap');
const petMood = document.getElementById('petMood');

const sessionId = crypto.randomUUID();
let mediaRecorder = null;
let chunks = [];
let wakeSocket = null;
let wakeAudioCtx = null;
let wakeSource = null;
let wakeProcessor = null;
let wakeStream = null;

function line(role, text) {
  const div = document.createElement('div');
  div.className = `chat-line ${role}`;
  div.textContent = `${role.toUpperCase()}: ${text}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function refreshStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    llmStatus.textContent = `LLM: ${data.status}${data.wakeword ? ' | wake:ready' : ' | wake:off'}`;
  } catch (e) {
    llmStatus.textContent = `LLM: error (${e})`;
  }
}

async function refreshDebugInfo() {
  const res = await fetch('/api/debug');
  const data = await res.json();
  debugBox.textContent = JSON.stringify(data, null, 2);
}

async function refreshPronunciations() {
  const res = await fetch('/api/pronunciation');
  const data = await res.json();
  pronounceMap.textContent = JSON.stringify(data, null, 2);
}

async function sendChatMessage(text) {
  line('user', text);
  const body = {
    message: text,
    session_id: sessionId,
    play_on_pi_audio: piAudio.checked,
    history: []
  };
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (data.error) {
    line('bot', `error: ${data.error}`);
    return;
  }
  line('bot', data.response);
  if (data.audio_url) {
    replyAudio.src = data.audio_url;
    replyAudio.play().catch(() => {});
  }
}

async function transcribeAndSend(blob) {
  const fd = new FormData();
  fd.append('file', blob, 'recording.webm');
  const res = await fetch('/api/transcribe', {method: 'POST', body: fd});
  const data = await res.json();
  if (!data.text) {
    line('bot', 'I did not catch that.');
    return;
  }
  textInput.value = data.text;
  await sendChatMessage(data.text);
}

async function startPressRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({audio: true});
  chunks = [];
  mediaRecorder = new MediaRecorder(stream, {mimeType: 'audio/webm'});
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(chunks, {type: 'audio/webm'});
    stream.getTracks().forEach(t => t.stop());
    await transcribeAndSend(blob);
  };
  mediaRecorder.start();
}

function stopPressRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
}

async function startWakewordStream() {
  if (wakeSocket) return;
  wakeStream = await navigator.mediaDevices.getUserMedia({audio: true});
  wakeAudioCtx = new AudioContext({sampleRate: 16000});
  wakeSource = wakeAudioCtx.createMediaStreamSource(wakeStream);
  wakeProcessor = wakeAudioCtx.createScriptProcessor(1024, 1, 1);
  wakeSocket = new WebSocket(`ws://${location.host}/api/wakeword`);

  wakeSocket.onmessage = async (msg) => {
    try {
      const data = JSON.parse(msg.data);
      if (data.event === 'wakeword_detected') {
        line('bot', `wake word detected: ${data.model}`);
        const recStream = await navigator.mediaDevices.getUserMedia({audio: true});
        chunks = [];
        const recorder = new MediaRecorder(recStream, {mimeType: 'audio/webm'});
        recorder.ondataavailable = (e) => chunks.push(e.data);
        recorder.onstop = async () => {
          const blob = new Blob(chunks, {type: 'audio/webm'});
          recStream.getTracks().forEach(t => t.stop());
          await transcribeAndSend(blob);
        };
        recorder.start();
        setTimeout(() => recorder.stop(), 3500);
      }
    } catch (_) {}
  };

  wakeProcessor.onaudioprocess = (e) => {
    if (!wakeSocket || wakeSocket.readyState !== WebSocket.OPEN) return;
    const input = e.inputBuffer.getChannelData(0);
    const pcm = new Int16Array(input.length);
    for (let i = 0; i < input.length; i++) {
      let v = Math.max(-1, Math.min(1, input[i]));
      pcm[i] = v < 0 ? v * 32768 : v * 32767;
    }
    wakeSocket.send(pcm.buffer);
  };

  wakeSource.connect(wakeProcessor);
  wakeProcessor.connect(wakeAudioCtx.destination);
}

function stopWakewordStream() {
  if (wakeSocket) {
    wakeSocket.close();
    wakeSocket = null;
  }
  if (wakeProcessor) {
    wakeProcessor.disconnect();
    wakeProcessor = null;
  }
  if (wakeSource) {
    wakeSource.disconnect();
    wakeSource = null;
  }
  if (wakeAudioCtx) {
    wakeAudioCtx.close();
    wakeAudioCtx = null;
  }
  if (wakeStream) {
    wakeStream.getTracks().forEach(t => t.stop());
    wakeStream = null;
  }
}

holdTalk.addEventListener('mousedown', () => startPressRecording().catch(e => line('bot', `mic error: ${e}`)));
holdTalk.addEventListener('mouseup', stopPressRecording);
holdTalk.addEventListener('mouseleave', stopPressRecording);
holdTalk.addEventListener('touchstart', (e) => { e.preventDefault(); startPressRecording().catch(err => line('bot', `mic error: ${err}`)); });
holdTalk.addEventListener('touchend', (e) => { e.preventDefault(); stopPressRecording(); });

sendText.addEventListener('click', async () => {
  const text = textInput.value.trim();
  if (!text) return;
  textInput.value = '';
  await sendChatMessage(text);
});

refreshDebug.addEventListener('click', refreshDebugInfo);

savePronounce.addEventListener('click', async () => {
  const word = document.getElementById('word').value.trim();
  const phonetic = document.getElementById('phonetic').value.trim();
  if (!word || !phonetic) return;
  await fetch('/api/pronunciation', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({word, phonetic})
  });
  await refreshPronunciations();
});

handsFree.addEventListener('change', () => {
  if (handsFree.checked) {
    startWakewordStream().catch(e => {
      line('bot', `hands-free failed: ${e}`);
      handsFree.checked = false;
    });
  } else {
    stopWakewordStream();
  }
});

setInterval(async () => {
  try {
    const res = await fetch('/api/idle-signal');
    const data = await res.json();
    petMood.textContent = `${data.mood} ${data.symbol}`;
  } catch (_) {}
}, 15000);

setInterval(refreshStatus, 7000);
setInterval(refreshDebugInfo, 10000);

refreshStatus();
refreshDebugInfo();
refreshPronunciations();
