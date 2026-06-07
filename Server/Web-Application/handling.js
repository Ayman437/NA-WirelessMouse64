const accessPassKey = prompt("Please enter your access key: ");
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|OperaMini/i.test(navigator.userAgent);
const userAgent = navigator.userAgent;
const pad = document.getElementById("touchpad");
const coords = document.getElementById("coords");
const checkBoxMouseBasedType = document.getElementById("checkBoxMouseBasedType");
const wheel = document.getElementById("wheel");
const DOUBLE_TAP_DELAY = 250;
const MOVE_THRESHOLD = 30;
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let lastTpadX = 0;
let lastTpadY = 0;
let lastTapTime = 0;
let lastMouseX = 0;
let lastMouseY = 0;
let lastMouseMoveTime = 0;
let startWheelY = 0;
let isItStopped = true;
let doubleTap = false;
let isMouseDown = false;
let isUserBlocked = false
let isAccessPermitted = false;
let isOverlayFlexed = false
let cursor = false
let instruction = false
let mouseListened = false;
let didItSendAMove = false;
let isItAccOrTpad = "Acc";
let Interval5923;
let pointerType;

fetch(`/login-${accessPassKey}`, {method: "POST", body: userAgent}).then(response => response.text()).then(async text =>{
    if (text !== "Access permitted!"){
        await fetch(`/wrongKey-${accessPassKey}`, {method: "POST", body: userAgent});
        alert("Access denied!");

        return;
    }else{
        isAccessPermitted = true;
        document.body.style.display = "block";

        checkedTLSIO();
    }
});


wheel.addEventListener("touchmove", (e) => {
    let currentWheelY = e.touches[0].clientY;

    e.preventDefault();

    if(currentWheelY < startWheelY){
        scroll("UP");
    }else if(currentWheelY > startWheelY){
        scroll("DOWN");
    }

    startWheelY = currentWheelY;
});

pad.addEventListener("touchstart", function(e){
    const now = Date.now();
    const LXYValueX = (e.touches[0].clientX) - (lastTpadX);
    const LXYValueY = (e.touches[0].clientY) - (lastTpadY);
    const distance = Math.sqrt((LXYValueX * LXYValueX) + (LXYValueY * LXYValueY));

    if (now - lastTapTime < DOUBLE_TAP_DELAY) {
        if (distance < MOVE_THRESHOLD){
        doubleTap = true;
        isMouseDown = true;

        sendClickLD();
        }
    }

    lastTapTime = now;

    lastTpadX = e.touches[0].clientX;
    lastTpadY = e.touches[0].clientY;
});

pad.addEventListener("touchend", function(){
if (doubleTap && isMouseDown) {
    isMouseDown = false;

    sendClickLU();
}

doubleTap = false;
});


pad.addEventListener("touchmove", function(e){
    e.preventDefault();

    const touch = e.touches[0];

    const x = touch.clientX;
    const y = touch.clientY;

    deltaX = x - lastTpadX;
    deltaY = y - lastTpadY;

    lastTpadX = x;
    lastTpadY = y;

    coords.innerText = `X: ${Math.round(x)}, Y: ${Math.round(y)}`;

    if (isItAccOrTpad == "Tpad" && !isOverlayFlexed && !isUserBlocked) {
    var data = "Tpad(" + deltaX + ", " + deltaY + ")";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
    }

});

if (!isMobile){
    document.body.innerText = "Only mobiles are allowed to use this web application!";
}

const mouseSpeedslider = document.getElementById("mouseSpeed");
const mouseSpeedValue = document.getElementById("mouseSpeedValue");

mouseSpeedslider.oninput = function(){
    mouseSpeedValue.textContent = this.value;
    sendMouseSpeedvalue(this.value);
}


