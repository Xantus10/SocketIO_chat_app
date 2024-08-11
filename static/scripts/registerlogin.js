var socketIO = io();

function usernameInUse() {
  let msg = document.getElementById("name");
  if (msg.value === "") return;
  socketIO.emit("usernameInUse", {username: msg.value});
}

socketIO.on("usernameInUseReply", function (rep) {
  if (rep.status === "Y") {
    document.getElementById("name").style.backgroundColor = "lightcoral";
  } else {
    document.getElementById("name").style.backgroundColor = "lightgreen";
  }
});

function passwordCheck() {
  pass = document.getElementById("password").value;
  check = document.getElementById("check").value;
  passp = document.getElementById("passp");
  if (pass.length < 8) {
    passp.style.display = "flex";
    passp.innerHTML = "Password must be longer than 8 characters!";
    return;
  } else if (pass !== check) {
    passp.style.display = "flex";
    passp.innerHTML = "Passwords don't match!";
  } else {
    passp.style.display = "none";
  }
}
