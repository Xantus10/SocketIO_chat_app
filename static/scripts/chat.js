var socketIO = io();

// Recieving a message
socketIO.on("message", function (message) {createChatLine(message);});
function createChatLine(message) {
  document.getElementById("messageUL").innerHTML += `<li><p>${message}</p></li>`;
}

// Sending a message
function sendMessage() {
  let msg = document.getElementById("message");
  if (msg.value === "") return;
  socketIO.emit("message", {message: msg.value});
  msg.value = "";
}


