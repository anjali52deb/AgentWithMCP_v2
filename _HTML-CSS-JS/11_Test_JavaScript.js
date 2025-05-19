// vika_ai_agent_final.js (FINAL with localStorage support)

let chatSessions = [];
let activeSessionIndex = null;

// -------------------- Load from localStorage on Page Load --------------------
window.addEventListener("load", () => {
    loadChatSessions();
    if (chatSessions.length === 0) {
        startNewChat();
    } else {
        renderChatHistory();
        activeSessionIndex = chatSessions.length - 1;
        loadSessionMessages(activeSessionIndex);
    }
});

function saveChatSessions() {
    localStorage.setItem("chatSessions", JSON.stringify(chatSessions));
}

function loadChatSessions() {
    const saved = localStorage.getItem("chatSessions");
    if (saved) {
        chatSessions = JSON.parse(saved);
    }
}

// -------------------- SESSION MANAGEMENT --------------------
function startNewChat() {
    const timestamp = new Date();
    const title = `Chat at ${timestamp.getHours()}:${timestamp.getMinutes().toString().padStart(2, '0')}:${timestamp.getSeconds().toString().padStart(2, '0')}`;

    chatSessions.push({
        startedAt: timestamp,
        title: title,
        messages: []
    });

    activeSessionIndex = chatSessions.length - 1;
    clearMessages();
    renderChatHistory();
    saveChatSessions();
}

function clearMessages() {
    document.getElementById("messages").innerHTML = "";
}

// -------------------- MESSAGE SENDING --------------------
async function sendMessage() {
    const inputBox = document.getElementById("user-input");
    const message = inputBox.value.trim();
    if (!message) return;

    if (activeSessionIndex === null) startNewChat();

    const msgDiv = appendMessage("Me", message, "user");
    inputBox.value = "";
    setMsgTick(msgDiv, "sent");

    chatSessions[activeSessionIndex].messages.push({ sender: "user", text: message, timestamp: new Date() });
    saveChatSessions();

    const modelType = getSelectedModel();
    const sessionId = getSessionId();

    try {
        const response = await fetch("https://agentwithmcp.onrender.com/agent/message", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ session_id: sessionId, query: message, model: modelType })
        });

        const data = await response.json();
        const agentReply = data.response ?? "No response from agent.";
        appendMessage("Vika.AI", agentReply, "agent");

        chatSessions[activeSessionIndex].messages.push({ sender: "agent", text: agentReply, timestamp: new Date() });
        saveChatSessions();

        setTimeout(() => setMsgTick(msgDiv, "read"), 1000);

    } catch (error) {
        appendMessage("Vika.AI", "⚠️ **Failed to reach Agent**.", "agent");
    }
}

// -------------------- UI MESSAGE RENDER --------------------
function appendMessage(sender, text, type) {
    const messages = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = `message ${type}`;

    const now = new Date();
    const time = `${now.getHours()}:${now.getMinutes().toString().padStart(2, "0")}`;

    let inner = `<strong>${sender}:</strong> ${marked.parseInline(text)}`;
    if (type === "user") {
        inner += `<span class="msg-tick" title="Sent">&#10003;</span>`;
    }
    inner += `<span class="message-time">${time}</span>`;

    div.innerHTML = inner;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
}

function setMsgTick(div, status) {
    const tick = div.querySelector('.msg-tick');
    if (!tick) return;
    tick.innerHTML = status === "read" ? "&#10003;&#10003;" : "&#10003;";
    tick.className = status === "read" ? "msg-tick read" : "msg-tick";
}

// -------------------- CHAT HISTORY --------------------
function renderChatHistory() {
    const container = document.getElementById("chatHistoryContainer");
    container.innerHTML = "";

    const groups = { Today: [], Yesterday: [], "This Week": [], Earlier: [] };
    const now = new Date();

    chatSessions.forEach((session, index) => {
        const date = new Date(session.startedAt);
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
        
        let groupKey = diffDays === 0 ? "Today" : diffDays === 1 ? "Yesterday" : diffDays < 7 ? "This Week" : "Earlier";
        groups[groupKey].push({ index, title: session.title });
    });

    for (const [section, sessions] of Object.entries(groups)) {
        if (sessions.length > 0) {
            const sectionDiv = document.createElement("div");
            sectionDiv.innerHTML = `<strong>${section}</strong>`;
            sessions.forEach(sess => {
                const item = document.createElement("div");
                item.className = "history-item";
                item.textContent = sess.title;
                item.onclick = () => loadSessionMessages(sess.index);
                sectionDiv.appendChild(item);
            });
            container.appendChild(sectionDiv);
        }
    }
}

function loadSessionMessages(index) {
    activeSessionIndex = index;
    clearMessages();
    const session = chatSessions[index];
    session.messages.forEach(msg => {
        appendMessage(msg.sender === "user" ? "Me" : "Vika.AI", msg.text, msg.sender);
    });
}

function getSelectedModel() {
    const select = document.querySelector('select[name="llm"]');
    return select ? select.value : "Gemini";
}

function getSessionId() {
    let sessionId = sessionStorage.getItem("agent_session_id");
    if (!sessionId) {
        sessionId = Math.random().toString(36).substring(2);
        sessionStorage.setItem("agent_session_id", sessionId);
    }
    return sessionId;
}

async function doLogout() {
    localStorage.clear();
    window.location.href = "https://ai.story360degree.com/";
}
