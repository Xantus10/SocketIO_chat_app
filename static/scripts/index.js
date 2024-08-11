var socketIO = io();

function codeInUse() {
  let msg = document.getElementById("code");
  if (msg.value === "") return;
  socketIO.emit("codeInUse", {code: msg.value});
}

socketIO.on("codeInUseReply", function (rep) {
  if (rep.status === "Y") {
    document.getElementById("code").style.backgroundColor = "lightcoral";
  } else {
    document.getElementById("code").style.backgroundColor = "lightgreen";
  }
});