function checkedTLSIO(){
      isItAccOrTpad = "Tpad";

        document.getElementById("touchPaddCh").style.backgroundColor = "rgba(0, 0, 0, 0.678)";
        document.getElementById("touchPaddCh").style.color = "white";

        document.getElementById("accCh").style.backgroundColor = "#ccc"
        document.getElementById("accCh").style.color = "black";

        // var data = `{'accX': 0, 'accY': 0, 'accZ': 9.8}`;
        var data = `{'accX': 0, 'accY': 0}`;

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.text())
    .catch(err => console.error(err));
}

function start(){

    if (document.getElementById("rlcB").innerHTML == 'Tap here to start'){
        if (isItStopped){
            isItStopped = false
             // For ios needs permission
    if (typeof DeviceMotionEvent.requestPermission === 'function'){

        DeviceMotionEvent.requestPermission().then(response => { if (response === 'granted'){
            window.addEventListener('devicemotion', handleMotion);
        }else{
            alert("Permission denied!");
        }
        }).catch(console.error);
      }else{
        // Adnroid and others

        window.addEventListener("devicemotion", handleMotion);
        rcButton = document.getElementById("rc");
        lcbutton = document.getElementById("lc");
        rcButton.addEventListener("touchstart", sendClickRD);
        rcButton.addEventListener("touchend", sendClickRU);
        lcbutton.addEventListener("touchstart", sendClickLD);
        lcbutton.addEventListener("touchend", sendClickLU);
        rcButton.addEventListener("touchstart", sendClickRD);
        rcButton.addEventListener("touchend", sendClickRU);
        lcbutton.addEventListener("touchstart", sendClickLD);
        lcbutton.addEventListener("touchend", sendClickLU);
        sendMouseSpeedvalue(35);
      }
      document.getElementById("rlcB").innerHTML = 'Tap here to stop';
      document.getElementById("entirePage").style.display = "block";

      checkBoxMouseBasedType.addEventListener("change", () => {
      if (checkBoxMouseBasedType.checked){
      checkedTLSIO();
      }else{
        isItAccOrTpad = "Acc";

        document.getElementById("accCh").style.backgroundColor = "rgba(0, 0, 0, 0.678)";
        document.getElementById("accCh").style.color = "white";

        document.getElementById("touchPaddCh").style.backgroundColor = "#ccc"
        document.getElementById("touchPaddCh").style.color = "black";
      }
      });
        }

    }else{
        if (document.getElementById("latencyTest").innerHTML == "Stop latency test"){
            startLatencyTest();
        }

        if (isItStopped){
            isItStopped = false;
            document.getElementById("entirePage").style.display = "block";
            document.getElementById("rlcB").innerHTML = 'Tap here to stop';
        }else{
            isItStopped = true;
            document.getElementById("entirePage").style.display = "none";
            document.getElementById("rlcB").innerHTML = 'Tap here to start';

            var data = `{'accX': 0, 'accY': 0}`;

            fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
        }
    }
    }


function handleMotion(event){
    const acc = event.accelerationIncludingGravity;
    let accx = acc.x;
    let accy = acc.y;
    let accz = acc.z;

    if (accx == null){
        accx = 0.0;
    }
    if (accy == null){
        accy = 0.0;
    }
    if (accz == null){
        accz = 0.0;
    }

    document.getElementById('output').innerText =
    `Accelerometer X,Y,Z Values\n`+
    `X: ${accx.toFixed(2)} ` +
    `Y: ${accy.toFixed(2)} ` +
    `Z: ${accz.toFixed(2)}`;

    if (!isItStopped){
if (isItAccOrTpad == "Acc" && !isOverlayFlexed && !isUserBlocked) {
        // var data = `{'accX': ${accx}, 'accY': ${accy}, 'accZ': ${accz}}`;
        var data = `{'accX': 0, 'accY': 0}`;

      if (accy > 0.5 || accy < -0.5 || accx > 1 || accx < -1){
        data = `{'accX': ${accx}, 'accY': ${accy}}`;
        didItSendAMove = true;
      }

      if (didItSendAMove){
        if (data === `{'accX': 0, 'accY': 0}`){
            didItSendAMove = false;
        }
    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
    }
      }
    }
}

