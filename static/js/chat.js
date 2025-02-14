const apiBaseUrl = "http://18.236.231.159:5000";

// Function to display messages in the chat area
function displayMessage(content, isUserMessage = true) {
  const chatArea = document.getElementById("chatArea");
  const message = document.createElement("div");
  message.className =
    "message " + (isUserMessage ? "user-message" : "bot-message");

  if (!isUserMessage) {
    message.innerHTML = marked.parse(content);
  } else {
    message.textContent = content;
  }
  chatArea.appendChild(message);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function setPlaceholder(text) {
  document.getElementById("userInput").placeholder = text;
}

// Function to send a message
async function sendMessage() {
  const userInput = document.getElementById("userInput");
  const message = userInput.value.trim();

  if (message) {
    displayMessage(message); // Display full prompt in chat
    userInput.value = "";

    try {
      const response = await fetch(`${apiBaseUrl}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: message,
          sessionId: "defaultSession",
          endSession: false,
        }),
      });

      const data = await response.json();
      const botResponse = data.response || "No response from agent.";
      displayMessage(botResponse, false);
    } catch (error) {
      console.error("Error fetching response:", error);
      displayMessage("Error: Unable to reach the chatbot service.", false);
    }
  }
}

// Function to end the session and redirect to the login page
function endSession() {
  window.location.href = "/static/index.html";
}
