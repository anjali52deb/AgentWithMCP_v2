// ----------------------- GLOBAL STATE -----------------------

let chatSessions = [];
let activeSessionIndex = null;
let pendingAttachments = [];

// ============= added on 08-May
function renderPendingAttachments() {
  const container = document.getElementById("pendingAttachmentsPreview");
  container.innerHTML = "";

  pendingAttachments.forEach((att, index) => {
      const div = document.createElement("div");
      div.className = "pending-attachment";

      if (att.dataUrl.startsWith("data:image")) {
          div.innerHTML = `<img src="${att.dataUrl}">`;
      }

      div.innerHTML += `<span>${att.filename}</span> <button onclick="removePendingAttachment(${index})">Remove</button>`;
      container.appendChild(div);
  });

  container.style.display = pendingAttachments.length > 0 ? "flex" : "none";
}

function removePendingAttachment(index) {
  pendingAttachments.splice(index, 1);
  renderPendingAttachments();
}


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

// ----------------------- UTILS -----------------------
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

function clearMessages() {
  document.getElementById("messages").innerHTML = "";
}

// ----------------------- SESSION MANAGEMENT -----------------------
function startNewChat() {
  const timestamp = new Date();
  const title = `📝 New Chat at ${timestamp.getHours()}:${timestamp.getMinutes().toString().padStart(2, '0')}`;

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

// ----------------------- MESSAGE SENDING -----------------------
async function sendMessage() {
  const inputBox = document.getElementById("user-input");
  const message = inputBox.value.trim();
  if (!message) return;

  /// NEW LINE
  if (activeSessionIndex === null) startNewChat();

  const msgDiv = appendMessage("Me", message, "user");
  inputBox.value = "";
  setMsgTick(msgDiv, "sent");

  /// NEW LINE
  chatSessions[activeSessionIndex].messages.push({ sender: "user", text: message, timestamp: new Date() });
  saveChatSessions();
  
  // [NEW] If this is the first user message → update session title to be meaningful
  if (chatSessions[activeSessionIndex].messages.length === 1) {
      chatSessions[activeSessionIndex].title = message.length > 30 ? message.substring(0, 30) + '...' : message;
      renderChatHistory();
      saveChatSessions();
  }

  const modelType = getSelectedModel();
  const sessionId = getSessionId();

  try {
    const response = await fetch("https://agentwithmcp.onrender.com/agent/message", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        session_id: sessionId,
        query: message,
        model: modelType,
        attachments: pendingAttachments
      }),
    });

    const data = await response.json();
    if (data.response && data.response.startsWith("Access denied")) {
        alert(data.response); // Show popup
        return;
    }
    const agentReply = data.response ?? "No response from agent.";
    appendMessage("Vika.AI", agentReply, "agent");

    /// NEW LINE
    chatSessions[activeSessionIndex].messages.push({ sender: "agent", text: agentReply, timestamp: new Date() });
    
    setTimeout(() => setMsgTick(msgDiv, "read"), 1000);
    pendingAttachments = [];  // Clear after sending
    renderPendingAttachments();

  } catch (error) {
    appendMessage("Vika.AI", "⚠️ **Failed to reach Agent**. API Call Error in **sendMessage()** catch", "agent");
  }
}

// ----------------------- MESSAGE UI -----------------------      
function appendMessage(sender, text, type, isHtml = false) {
    const messages = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = `message ${type}`;

    const now = new Date();
    const year = now.getFullYear();
    const month = (now.getMonth() + 1).toString().padStart(2, "0");
    const day = now.getDate().toString().padStart(2, "0");
    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    const fullDateTime = `${year}-${month}-${day} ${hours}:${minutes}`;
    
    /// Replaced line
    let inner = `<strong>${sender}:</strong> ${marked.parseInline(text)}`;

    if (isHtml) {
        inner = `<strong>${sender}:</strong> ${text}`;
    } else {
        if (type === "agent") {
            // Full markdown (paragraph support)
            const formattedText = marked.parse(text);
            inner = `<strong>${sender}:</strong><div class="agent-response">${formattedText}</div>`;
        } else {
            // Inline markdown (user message simple)
            const formattedText = marked.parseInline(text);
            inner = `<strong>${sender}:</strong> ${formattedText}`;
        }
    }
    if (type === "user") {
        inner += `<span class="msg-tick" title="Sent">&#10003;</span>`;
    }
    inner += `<span class="message-time">${fullDateTime}</span>`;
    div.innerHTML = inner;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
}

