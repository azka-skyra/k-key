// Y-Key Chatbot Widget Logic

let chatSessionId = null;
let chatLoading = false;

const WELCOME_MSG = "Hai! 👋 Aku **Y-Key Bot**, asisten AI kamu buat bantu pilih produk Y-Key. Aku bisa kasih rekomendasi yogurt & keychain sesuai seleramu. Kamu lagi cari produk untuk siapa / acara apa nih? 🍓🏷️";

const QUICK_PROMPTS = [
  "Mau rekomendasi yogurt buat sarapan",
  "Berapa harga keychain custom?",
  "Cara pemesanan gimana?",
  "Mau keychain buat hadiah ultah",
];

document.addEventListener('DOMContentLoaded', () => {
  addMessage('assistant', WELCOME_MSG);
  renderQuickPrompts();
});

function toggleChatbot() {
  const panel = document.getElementById('chatbot-panel');
  const bubble = document.getElementById('chatbot-bubble');
  if (panel.style.display === 'none' || !panel.style.display) {
    panel.style.display = 'flex';
    bubble.style.display = 'none';
  } else {
    panel.style.display = 'none';
    bubble.style.display = 'flex';
  }
}

function addMessage(role, content) {
  const messages = document.getElementById('chatbot-messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = `<div class="message-bubble">${renderMarkdownLite(content)}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function renderMarkdownLite(text) {
  // Simple **bold** parsing
  return text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

function renderQuickPrompts() {
  const container = document.getElementById('quick-prompts');
  container.innerHTML = QUICK_PROMPTS.map(q =>
    `<button class="quick-prompt" onclick="sendQuickPrompt('${q}')">${q}</button>`
  ).join('');
}

function sendQuickPrompt(prompt) {
  document.getElementById('chatbot-input').value = prompt;
  sendMessage(new Event('submit'));
}

async function sendMessage(e) {
  e.preventDefault();
  if (chatLoading) return;

  const input = document.getElementById('chatbot-input');
  const message = input.value.trim();
  if (!message) return;

  addMessage('user', message);
  input.value = '';
  chatLoading = true;

  // Show typing indicator
  const messages = document.getElementById('chatbot-messages');
  const typingDiv = document.createElement('div');
  typingDiv.className = 'message assistant';
  typingDiv.id = 'typing-indicator';
  typingDiv.innerHTML = '<div class="message-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
  messages.appendChild(typingDiv);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, sessionId: chatSessionId }),
    });
    const data = await res.json();
    if (data.sessionId) chatSessionId = data.sessionId;
    document.getElementById('typing-indicator')?.remove();
    addMessage('assistant', data.reply || 'Maaf, aku gak nangkap. Coba lagi ya 🙏');
  } catch (err) {
    document.getElementById('typing-indicator')?.remove();
    addMessage('assistant', 'Yah, koneksi lagi bermasalah nih 🙏 Coba kirim ulang ya.');
  } finally {
    chatLoading = false;
  }
}