function sendMouseSpeedvalue(value){
    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: "MouseSpeed: " + value
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function scroll(value){
    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: "Scroll: " + value
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendClickRD(){
    data = "RCD";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}
function sendClickRU(){
    data = "RCU";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendClickLD(){
    data = "LCD";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendClickLU(){
    data = "LCU";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendBackwardD(){
    data = "BD";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendBackwardU(){
    data = "BU";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendForwardD(){
    data = "FD";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendClickWheelD(){
    data = "WCD";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendClickWheelU(){
    data = "WCU";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function sendForwardU(){
    data = "FU";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: data
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
}

function startLatencyTest(){
    if (document.getElementById("latencyTest").innerHTML == "Start latency test"){
        document.getElementById("latencyTest").innerHTML = "Stop latency test";
    var interval87538 = setInterval(() =>{
    if (document.getElementById("latencyTest").innerHTML == "Stop latency test"){
    const startTime = Date.now();

    if (!isOverlayFlexed && !isUserBlocked){
    fetch(`${window.location.href}data`, { method: "POST" }).then(() => {
        const endTime = Date.now();
        const latency = `Latency(${(endTime - startTime)})`;

        document.getElementById('latencyValue').innerHTML = `${endTime - startTime}ms`;
        updateLatencyStrength();

        fetch(`${window.location.href}data`, {
        method: "POST",
        body: latency
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
    });
    }
    }else{
        clearInterval(interval87538);
    }

    }, 1000 / 30);
    }else{
        document.getElementById("latencyTest").innerHTML = "Start latency test";
    }
}

checkBoxMouseBasedType.checked = true;
//checkedTLSIO();


function updateLatencyStrength(){
    let latencyValueThis = document.getElementById("latencyValue").innerHTML;
    latencyValueThis = Number(latencyValueThis.replace("ms", ""));

    const latencyValueItem = document.getElementById("latencyValue");
    if (latencyValueThis <= 20){
        latencyValueItem.style.backgroundColor = "#00C853";
    }else if (latencyValueThis >= 21 && latencyValueThis <= 40){
        latencyValueItem.style.backgroundColor = "#2E7D32";
    }else if (latencyValueThis >= 41 && latencyValueThis <= 70){
        latencyValueItem.style.backgroundColor = "#C0CA33";
    }else if (latencyValueThis >= 71 && latencyValueThis <= 120){
        latencyValueItem.style.backgroundColor = "#FBC02D";
    }else if (latencyValueThis >= 121 && latencyValueThis <= 200){
        latencyValueItem.style.backgroundColor = "#F57C00";
    }else if (latencyValueThis > 200){
        latencyValueItem.style.backgroundColor = "#C62828";
    }
}

document.addEventListener("pointermove", (e) => {
    pointerType = e.pointerType;
});

fetch("/checkconnected", {
        method: "POST",
        body: userAgent
        }).then(response => response.text()).then(text => {
        if (text == "You're blocked!"){
            isUserBlocked = true;
            document.body.innerText = "You are blocked from the server!";
            stopCheckingForConnection();
        }else if (text == "You're kicked!"){
            isUserBlocked = true;
            document.body.innerText = "You are kicked from the server!";
            stopCheckingForConnection();
        }
});

function startCheckingForConnection(){
Interval5923 = setInterval(()=>{
    if (isAccessPermitted){
            fetch("/checkconnected", {
        method: "POST",
        body: userAgent
    }).then(response => response.text()).then(text => {
        if (text === "You're blocked!"){
            isUserBlocked = true;
            document.body.innerText = "You are blocked from the server!";
            stopCheckingForConnection();
        }else if (text === "You're kicked!"){
            isUserBlocked = true;
            document.body.innerText = "You are kicked from the server!";
            stopCheckingForConnection();
        }else if(text === "Controller"){
            document.getElementById("unavailableOverlay").style.display = "none";
            isOverlayFlexed = false;
        }else if(text === "NotController"){
            document.getElementById("unavailableOverlay").style.display = "flex";
            isOverlayFlexed = true;
        }
    })
    }
}, 2000);
}

function stopCheckingForConnection(){
    clearInterval(Interval5923);
}

startCheckingForConnection();

function handleExternalMouse(event){
    event.preventDefault();

    if (document.pointerLockElement === document.body){
            mouseX += event.movementX;
            mouseY += event.movementY;

            cursor.style.left = `${mouseX}px`;
            cursor.style.top = `${mouseY}px`;
    }

    const x = mouseX
    const y = mouseY

    deltaX = x - lastMouseX;
    deltaY = y - lastMouseY

    lastMouseX = x;
    lastMouseY = y;

    coords.innerText = `X: ${Math.round(x)}, Y: ${Math.round(y)}`;

    if (!isOverlayFlexed && !isUserBlocked && pointerType === "mouse") {
    var data = "Tpad(" + deltaX + ", " + deltaY + ")";

    fetch(`${window.location.href}data`, {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.text())
    .then(text => console.log(`Server response: ${text}`))
    .catch(err => console.error(err));
    }
}

function handleExternalMouseDown(event){
    event.preventDefault();

    if (event.button == 0){
        sendClickLD();
    }else if (event.button == 2){
        sendClickRD();
    }else if (event.button == 4){
        sendForwardD();
    }else if (event.button == 3){
        sendBackwardD();
    }else if (event.button == 1){
        sendClickWheelD();
    }
}

function handleExternalMouseUp(event){
    event.preventDefault();

    if (event.button == 0){
        sendClickLU();
    }else if (event.button == 2){
        sendClickRU();
    }else if (event.button == 4){
        sendForwardU();
    }else if (event.button == 3){
        sendBackwardU();
    }else if (event.button == 1){
        sendClickWheelU();
    }
}

function handleExternalMouseWheel(event){
    event.preventDefault();

    if (event.deltaY > 0) {
        scroll("DOWN");
    }else{
        scroll("UP");
    }
}

document.addEventListener("visibilitychange", () => {
    if (document.hidden){
        stopCheckingForConnection();

        document.getElementById("leavedPage").style.display = "flex";
        isOverlayFlexed = true
        document.exitPointerLock();
    }
});

setInterval(()=>{
    if (pointerType === "mouse" && !isOverlayFlexed && !isUserBlocked ){
        document.getElementById("mouseArea").style.display = "block";
        if (!mouseListened){
        mouseListened = true;
        cursor = document.getElementById('cursor');
        instruction = document.getElementById('instruction');
        cursor.style.left = `${mouseX}px`;
        cursor.style.top = `${mouseY}px`;
        window.addEventListener("mousemove", handleExternalMouse);
        window.addEventListener("mousedown", handleExternalMouseDown);
        window.addEventListener("mouseup", handleExternalMouseUp);
        window.addEventListener("wheel", handleExternalMouseWheel);
        window.addEventListener("contextmenu", function (e){
            e.preventDefault();
        });
        document.addEventListener('pointerlockchange', () => {
            if (document.pointerLockElement === document.body) {
                instruction.style.display = 'none';
            } else {
                instruction.style.display = 'block';
            }
        });
        document.body.addEventListener('click', () => {
            document.body.requestPointerLock();
        });
        }
    }else{
        document.getElementById("mouseArea").style.display = "none";

        mouseListened = false
        window.removeEventListener("mousemove", handleExternalMouse, true);
        window.removeEventListener("mousedown", handleExternalMouseDown, true);
        window.removeEventListener("mouseup", handleExternalMouseUp, true);
        window.removeEventListener("wheel", handleExternalMouseWheel, true);
        window.removeEventListener("contextmenu", function (e){
            e.preventDefault();
        }, true);
        ocument.removeEventListener('pointerlockchange', () => {
            if (document.pointerLockElement === document.body) {
                instruction.style.display = 'none';
            } else {
                instruction.style.display = 'block';
            }
        }, true);
        document.body.removeEventListener('click', () => {
            document.body.requestPointerLock();
        }, true);

        document.exitPointerLock();
    }
}, 1000);