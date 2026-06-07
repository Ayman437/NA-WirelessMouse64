# NA-WirelessMouse64

A flexible software that allows you to use your mobile phone as a wireless mouse for your PC with three different methods by hosting a local server on the PC so that any connected mobile phone to the same Wi-Fi as the PC can eventually access the server and be used as a wireless mouse.

## Architecture

```text
NA-WirelessMouse64/
│
├── Server/
│   │
│   ├── Info/
│   │   ├── BlockedDevices.txt      # List of blocked devics
│   │   ├── ConnectedDevices.txt    # Currently connected devices
│   │   ├── LastVisitsLog.txt       # Connection history log
│   │   ├── ServerOutputs.txt       # Server outputs log
│   │   └── Uptime.txt              # Server uptime
│   │
│   ├── Java/
│   │   ├── keystore.p12            # SSL certificate keystore
│   │   ├── MouseMover.java         # Mouse control implementation
│   │   ├── WebServer.jar           # Compiled web WebServer.java & MouseMover.java
│   │   └── WebServer.java          # Main server logic
│   │
│   ├── Web-Application/
│   │   ├── handling.js             # Client-side event handling
│   │   ├── index.html              # Main web-application interface
│   │   └── style.css               # Web-application user interface styling
│   │
│   ├── Configuration.json          # Software & server configuration settings
│   └── README.txt                  # Server's folder README.txt
│
├── app_version.txt                 # Current application version
├── exe_program.rar                 # Packaged executable release
├── Icon.ico                        # Application icon
├── NA-WirelessMouse64.py           # Main Python launcher / application
├── README.md                       # Project documentation
└── Sketch.jpeg                     # Design sketch / preview image
```

## Instructions for normal user

To download the software, download the `exe_program.rar` file and extract it
<br>
Then you can use it as an ordinary exe program.
<br>
Note that this works for `Windows 10+ 64-bit`.

## Version
- Current version: 1.0.0

## Software's User interface
When you open the software, you are going to see this interface:

- On top, there is a **server status** text label, it tells you whether the server is running or not and also shows you the URL of the web-application.
- Then, there is a section where it shows you 3 options:

1. **Server pot**, you can the port that the server uses, make sure that this port is not used by any other service, default is 3001.
2. **Server access key**, you can make your own access key for the web-application, every device that visits the web-application is asked for access key in order to have access to the full web-application, default is admin.
3. **Clear logs on server startup**, toggling this option on will make the server automatically clear logs files, which are `ServerOutputs.txt` and `LastVisitsLog.txt`, they exist at `NA-WirelessMouse64/Server/Info/`.

- Then, there is 3 buttons that do different functions.

1. **Start server**, this button starts hosting the server locally on your machine using the port that you chose earlier.
2. **Stop server**, this button sends a request to the server to shut down.
3. **Save changes**, every change you make in any option won't be saved unless you click this button.

- Then, there is the **Connected devices** section, it shows you in a table the currently connected devices, where you can also click on any shown device to whether block it or kick it out of the server. You need to know also that if there is a device shown in a green background, it's the device that currently has the priority access.
- Then, there is **Blocked & Kicked devices** section, it shows you in table all the blocked and kicked devices, note that you can also click on any device and chose whether to unblock (if blocked) it or to restore its access to the server (if kicked).
- Then, there is the **Visits log**, it shows you all the visits made by any device that has tried to access the web-application.
- Then, there is **Requests signals & Other** section, it has 5 features:

1. **Incoming requests**, it shows you literally every single request signal that the server receives, every signal is shown as a green light, it's composed of 3 lights given to the request method, 1. GET, 2. POST, 3. Other. The whole software has been programmed to send POST & GET requests, so if you see a green light for any Other request, it's sent form an external source.
2. **Uptime**, this shows you how much time the server is running.
3. **Outputs size**, this shows you the sum of `ServerOutputs.txt` and `LastVisitsLog.txt` files size.
4. **Logs size limit**, this lets you choose the max size of outputs size, if you want to make it limitless, enter OFF in the entry box, default is 30 MB.
5. **Single mouse controller**, enabling this option will prevent any connected device from using being used as a mouse for the PC unless it has the priority access.

-Then, in the bottom section, there is:
1. **Server outputs**, clicking this button creates another window contains all the server outputs in real-time.
2. There is a status text label that tells you what is happening right now in terms of fetching server status or saving changes, etc.

## Web-Application's user interface
When you open the web-application, you are going to encounter this interface:

- First thing you see when you open the web-application is an entry that asks you for the server access key, you need to enter the right access key in order to continue.
- Then - if you entered the right access key - you will see a button named `Tap here to start`, when you press it, it will show you the whole interface.
- Then, you will see your current device's accelerometer `x, y, z` values in real-time.
- Then, you're going to see the left click button, the mouse wheel button and the right click button.
- Then, you are going to see toggle button which make you choose between the accelerometer-based method or the touchpad-based method. Keep in mind that there is a third method that we're going to talk about later.
- Then, you will see the mouse speed option.
- Then, you will see the touchpad and it's x and y values.
- Then, you will see the `Start latency test` button, which makes you test your network speed in terms of transferring data, in details, it sends a request from your mobile phone to the server and waits for the response, once it receives a response, it calculates the time that this process had taken. Higher values of milliseconds means slower connection while smaller values means faster connection, and it really depends on how good your Wi-Fi router your PCa and your mobile phone.

## How to use?

1. Open the software on your PC.
2. Click on start server button.
3. After starting the server, open any internet browser on your mobile phone and enter the web-application URL shown in the software **"use the one that has an IP address, the one that has localhost only works for you PC"**.
4. Once you are in the web-application, it will ask you for your server access key, enter it, and use the full web-application.

## The 3 methods that you can use
In this software, there is 3 possible ways of using your mobile phone as a mouse for your PC.

1. **Touchpad-based**, this method will allow you to move your finger across the touchpad in the web-application, just like a touchpad in a laptop. **"Recommended"**.
2. **Accelerometer-based**, this method will use your X, Y values of your device's accelerometer in order to move the mouse, Tilting you device forward will move the mose up, backward will move it down, left will move it to the left side, right will move it to the right side and keeping it flat will stop the mose from moving. **"Not very recommended :)"**.
3. **OTG Mouse-to-PC control**, this method can turn your wired physical mouse into a wireless Wi-Fi mouse, just get an OTG and connect your wired mouse to your mobile phone using it and open the web-application and it will automatically detect it and allow you to use it as a wireless mouse for your PC. **"Most recommended"**.

## Additional notes
- When you use the OTG Mouse-to-PC control method, you might need 2 different physical mouses, one connected to the PC so that the PC can show a cursor, and another that connected to your phone that can move this cursor. In the incoming updates I will hopefully fix this by adding a virtual mouse, so you can only use one mouse that is connected to your mobile phone.
- This software does not support most of the games. Because this software can move the mouse and simulate clicks at the operating system level (GUI automation). However, most games do not read these events the same way normal desktop applications do. Instead, they often use Raw Input / DirectInput / low-level drivers, which bypass standard OS-generated events. Because of this, The software input may be ignored, filtered, or treated as synthetic input by games, so it does not reliably control gameplay. 
- If 3 mobile phones are connected to the web-application and the single mouse controller feature is ON, only the device that joined first - has priority access - will be able to use the full web-application, others will have to wait until this device leaves the web-application, then, the priority will move to the device that joined right after this device, and so.
- When you leave the browser opened tap, the web-application will disconnect you automatically and you will have to restart the web page.
- The web-application is using a self-signed ssl-certification, which may make you encounter a warning in your web browser that says `Your connection is not private`, if this happens, just ignore it and press `Advanced -> Procced`.
- Do NOT modify anything in the program files to avoid unexpected errors.

- Developed by Ayman Saied -
- Please contact me [ clulyf88@gmail.com ] if you face any problem with the program, so I can fix it -


## Some information for developers on GitHub
- This project is written in `JAVA` 'for the server', `Python` 'for the program', `Javascript` 'for handling web-application interactions and sending data', `HTML` 'for main web-application interface', `CSS` 'for web-application user interface styling'.
- Libraries used in JAVA:

```java
import java.awt.AWTException;
import java.awt.MouseInfo;
import java.awt.Point;
import java.awt.Robot;
import java.awt.event.InputEvent;
import com.sun.net.httpserver.*;
import java.io.*;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import javax.net.ssl.*;
```

- Libraries used in Python:

```python
import socket
import time
from datetime import datetime
import requests
from requests.exceptions import RequestException
import threading
import subprocess
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import font
from tkinter.ttk import *
import urllib3
import os
import sys
import json
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
```

- To run the software run the NA-WirelessMouse64.py file or use this command `python NA-WirelessMouse64.py`.
- The source code of this software is converted into an exe program using pyinstaller.
- WebServer.jar file is the compiled version of WebServer.java and MouseMover.java.
- On every server startup, the software creates a new keystore.p12 file with a validation time of 10 years, that mean the https protocol will work unless you leave the server running for more than 10 years, then you will have to restart it :). 