function setMsgTick(div, status) {
  const tick = div.querySelector('.msg-tick');
  if (!tick) return;
  if (status === "read") {
    tick.innerHTML = "&#10003;&#10003;";
    tick.classList.add("read");
    tick.title = "Read";
  } else {
    tick.innerHTML = "&#10003;";
    tick.classList.remove("read");
    tick.title = "Sent";
  }
}

// SVGs as strings for easy swapping
const leftArrowSVG = `
  <svg width="24" height="24" viewBox="0 0 32 32">
    <circle cx="16" cy="16" r="15" stroke="grey" stroke-width="2" fill="none"/>
    <polyline points="20,10 12,16 20,22" fill="none" stroke="grey" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
`;
const rightArrowSVG = `
  <svg width="24" height="24" viewBox="0 0 32 32">
    <circle cx="16" cy="16" r="15" stroke="grey" stroke-width="2" fill="none"/>
    <polyline points="12,10 20,16 12,22" fill="none" stroke="grey" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
`;
// Track collapsed state for each sidebar
let leftCollapsed = false;
let rightCollapsed = false;

function toggleSidebar(side) {
  if (side === "left") {
    const sidebar = document.getElementById("leftSidebar");
    const btn = document.getElementById("leftToggleBtn");
    const iconSpan = btn.querySelector("span");
    leftCollapsed = !leftCollapsed;
    sidebar.classList.toggle("sidebar-collapsed", leftCollapsed);
    btn.classList.toggle("left-collapsed", leftCollapsed);
    iconSpan.innerHTML = leftCollapsed ? rightArrowSVG : leftArrowSVG;
  } else {
    const sidebar = document.getElementById("rightSidebar");
    const btn = document.getElementById("rightToggleBtn");
    const iconSpan = btn.querySelector("span");
    rightCollapsed = !rightCollapsed;
    sidebar.classList.toggle("sidebar-collapsed", rightCollapsed);
    btn.classList.toggle("right-collapsed", rightCollapsed);
    iconSpan.innerHTML = rightCollapsed ? leftArrowSVG : rightArrowSVG;
  }
}
lucide.createIcons();

