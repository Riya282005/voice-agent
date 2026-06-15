// script.js — Frontend logic

let isListening = false;
let continuousMode = false;
let recognition = null;
let voicesLoaded = [];

// ── Tab Switching ──────────────────────────────────────────
function showTab(tab) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  event.target.classList.add('active');
  if (tab === 'history') loadHistory();
}

// ── Send Command ───────────────────────────────────────────
async function sendCommand(text) {
  const input = document.getElementById('textInput');
  const userText = text || input.value.trim();
  if (!userText) return;

  addBubble(userText, 'user');
  input.value = '';

  setStatus('Jarvis soch raha hai...');

  try {
    const res = await fetch('/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: userText })
    });

    const data = await res.json();
    addBubble(data.response, 'jarvis');

    if (continuousMode) {
      const checkSpeaking = setInterval(() => {
        if (!window.speechSynthesis.speaking) {
          clearInterval(checkSpeaking);
          setTimeout(() => startListening(), 300);
        }
      }, 200);
    } else {
      setStatus('Click mic or type below');
    }

  } catch (err) {
    addBubble('Kuch error aaya, dobara try karo!', 'jarvis');
    if (continuousMode) {
      setTimeout(() => startListening(), 500);
    } else {
      setStatus('Click mic or type below');
    }
  }
}

// ── Quick Command ──────────────────────────────────────────
function quickCmd(cmd) {
  sendCommand(cmd);
}

// ── Handle Enter Key ──────────────────────────────────────
function handleKey(e) {
  if (e.key === 'Enter') sendCommand();
}

// ── Add Chat Bubble ───────────────────────────────────────
function addBubble(text, type) {
  const chat = document.getElementById('chatArea');
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${type}`;

  const avatar = document.createElement('div');
  avatar.className = 'bubble-avatar';
  avatar.textContent = type === 'jarvis' ? 'J' : '👤';

  const msg = document.createElement('div');
  msg.className = 'bubble-text';
  msg.textContent = text;

  bubble.appendChild(avatar);
  bubble.appendChild(msg);
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;

  if (type === 'jarvis') {
    speakText(text);
  }
}

// ── Text to Speech ──────────────────────────────────────────
window.speechSynthesis.onvoiceschanged = () => {
  voicesLoaded = window.speechSynthesis.getVoices();
};

function speakText(text) {
  if (!('speechSynthesis' in window)) return;

  window.speechSynthesis.cancel();

  setTimeout(() => {
    const utterance = new SpeechSynthesisUtterance(text);

    let voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) voices = voicesLoaded;

    let voice = voices.find(v => v.lang === 'en-IN');
    if (!voice) voice = voices.find(v => v.lang.startsWith('en'));
    if (voice) utterance.voice = voice;

    utterance.lang = 'en-IN';
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(utterance);
  }, 150);
}

// ── Mic Toggle (Continuous Mode) ────────────────────────────
function toggleMic() {
  if (continuousMode) {
    stopContinuousMode();
  } else {
    startContinuousMode();
  }
}

function startContinuousMode() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    addBubble('Tumhara browser voice support nahi karta — Chrome use karo!', 'jarvis');
    return;
  }

  continuousMode = true;
  const btn = document.getElementById('micBtn');
  btn.classList.add('listening');
  setStatus('🎤 Continuous mode ON — keep talking!');

  startListening();
}

function stopContinuousMode() {
  continuousMode = false;
  isListening = false;
  const btn = document.getElementById('micBtn');
  btn.classList.remove('listening');
  setStatus('Click mic or type below');

  if (recognition) {
    recognition.stop();
  }
  window.speechSynthesis.cancel();
}

function startListening() {
  if (!continuousMode) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    isListening = true;
    setStatus('🎤 Sun raha hoon... bolo!');
  };

  recognition.onresult = (e) => {
    const text = e.results[0][0].transcript;
    setStatus(`Suna: "${text}"`);
    sendCommand(text);
  };

 recognition.onerror = (e) => {
    console.log("Speech error:", e.error);
    if (e.error === 'no-speech') {
      if (continuousMode) {
        setTimeout(() => startListening(), 500);
      }
    } else {
      setStatus('Error (' + e.error + ') — dobara try karo');
      if (continuousMode) {
        setTimeout(() => startListening(), 1000);
      }
    }
  };
  
  recognition.onend = () => {
    isListening = false;
    if (continuousMode && !window.speechSynthesis.speaking) {
      setTimeout(() => startListening(), 500);
    }
  };

  recognition.start();
}

// ── Status Text ───────────────────────────────────────────
function setStatus(text) {
  document.getElementById('micStatus').textContent = text;
}

// ── Load History ──────────────────────────────────────────
async function loadHistory() {
  try {
    const res = await fetch('/history');
    const data = await res.json();
    const list = document.getElementById('historyList');

    if (data.length === 0) {
      list.innerHTML = '<div class="empty-state">No commands yet — start talking to Jarvis!</div>';
      return;
    }

    list.innerHTML = '';
    data.slice().reverse().forEach(item => {
      const div = document.createElement('div');
      div.className = 'history-item';
      div.innerHTML = `
        <div class="history-time">${item.time}</div>
        <div class="history-cmd">
          <div class="cmd-text">🎤 "${item.command}"</div>
          <div class="cmd-response">💬 ${item.response}</div>
        </div>
        <div class="history-action">${item.action}</div>
      `;
      list.appendChild(div);
    });

  } catch (err) {
    console.error('History load nahi hui:', err);
  }
}