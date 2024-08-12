var socketIO = io();



// Recieving a message
socketIO.on("message", function (message) {createChatLine(message.sender, message.message, message.time);});
function createChatLine(sender, message, time) {
  document.getElementById("messageUL").innerHTML += `<li>
  <p class="smalltime">${time}</p>
  <p>${sender}${(sender === "") ? "[O] " : ": "}${message}</p></li>`;
  window.scrollTo(0, document.body.scrollHeight);
}


// Person dis/connect count
socketIO.on("Dis/Connect", function (change) {changePersonCount(change.change)});
function changePersonCount(change) {
  let num = parseInt(document.getElementById("onlineCount").innerHTML);
  console.log(change);
  if (change === "+") {
    num++;
  } else {
    num--;
  }
  document.getElementById("onlineCount").innerHTML = num;
}


// Sending a message
function sendMessage() {
  let msg = document.getElementById("message");
  if (msg.value === "") return;
  socketIO.emit("message", {message: msg.value});
  msg.value = "";
}


window.addEventListener("DOMContentLoaded", function (event) {
  // When user presses enter we send the message
  document.getElementById('message').addEventListener('keyup', function (event) {
    event.preventDefault();
    if (event.key === "Enter") {
      document.getElementById('submitButton').click();
    }
  });
});
