var socketIO = io();



// Recieving a message
socketIO.on("message", function (message) {createChatLine(message.sender, message.message, message.time);});
function createChatLine(sender, message, time) {
  document.getElementById("messageUL").innerHTML += `<li>
  <p class="smalltime">${time}</p>
  <p>${sender}${(sender === "") ? "[O] " : ": "}${message}</p></li>`;
  window.scrollTo(0, document.body.scrollHeight);
}

// Sending a message
function sendMessage() {
  let msg = document.getElementById("message");
  if (msg.value === "") return;
  socketIO.emit("message", {message: msg.value});
  msg.value = "";
}


// When user presses enter we send the message
window.addEventListener("DOMContentLoaded", function (event) {
  document.getElementById('message').addEventListener('keyup', function (event) {
    event.preventDefault();
    if (event.key === "Enter") {
      document.getElementById('submitButton').click();
    }
  });
});