// ----------------------- CHAT HISTORY RENDER -----------------------
function renderChatHistory() {
    const container = document.getElementById("chatHistoryContainer");
    container.innerHTML = "";

    // Remove active class from all (precaution)
    document.querySelectorAll(".history-item").forEach(item => {
        item.classList.remove("active");
    });

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
                if (sess.index === activeSessionIndex) {
                    item.classList.add("active");
                }

                // Make the inner HTML -> title + options (...)
                item.innerHTML = `
                  <span class="history-item-title" style="flex:1 1 auto; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${sess.title}</span>
                  <span class="history-item-options" style="margin-left:auto; cursor:pointer; display:inline-block; font-weight:bold;" onclick="event.stopPropagation(); showHistoryOptions(${sess.index}, this)">⋯</span>
                `;
                item.style.display = "flex";
                item.style.alignItems = "center";

                // Handle clicking on the title → load session
                item.querySelector('.history-item-title').onclick = () => {
                    loadSessionMessages(sess.index);
                    renderChatHistory();
                };

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
// ================================================

// Do logout and redirect
async function doLogout() {
  const SUPABASE_URL = "https://hvqijjmhhhukoarccqhh.supabase.co";
  const tokenDataRaw = localStorage.getItem("authData");
  const accessToken = tokenDataRaw ? JSON.parse(tokenDataRaw)?.accessToken : null;

  // If an access token was found, attempt to call the Supabase logout endpoint
  if (accessToken) {
    try {
        const response = await fetch(`${SUPABASE_URL}/auth/v1/logout`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${accessToken}`,
                "Content-Type": "application/json"
            }
        });
        if (!response.ok) {
            if (response.status === 401) {
                console.log("Token expired or session invalid. Treating as logged out.");
            } else {
                console.error("Logout error:", response.status);
            }
        } else {
            console.log("Successfully called Supabase logout endpoint.");
        }
        
    } catch (err) {
        console.error("Network error during logout API call:", err);
    }
  } else {
      // No valid token was found in localStorage
      console.log("No access token found in localStorage, proceeding without API logout call.");
  }

  // Regardless of API call success or token presence, clear local storage and redirect
  // This ensures the client-side session is cleared.
  localStorage.clear();
  window.location.href = "https://ai.story360degree.com/";
}

// Attach window close/tab close handler
window.addEventListener("beforeunload", (event) => {
    doLogout();
});

// ======== Chat History Management =======================================================

function showHistoryOptions(index, button) {
  // Remove existing menu if already open
  const existingMenu = document.getElementById("history-options-menu");
  if (existingMenu) existingMenu.remove();

  // Create menu
  const menu = document.createElement("div");
  menu.id = "history-options-menu";
  menu.className = "history-options-menu";
  menu.innerHTML = `
      <div style="font-weight:normal;" onclick="renameSession(${index})">Rename</div>
      <div style="font-weight:normal;" onclick="deleteSession(${index})">Delete</div>
  `;

  // Position and add
  button.parentNode.appendChild(menu);

  // Close on outside click
  document.addEventListener("click", function handler(e) {
      if (!menu.contains(e.target) && e.target !== button) {
          menu.remove();
          document.removeEventListener("click", handler);
      }
  });
}

function renameSession(index) {
  const newName = prompt("Enter new chat name:", chatSessions[index].title);
  if (newName) {
      chatSessions[index].title = '📝 ' + newName;
      saveChatSessions();
      renderChatHistory();
  }
}

function deleteSession(index) {
  if (!confirm("Are you sure you want to delete this chat?")) return;

  chatSessions.splice(index, 1);
  saveChatSessions();
  renderChatHistory();

  if (index === activeSessionIndex) {
      clearMessages();
      activeSessionIndex = null;
  }
}

// ======================================================================

// 1️⃣ Voice Command (Microphone)

let recognition;
function startVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Your browser doesn't support Speech Recognition");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.start();

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("user-input").value = transcript;
        sendMessage(); // Automatically send the captured voice as message
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
    };
}

// 2️⃣ Camera Snapshot (Webcam)
async function captureImage() {
  const video = document.createElement('video');
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;
  await video.play();

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageDataUrl = canvas.toDataURL('image/png');

  stream.getTracks().forEach(track => track.stop());

  // Send imageDataUrl to backend or append to chat
  appendMessage("Me", `<img src="${imageDataUrl}" style="max-width:200px;">`, "user", true);

  // Optional: Send to backend API
  // await sendAttachment(imageDataUrl);
}


window.addEventListener('DOMContentLoaded', function () {
  document.getElementById("sendButton").addEventListener('click', sendMessage);
  document.getElementById("voiceButton").addEventListener('click', startVoiceRecognition);
  document.getElementById("cameraButton").addEventListener('click', captureImage);
  document.getElementById("attachmentButton").addEventListener('click', () => {
      document.getElementById("fileInput").click();
  });

  // Handle file upload and preview
  // ============== Added on 08-May-
  document.getElementById("fileInput").addEventListener('change', function(event) {
      const files = event.target.files;
      if (files.length === 0) return;

      Array.from(files).forEach(file => {
          const reader = new FileReader();
          reader.onload = function(e) {
              const fileContent = e.target.result;
              pendingAttachments.push({
                  filename: file.name,
                  dataUrl: fileContent
              });
              renderPendingAttachments();
          };
          reader.readAsDataURL(file);
      });
  });



});


// ======================= END ============================      