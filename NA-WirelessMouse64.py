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

currentPath = os.getcwd().replace("\\", "/")
WebServerJavaFilePath = f"{currentPath}/Server/Java/WebServer.jar"
configurationJsonFilePath = f"{currentPath}/Server/Configuration.json"
LastVisitsLogPath = f"{currentPath}/Server/Info/LastVisitsLog.txt"
ServerOutputsPath = f"{currentPath}/Server/Info/ServerOutputs.txt"
ConnectedDevicesPath = f"{currentPath}/Server/Info/ConnectedDevices.txt"
ServerUptimePath = f"{currentPath}/Server/Info/Uptime.txt"
BlockedDevices = f"{currentPath}/Server/Info/BlockedDevices.txt"
p12FilePath = f"{currentPath}/Server/Java/keystore.p12"
p12Password = b"12345678"

isClosing = False
isServerOutputsOpened = False
isUsingOutputsWindow = False
openedItems = ""
openedItemsBlockedAndKickedDevices = ""
outputsSize = "Null"
serverUptime = "00:00:00"

def formatSize(sizeBytes):
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(sizeBytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


try:
    with open(ConnectedDevicesPath, "w", encoding="utf-8") as file:
        file.write("")
    file.close()
except Exception as e:
    print(e)

try:
    if not os.path.exists(LastVisitsLogPath):
        with open(LastVisitsLogPath, "w", encoding="utf-8") as file:
            file.write("")
        file.close()

    if not os.path.exists(ServerOutputsPath):
        with open(ServerOutputsPath, "w", encoding="utf-8") as file:
            file.write("")
        file.close()

    if not os.path.exists(ConnectedDevicesPath):
        with open(ConnectedDevicesPath, "w", encoding="utf-8") as file:
            file.write("")
        file.close()

    if not os.path.exists(ServerUptimePath):
        with open(ServerUptimePath, "w", encoding="utf-8") as file:
            file.write(serverUptime)
        file.close()

    if not os.path.exists(BlockedDevices):
        with open(BlockedDevices, "w", encoding="utf-8") as file:
            file.write("")
        file.close()

    if not os.path.exists(configurationJsonFilePath):
        with open(configurationJsonFilePath, "w", encoding="utf-8") as file:
            file.write('{\n"PORT": 3001,\n"Key": "admin",\n"SSLCertificateKeyStorePath": "",\n"WebApplicationPath": "",\n"ClearLogsEveryStartup": true,\n"SingleMouseController": true,\n"ServerOutputsSizeLimit": "30 MB"\n}')
        file.close()
except Exception as e:
    print(e)


def getLocalIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        return local_ip
    except Exception as e:
        print(e)
        return "IP not found!"


ip = getLocalIp()


def getServerStats():
    global serverStatusVar
    global serverStatusLbl
    global stopServerBtn
    global StartServerBtn
    global saveChangesBtn
    global serverPortEntry
    global serverPassEntry
    global sizeLimitEntry
    global singleMouseControllerBtn
    global stl
    global stLbl

    stl.set("Getting server status...")
    stLbl.config(fg="black")

    try:
        with open(configurationJsonFilePath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(f"https://{ip}:{data.get('PORT')}/health-check", verify=False)
        if response:
            serverStatusVar.set(f"  The server is online\n  The server is running at: https://{ip}:{data.get('PORT')}/\n  or https://localhost:{data.get('PORT')}/")
            serverStatusLbl.config(fg="green")

            stopServerBtn.config(state=NORMAL)
            StartServerBtn.config(state=DISABLED)
            saveChangesBtn.config(state=DISABLED)
            serverPortEntry.config(state=DISABLED)
            serverPassEntry.config(state=DISABLED)
            sizeLimitEntry.config(state=DISABLED)
            singleMouseControllerBtn.config(state=DISABLED)

        file.close()
    except RequestException:
        serverStatusVar.set("  The server is offline")
        serverStatusLbl.config(fg="red")

        stopServerBtn.config(state=DISABLED)
        StartServerBtn.config(state=NORMAL)
        saveChangesBtn.config(state=NORMAL)
        serverPortEntry.config(state=NORMAL)
        serverPassEntry.config(state=NORMAL)
        sizeLimitEntry.config(state=NORMAL)
        singleMouseControllerBtn.config(state=NORMAL)

    stl.set(" Server status fetched successfully")
    stLbl.config(fg="green")

    updateInputs()


def stopServer():
    global stopServerBtn
    global StartServerBtn
    global serverStatusVar
    global serverStatusLbl
    global saveChangesBtn
    global stl
    global serverPortEntry
    global serverPassEntry
    global sizeLimitEntry
    global singleMouseControllerBtn
    global stLbl

    stopServerBtn.config(state=DISABLED)
    stl.set("Closing the server...")
    stLbl.config(fg="black")

    try:
        with open(configurationJsonFilePath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(f"https://{ip}:{data.get('PORT')}/shutdownserver-{data.get('Key')}", verify=False)
        file.close()

        if response:
            threading.Thread(target=getServerStats).start()
        else:
            stopServerBtn.config(state=NORMAL)
            StartServerBtn.config(state=DISABLED)
            saveChangesBtn.config(state=DISABLED)
            serverPortEntry.config(state=DISABLED)
            serverPassEntry.config(state=DISABLED)
            sizeLimitEntry.config(state=DISABLED)
            singleMouseControllerBtn.config(state=DISABLED)
    except RequestException:
        stopServerBtn.config(state=NORMAL)
        StartServerBtn.config(state=DISABLED)
        saveChangesBtn.config(state=DISABLED)
        serverPortEntry.config(state=DISABLED)
        serverPassEntry.config(state=DISABLED)
        singleMouseControllerBtn.config(state=DISABLED)

    stl.set("The server has been closed successfully")
    stLbl.config(fg="green")


def stopServerThread():
    threading.Thread(target=stopServer).start()


def lightSignal(taregetCanvas, targetSignal, targetColor, targetTimeMs):
    taregetCanvas.itemconfig(targetSignal, fill=targetColor)
    time.sleep(targetTimeMs * 0.001)
    taregetCanvas.itemconfig(targetSignal, fill="gray")


def streamOutput(pipe):
    global root
    global isClosing

    global canvas
    global canvas2
    global canvas3

    global signalLight
    global signalLight2
    global signalLight3

    firstOutput = False

    for line in iter(pipe.readline, ''):
        if line.strip().startswith("Incoming request -> [RequestURI: "):
            requestMethod = line.strip().split("RequestMethod: ")[1].split("] [")[0]

            if requestMethod == "GET":
                threading.Thread(target=lambda: lightSignal(canvas, signalLight, "green", 200)).start()
            elif requestMethod == "POST":
                threading.Thread(target=lambda: lightSignal(canvas2, signalLight2, "green", 200)).start()
            else:
                threading.Thread(target=lambda: lightSignal(canvas3, signalLight3, "green", 200)).start()

        if not firstOutput:
            firstOutput = True
            threading.Thread(target=getServerStats).start()

        try:
            with open(ServerOutputsPath, "a", encoding="utf-8") as file:
                now = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                file.write(now + " " + line)
        except Exception as e:
            print(e)

        if line.strip() == "CloseServer" and isClosing:
            try:
                sys.exit()
            except SystemExit:
                os._exit(0)


def runStartServerCommand():
    global serverOutputsEntry
    global visitsLogScrolledText

    try:
        linesToRemain = ""
        with open(BlockedDevices, "r", encoding="utf-8") as file:
            for line in file:
                if not line.strip().endswith("+"):
                    linesToRemain += line
        file.close()

        with open(BlockedDevices, "w", encoding="utf-8") as fileToReWrite:
            fileToReWrite.write(linesToRemain)
        fileToReWrite.close()

        clearOrNot = True

        with open(configurationJsonFilePath, "r", encoding="utf-8") as configFile:
            data = json.load(configFile)
        configFile.close()

        if data.get("ClearLogsEveryStartup"):
            clearOrNot = data.get("ClearLogsEveryStartup")

        if clearOrNot:
            with open(ServerOutputsPath, "w", encoding="utf-8") as outputsFile:
                outputsFile.write("")
            outputsFile.close()

            with open(LastVisitsLogPath, "w", encoding="utf-8") as lastVisitsFile:
                lastVisitsFile.write("")
            lastVisitsFile.close()

            serverOutputsEntry.config(state=NORMAL)
            serverOutputsEntry.delete("1.0", "end")
            serverOutputsEntry.config(state=DISABLED)
            visitsLogScrolledText.config(state=NORMAL)
            visitsLogScrolledText.delete("1.0", "end")
            visitsLogScrolledText.config(state=DISABLED)

    except Exception as e:
        print(e)

    process = subprocess.Popen(["javaw", "-jar", WebServerJavaFilePath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    runCommandThread = threading.Thread(target=streamOutput, args=(process.stdout,))
    runCommandThread.daemon = True
    runCommandThread.start()

    return process


def isValidSizeText(text):
    units = ["B", "KB", "MB", "GB", "TB"]

    isValid = False
    for unit in units:
        if text.endswith(" " + unit):
            if text.replace(f" {unit}", "").isdigit():
                isValid = True

    if text.lower() == "off":
        isValid = True

    return isValid


def startServer():
    global StartServerBtn
    global stl
    global stLbl
    global serverPortEntry
    global serverPassEntry
    global sizeLimitEntry
    global singleMouseControllerBtn
    global saveChangesBtn

    stl.set("Starting the server...")
    stLbl.config(fg="black")

    StartServerBtn.config(state=DISABLED)
    saveChangesBtn.config(state=DISABLED)
    serverPortEntry.config(state=DISABLED)
    serverPassEntry.config(state=DISABLED)
    sizeLimitEntry.config(state=DISABLED)
    singleMouseControllerBtn.config(state=DISABLED)

    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NA-WirelessMouse64"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])

        now = datetime.now(timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=3650)) # Valid for 10 years!
            .sign(private_key, hashes.SHA256())
        )

        keystore_password = p12Password
        encryption_algorithm = serialization.BestAvailableEncryption(keystore_password)

        p12_data = pkcs12.serialize_key_and_certificates(
            name=b"my-alias",
            key=private_key,
            cert=certificate,
            cas=None,
            encryption_algorithm=encryption_algorithm
        )

        with open(p12FilePath, "wb") as f:
            f.write(p12_data)
        f.close()
    except Exception as e:
        print(e)

    try:
        with open(configurationJsonFilePath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        file.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            isPort = s.connect_ex(((ip), data.get('PORT'))) != 0
    except Exception as e:
        print(e)

    if isPort == True:
        if not os.path.exists(WebServerJavaFilePath):
            messagebox.showwarning("Missing file/folder error", "The WebServer.java file is missing, the program will be closed now!")
            root.destroy()
            try:
                sys.exit()
            except SystemExit:
                os._exit(0)

        runStartServerCommand()
    else:
        stl.set("Cannot use this port")
        stLbl.config(fg="red")
        messagebox.showwarning("Invalid inputs", f"Port {str(serverPortIntVar.get())} is already in use, please choose a different port number")
        StartServerBtn.config(state=NORMAL)


def startServerThread():
    threading.Thread(target=startServer).start()


def checkJAVA():
    nodeCommandResult = subprocess.run(['java', '--version'], shell=True, timeout=10)

    if nodeCommandResult.returncode != 0:
        messagebox.showwarning("Requirements error", "This program requires JAVA installed on your device in order to work properly")
        root.destroy()
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)


def updateInputs():
    global serverPortIntVar
    global serverPassVar
    global startClearEveryStartupCheckText
    global startClearEveryStartupCheck
    global singleMouseControllerCheckText
    global singleMouseControllerCheck
    global outputsSizeLimitEntered

    try:
        with open(configurationJsonFilePath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        serverPortIntVar.set(data.get("PORT"))
        serverPassVar.set(data.get("Key"))
        outputsSizeLimitEntered.set(data.get("ServerOutputsSizeLimit"))

        if data.get("ClearLogsEveryStartup"):
            startClearEveryStartupCheck.set(True)
            startClearEveryStartupCheckText.set("Yes")
        else:
            startClearEveryStartupCheck.set(False)
            startClearEveryStartupCheckText.set("No")

        if data.get("SingleMouseController"):
            singleMouseControllerCheck.set(True)
            singleMouseControllerCheckText.set("ON")
        else:
            singleMouseControllerCheck.set(False)
            singleMouseControllerCheckText.set("OFF")

        file.close()
    except Exception as e:
        print(e)


def upDatePaths():
    global serverPortIntVar
    global serverPassVar

    if os.path.exists(configurationJsonFilePath):
        try:
            with open(configurationJsonFilePath, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if not os.path.exists(data.get("SSLCertificateKeyStorePath")):
                data["SSLCertificateKeyStorePath"] = os.path.abspath("Server/Java/keystore.p12").replace("\\", "/")

            if not os.path.exists(data.get("WebApplicationPath")):
                if not os.path.exists("Server/Web-Application/"):
                    messagebox.showwarning("Missing file/folder error",
                                           "The Server/Web-Application folder is missing, the program will be ended now!")
                    root.destroy()
                    try:
                        sys.exit()
                    except SystemExit:
                        os._exit(0)

                data["WebApplicationPath"] = os.path.abspath("Server/Web-Application").replace("\\", "/") + "/"
        except Exception as e:
            print(e)

        try:
            if (data.get("Key")).replace(" ", "") == "":
                data["Key"] = "admin"
        except Exception:
            data["Key"] = "admin"

        try:
            int(str(data.get("PORT")))
            isPortNumeric = True
        except Exception:
            isPortNumeric = False

        if isPortNumeric == False:
            data["PORT"] = 3001

        try:
            if not data.get("ServerOutputsSizeLimit") or not isValidSizeText(data.get("ServerOutputsSizeLimit")):
                data["ServerOutputsSizeLimit"] = "30 MB"
        except:
            data["ServerOutputsSizeLimit"] = "30 MB"

        try:
            if data.get("ClearLogsEveryStartup") != True and data.get("ClearLogsEveryStartup") != False:
                data["ClearLogsEveryStartup"] = True
        except:
            data["ClearLogsEveryStartup"] = True

        try:
            if data.get("SingleMouseController") != True and data.get("SingleMouseController") != False:
                data["SingleMouseController"] = True
        except:
            data["SingleMouseController"] = True

        file.close()

        try:
            with open(configurationJsonFilePath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            file.close()
        except Exception as e:
            print(e)
    else:
        messagebox.showwarning("Missing file/folder error", "The Configuration.json file is missing, the program will be closed now!")
        root.destroy()
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)

    updateInputs()
    getServerStats()


def saveChanges():
    global serverPassVar
    global serverPortIntVar
    global saveChangesBtn
    global serverPortEntry
    global serverPassEntry
    global StartServerBtn
    global stopServerBtn
    global startClearEveryStartupCheck
    global singleMouseControllerCheck
    global outputsSizeLimitEntered
    global sizeLimitEntry
    global singleMouseControllerBtn
    global stl
    global stLbl

    stl.set("Saving changes...")
    stLbl.config(fg="black")

    saveChangesBtn.config(state=DISABLED)
    serverPortEntry.config(state=DISABLED)
    serverPassEntry.config(state=DISABLED)
    StartServerBtn.config(state=DISABLED)
    stopServerBtn.config(state=DISABLED)
    sizeLimitEntry.config(state=DISABLED)
    singleMouseControllerBtn.config(state=DISABLED)

    try:
        int(str(serverPortIntVar.get()))
        isPortNumeric = True
    except Exception:
        isPortNumeric = False

    if isPortNumeric == True:
        if int(serverPortIntVar.get()) >= 1 and int(serverPortIntVar.get()) <= 65535:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                isPort = s.connect_ex(((ip), int(serverPortIntVar.get()))) != 0

            if isPort == True:
                if serverPassVar.get().replace(" ", "") != "":
                    if isValidSizeText(outputsSizeLimitEntered.get()):
                        try:
                            with open(configurationJsonFilePath, 'r', encoding='utf-8') as file:
                                data = json.load(file)

                            data["Key"] = serverPassVar.get()
                            data["PORT"] = serverPortIntVar.get()
                            data["ClearLogsEveryStartup"] = startClearEveryStartupCheck.get()
                            data["ServerOutputsSizeLimit"] = outputsSizeLimitEntered.get()
                            data["SingleMouseController"] = singleMouseControllerCheck.get()

                            file.close()

                            with open(configurationJsonFilePath, "w", encoding="utf-8") as file:
                                json.dump(data, file, indent=4, ensure_ascii=False)

                            file.close()
                        except Exception as e:
                            print(e)

                        stl.set("Changes saved successfully")
                        stLbl.config(fg="green")

                        stopServerBtn.config(state=DISABLED)
                        StartServerBtn.config(state=NORMAL)
                        serverPortEntry.config(state=NORMAL)
                        serverPassEntry.config(state=NORMAL)
                        saveChangesBtn.config(state=NORMAL)
                        sizeLimitEntry.config(state=NORMAL)
                        singleMouseControllerBtn.config(state=NORMAL)
                    else:
                        stl.set("Cannot save changes")
                        stLbl.config(fg="red")
                        messagebox.showwarning("Invalid inputs", "Please enter a valid outputs size limit in B or KB or MB or GB or TB, or enter OFF to make it limitless, Example 1: 10 MB, Example 2: OFF")
                        stopServerBtn.config(state=DISABLED)
                        StartServerBtn.config(state=NORMAL)
                        serverPortEntry.config(state=NORMAL)
                        serverPassEntry.config(state=NORMAL)
                        saveChangesBtn.config(state=NORMAL)
                        sizeLimitEntry.config(state=NORMAL)
                        singleMouseControllerBtn.config(state=NORMAL)
                else:
                    stl.set("Cannot save changes")
                    stLbl.config(fg="red")
                    messagebox.showwarning("Invalid inputs", "Please enter a valid server access key")
                    stopServerBtn.config(state=DISABLED)
                    StartServerBtn.config(state=NORMAL)
                    serverPortEntry.config(state=NORMAL)
                    serverPassEntry.config(state=NORMAL)
                    saveChangesBtn.config(state=NORMAL)
                    sizeLimitEntry.config(state=NORMAL)
                    singleMouseControllerBtn.config(state=NORMAL)
            else:
                stl.set("Cannot save changes")
                stLbl.config(fg="red")
                messagebox.showwarning("Invalid inputs", f"Port {str(serverPortIntVar.get())} is already in use, please choose a different port number")
                stopServerBtn.config(state=DISABLED)
                StartServerBtn.config(state=NORMAL)
                serverPortEntry.config(state=NORMAL)
                serverPassEntry.config(state=NORMAL)
                saveChangesBtn.config(state=NORMAL)
                sizeLimitEntry.config(state=NORMAL)
                singleMouseControllerBtn.config(state=NORMAL)
        else:
            stl.set("Cannot save changes")
            stLbl.config(fg="red")
            messagebox.showwarning("Invalid inputs", "Please enter a port value between 1 and 65535")
            stopServerBtn.config(state=DISABLED)
            StartServerBtn.config(state=NORMAL)
            serverPortEntry.config(state=NORMAL)
            serverPassEntry.config(state=NORMAL)
            saveChangesBtn.config(state=NORMAL)
            sizeLimitEntry.config(state=NORMAL)
            singleMouseControllerBtn.config(state=NORMAL)
    else:
        stl.set("Cannot save changes")
        stLbl.config(fg="red")
        messagebox.showwarning("Invalid inputs", "Please enter a valid port value")
        stopServerBtn.config(state=DISABLED)
        StartServerBtn.config(state=NORMAL)
        serverPortEntry.config(state=NORMAL)
        serverPassEntry.config(state=NORMAL)
        saveChangesBtn.config(state=NORMAL)
        sizeLimitEntry.config(state=NORMAL)
        singleMouseControllerBtn.config(state=NORMAL)


def saveChangesThread():
    threading.Thread(target=saveChanges).start()


def updateTextStartClearEveryStartupCheck():
    global startClearEveryStartupCheckText

    if startClearEveryStartupCheckText.get() == "No":
        startClearEveryStartupCheckText.set("Yes")
    else:
        startClearEveryStartupCheckText.set("No")


def updateSingleMouseControllerCheck():
    global singleMouseControllerCheckText

    if singleMouseControllerCheckText.get() == "OFF":
        singleMouseControllerCheckText.set("ON")
    else:
        singleMouseControllerCheckText.set("OFF")


def kickDevice(info, window, item):
    global connectedDevicesTable

    deviceIPFromInfo = info[0]
    deviceDetailsFromInfo = info[1]
    deviceConnectionDateFromInfo = info[2]

    targetLine = f"[{deviceConnectionDateFromInfo}] [{deviceIPFromInfo} | {deviceDetailsFromInfo}]+"

    isItThere = False
    lineToDelete = "None"

    try:
        with open(BlockedDevices, "r", encoding="utf-8") as fileToRead:
            for line in fileToRead:
                if line.strip().split("] ")[1] == targetLine.split("] ")[1]:
                    isItThere = True
                elif line.strip().split("] ")[1] == (targetLine.replace("]+", "") + "]").split("] ")[1]:
                    lineToDelete = line.strip()
                    break
        fileToRead.close()

        if lineToDelete != "None":
            linesToWrite = ""
            with open(BlockedDevices, "r", encoding="utf-8") as fileToRead2:
                for line in fileToRead2:
                    if line.strip() != lineToDelete:
                        linesToWrite += line
            fileToRead2.close()

            with open(BlockedDevices, "w", encoding="utf-8") as fileToReWrite:
                fileToReWrite.write(linesToWrite)
            fileToReWrite.close()

        if lineToDelete != "None":
            now = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            targetLine = f"[{now}] [{deviceIPFromInfo} | {deviceDetailsFromInfo}]+"

        if not isItThere:
            with open(BlockedDevices, "a", encoding="utf-8") as file:
                file.write(targetLine + "\n")
            file.close()

        linesToWrite2 = ""
        with open(ConnectedDevicesPath, "r", encoding="utf-8") as fileToRead3:
            for line in fileToRead3:
                line = line.replace("]*", "]")
                if not line.strip().split(" - ")[0].split("] ")[1] == ((targetLine.replace("]+", "") + "]").split("] ")[1]):
                    linesToWrite2 += line.strip() + "\n"
        fileToRead3.close()

        with open(ConnectedDevicesPath, "w", encoding="utf-8") as fileToReWrite2:
            fileToReWrite2.write(linesToWrite2)
        fileToReWrite2.close()

        connectedDevicesTable.delete(item)
        window.destroy()

    except Exception as e:
        print(e)

def getSizeOnlyInBytes(text):
    units = ["B", "KB", "MB", "GB", "TB"]

    isValid = False
    choseUnit = "Null"
    sizeNumber = 0

    for unit in units:
        if text.endswith(" " + unit):
            if text.replace(f" {unit}", "").isdigit():
                isValid = True
                choseUnit = unit
                sizeNumber = int(text.replace(f" {unit}", ""))

    if isValid:
        if choseUnit == units[0]:
            return sizeNumber
        elif choseUnit == units[1]:
            return sizeNumber * 1024
        elif choseUnit == units[2]:
            return sizeNumber * 1024 * 1024
        elif choseUnit == units[3]:
            return sizeNumber * 1024 * 1024 * 1024
        elif choseUnit == units[4]:
            return sizeNumber * 1024 * 1024 * 1024 * 1024
        else:
            return False
    else:
        if text.lower() == "off":
            return "OFF"

        return False


def blockDevice(info, window, item):
    global connectedDevicesTable

    deviceIPFromInfo = info[0]
    deviceDetailsFromInfo = info[1]
    deviceConnectionDateFromInfo = info[2]

    targetLine = f"[{deviceConnectionDateFromInfo}] [{deviceIPFromInfo} | {deviceDetailsFromInfo}]"
    isItThere = False
    lineToDelete = "None"

    try:
        with open(BlockedDevices, "r", encoding="utf-8") as fileToRead:
            for line in fileToRead:
                if line.strip().split("] ")[1] == targetLine.split("] ")[1]:
                    isItThere = True
                elif line.strip().split("] ")[1] == (targetLine + "+").split("] ")[1]:
                    lineToDelete = line.strip()
                    break
        fileToRead.close()

        if lineToDelete != "None":
            linesToWrite = ""
            with open(BlockedDevices, "r", encoding="utf-8") as fileToRead2:
                for line in fileToRead2:
                    if line.strip() != lineToDelete:
                        linesToWrite += line
            fileToRead2.close()

            with open(BlockedDevices, "w", encoding="utf-8") as fileToReWrite:
                fileToReWrite.write(linesToWrite)
            fileToReWrite.close()

        if lineToDelete != "None":
            now = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            targetLine = f"[{now}] [{deviceIPFromInfo} | {deviceDetailsFromInfo}]"

        if not isItThere:
            with open(BlockedDevices, "a", encoding="utf-8") as file:
                file.write(targetLine + "\n")
            file.close()

        linesToWrite2 = ""
        with open(ConnectedDevicesPath, "r", encoding="utf-8") as fileToRead3:
            for line in fileToRead3:
                line = line.replace("]*", "]")
                if not line.strip().split(" - ")[0].split("] ")[1] == targetLine.split("] ")[1]:
                    linesToWrite2 += line.strip() + "\n"
        fileToRead3.close()

        with open(ConnectedDevicesPath, "w", encoding="utf-8") as fileToReWrite2:
            fileToReWrite2.write(linesToWrite2)
        fileToReWrite2.close()

        connectedDevicesTable.delete(item)
        window.destroy()
    except Exception as e:
        print(e)

def onlyNumbers(P):
    return P.isdigit() or P.replace(" ", "") == "" or P == ""


def onCloseItemWindow(item, connectedDevicesTablePopup):
    global openedItems

    print(f"Closing item({item}) window...")

    openedItems = openedItems.replace(f"{item}-", "")
    connectedDevicesTablePopup.destroy()

def onCloseItemBlockedAndKickedDevicesWindow(item, blockedAndKickedDevicesTablePopup):
    global openedItemsBlockedAndKickedDevices

    print(f"Closing item({item}) blocked and kicked devices window...")

    openedItemsBlockedAndKickedDevices = openedItemsBlockedAndKickedDevices.replace(f"{item}-", "")
    blockedAndKickedDevicesTablePopup.destroy()

def onSelectColumnInConnectedDevicesTable(event):
    global connectedDevicesTable
    global customFont1
    global openedItems

    item = connectedDevicesTable.selection()

    if item:
        isItOpened = False
        for item3 in openedItems.split("-"):
            if item[0] == item3:
                isItOpened = True
            else:
                openedItems += (item[0] + "-")

        if not isItOpened:
            item = item[0]

            hasPriority = ""

            if connectedDevicesTable.item(item, "tags"):
                hasPriority = "- Has priority"

            values = connectedDevicesTable.item(item)["values"]

            deviceIpFromValues = values[0]
            deviceDetailsFromValues = values[1]
            deviceConnectionDateFromValues = values[2]

            connectedDevicesTablePopup = Toplevel(root)
            connectedDevicesTablePopup.maxsize(width=400, height=165)
            connectedDevicesTablePopup.minsize(width=400, height=165)
            connectedDevicesTablePopup.title("NA-WirelessMouse64 | Connected device information")
            if os.path.exists("Icon.ico"):
                connectedDevicesTablePopup.iconbitmap("Icon.ico")

            lable1 = tkinter.Label(connectedDevicesTablePopup, font=customFont1, justify="left", text=f"Connected device {hasPriority}")
            lable1.config(fg="green")
            lable1.grid(row=0, column=0, sticky=W, padx=5)

            lable2 = tkinter.Label(connectedDevicesTablePopup, font=customFont1, justify="left", text=f"Device IP: {deviceIpFromValues}")
            lable2.grid(row=1, column=0, sticky=W, padx=5)

            lable3 = tkinter.Label(connectedDevicesTablePopup, font=customFont1, justify="left", wraplength=400, text=f"User agent: {deviceDetailsFromValues}")
            lable3.grid(row=2, column=0, sticky=W, padx=5)

            lable4 = tkinter.Label(connectedDevicesTablePopup, font=customFont1, justify="left", text=f"Connection date: {deviceConnectionDateFromValues}")
            lable4.grid(row=3, column=0, sticky=W, padx=5)

            btn1 = Button(connectedDevicesTablePopup, text="Block", width=15, command=lambda: blockDevice(values, connectedDevicesTablePopup, item))
            btn1.grid(row=4, column=0, sticky=W, padx=95)

            btn2 = Button(connectedDevicesTablePopup, text="Kick", width=15, command=lambda: kickDevice(values, connectedDevicesTablePopup, item))
            btn2.grid(row=4, column=0, sticky=W, padx=205)

            connectedDevicesTablePopup.protocol("WM_DELETE_WINDOW", lambda: onCloseItemWindow(item, connectedDevicesTablePopup))


def updateConnectedDevices():
    global connectedDevicesTable
    global isClosing
    global singleMouseControllerCheck

    while True:
        if isClosing:
            break

        try:
            with open(ConnectedDevicesPath, "r", encoding="utf-8") as file:
                for line in file:
                    lineBeforeEditing = line
                    line = line.replace("]*", "]")

                    deviceIp = line.strip().split("] ")[1].split(" - ")[0].split(" | ")[0].replace("[", "")
                    deviceDetails = line.strip().split("] ")[1].split(" - ")[0].split(" | ")[1]
                    connectionDate = line.strip().split("] ")[0].replace("[", "")

                    isItRecorded = False
                    for item in connectedDevicesTable.get_children():
                        row = connectedDevicesTable.item(item)["values"]
                        if row[0] == deviceIp and row[1] == deviceDetails and row[2] == connectionDate:
                            isItRecorded = True

                    if not isItRecorded:
                        isBlockedOrKicked = False
                        targetLine = f"[{deviceIp} | {deviceDetails}]"
                        with open(BlockedDevices, "r", encoding="utf-8") as blockedDevicesFileToRead:
                            for line in blockedDevicesFileToRead:
                                if line.strip().split("] ")[1] == targetLine or line.strip().split("] ")[1] == (
                                        targetLine + "+"):
                                    isBlockedOrKicked = True
                        blockedDevicesFileToRead.close()

                        if not isBlockedOrKicked:
                            if lineBeforeEditing.__contains__("]*"):
                                if singleMouseControllerCheck:
                                    connectedDevicesTable.insert("", "end", values=(deviceIp, deviceDetails, connectionDate), tags=("greenRow",))
                            else:
                                connectedDevicesTable.insert("", "end", values=(deviceIp, deviceDetails, connectionDate))

            file.close()

            itemsToRemain = ""
            for item in connectedDevicesTable.get_children():
                row = connectedDevicesTable.item(item)["values"]

                with open(ConnectedDevicesPath, "r", encoding="utf") as fileToRead:
                    for line in fileToRead:
                        line = line.replace("]*", "]")
                        deviceIp = line.strip().split("] ")[1].split(" - ")[0].split(" | ")[0].replace("[", "")
                        deviceDetails = line.strip().split("] ")[1].split(" - ")[0].split(" | ")[1]
                        connectionDate = line.strip().split("] ")[0].replace("[", "")

                        if row[0] == deviceIp and row[1] == deviceDetails and row[2] == connectionDate:
                            itemsToRemain += item + "-"
                fileToRead.close()

            itemsToDelete = list(set(itemsToRemain.split("-")) ^ set(connectedDevicesTable.get_children()))

            for item in itemsToDelete:
                for item2 in connectedDevicesTable.get_children():
                    if item2 == item:
                        connectedDevicesTable.delete(item2)

            if singleMouseControllerCheck:
                with open(ConnectedDevicesPath, "r", encoding="utf") as fileToRead2:
                    for line in fileToRead2:
                        if line.__contains__("]*"):
                            line = line.replace("]*", "]")

                            deviceIp = line.strip().split("] ")[1].split(" - ")[0].split(" | ")[0].replace("[", "")
                            deviceDetails = line.strip().split("] ")[1].split(" - ")[0].split(" | ")[1]
                            connectionDate = line.strip().split("] ")[0].replace("[", "")

                            for item3 in connectedDevicesTable.get_children():
                                row = connectedDevicesTable.item(item3)["values"]
                                if row[0] == deviceIp and row[1] == deviceDetails and row[2] == connectionDate:
                                    connectedDevicesTable.item(item3, tags=("greenRow",))
                                    break
                            break

            fileToRead2.close()
        except Exception as e:
            print(e)

        time.sleep(0.5)


def updateBlockedOrKickedDevices():
    global blockedAndKickedDevicesTable
    global isClosing

    while True:
        if isClosing:
            break

        try:
            with open(BlockedDevices, "r", encoding="utf-8") as file:
                for line in file:
                    deviceIp = line.strip().split("] [")[1].split(" | ")[0]
                    deviceDetails = line.strip().split("] [")[1].split(" | ")[1].split("]")[0]
                    BlockingOrKickingDate = line.strip().split("] ")[0].replace("[", "")
                    statu = "Blocked"
                    if (line.strip().endswith("+")):
                        statu = "Kicked"

                    isItRecorded = False
                    for item in blockedAndKickedDevicesTable.get_children():
                        row = blockedAndKickedDevicesTable.item(item)["values"]
                        if row[0] == deviceIp and row[1] == deviceDetails and row[3] == BlockingOrKickingDate:
                            isItRecorded = True

                    if not isItRecorded:
                        blockedAndKickedDevicesTable.insert("", "end", values=(
                        deviceIp, deviceDetails, statu, BlockingOrKickingDate))

            file.close()

            itemsToRemain = ""
            for item in blockedAndKickedDevicesTable.get_children():
                row = blockedAndKickedDevicesTable.item(item)["values"]

                with open(BlockedDevices, "r", encoding="utf") as fileToRead:
                    for line in fileToRead:
                        deviceIp = line.strip().split("] [")[1].split(" | ")[0]
                        deviceDetails = line.strip().split("] [")[1].split(" | ")[1].split("]")[0]
                        BlockingOrKickingDate = line.strip().split("] ")[0].replace("[", "")

                        if row[0] == deviceIp and row[1] == deviceDetails and row[3] == BlockingOrKickingDate:
                            itemsToRemain += item + "-"
                fileToRead.close()

            itemsToDelete = list(set(itemsToRemain.split("-")) ^ set(blockedAndKickedDevicesTable.get_children()))

            for item in itemsToDelete:
                for item2 in blockedAndKickedDevicesTable.get_children():
                    if item2 == item:
                        blockedAndKickedDevicesTable.delete(item2)
        except Exception as e:
            print(e)

        time.sleep(0.5)


def unBlockDevice(info, window, item):
    global blockedAndKickedDevicesTable

    deviceIpFromValues = info[0]
    deviceDetailsFromValues = info[1]
    blockedOrKicked = info[2]
    deviceBlockingOrKickingDateFromValues = info[3]

    targetLine = f"[{deviceBlockingOrKickingDateFromValues}] [{deviceIpFromValues} | {deviceDetailsFromValues}]{blockedOrKicked.replace('Blocked', '').replace('Kicked', '+')}"
    linesToStay = ""

    try:
        with open(BlockedDevices, "r", encoding="utf-8") as fileToRead:
            for line in fileToRead:
                if (line.strip() != targetLine):
                    linesToStay += line
        fileToRead.close()

        with open(BlockedDevices, "w", encoding="utf-8") as fileToReWrite:
            fileToReWrite.write(linesToStay)
        fileToReWrite.close()

        blockedAndKickedDevicesTable.delete(item)
        window.destroy()
    except Exception as e:
        print(e)


def onSelectColumnInBLockedAndKickedDevicesTable(event):
    global blockedAndKickedDevicesTable
    global customFont1
    global openedItemsBlockedAndKickedDevices

    item = blockedAndKickedDevicesTable.selection()

    if item:
        isItOpened = False
        for item3 in openedItemsBlockedAndKickedDevices.split("-"):
            if item[0] == item3:
                isItOpened = True
            else:
                openedItemsBlockedAndKickedDevices += (item[0] + "-")

        if not isItOpened:
            item = item[0]
            values = blockedAndKickedDevicesTable.item(item)["values"]

            deviceIpFromValues = values[0]
            deviceDetailsFromValues = values[1]
            blockedOrKicked = values[2]
            deviceBlockingOrKickingDateFromValues = values[3]

            blockedAndKickedDevicesTablePopup = Toplevel(root)
            blockedAndKickedDevicesTablePopup.maxsize(width=400, height=165)
            blockedAndKickedDevicesTablePopup.minsize(width=400, height=165)
            blockedAndKickedDevicesTablePopup.title(f"NA-WirelessMouse64 | {blockedOrKicked} device information")
            if os.path.exists("Icon.ico"):
                blockedAndKickedDevicesTablePopup.iconbitmap("Icon.ico")

            lable1 = tkinter.Label(blockedAndKickedDevicesTablePopup, font=customFont1, justify="left", text=f"{blockedOrKicked} device")
            lable1.config(fg="red")
            lable1.grid(row=0, column=0, sticky=W, padx=5)

            lable2 = tkinter.Label(blockedAndKickedDevicesTablePopup, font=customFont1, justify="left", text=f"Device IP: {deviceIpFromValues}")
            lable2.grid(row=1, column=0, sticky=W, padx=5)

            lable3 = tkinter.Label(blockedAndKickedDevicesTablePopup, font=customFont1, justify="left", wraplength=400, text=f"User agent: {deviceDetailsFromValues}")
            lable3.grid(row=2, column=0, sticky=W, padx=5)

            lable4 = tkinter.Label(blockedAndKickedDevicesTablePopup, font=customFont1, justify="left", text=f"{blockedOrKicked.replace('ed', 'ing')} date: {deviceBlockingOrKickingDateFromValues}")
            lable4.grid(row=3, column=0, sticky=W, padx=5)

            if blockedOrKicked == "Blocked":
                btn1 = Button(blockedAndKickedDevicesTablePopup, text="Unblock", width=20, command=lambda: unBlockDevice(values, blockedAndKickedDevicesTablePopup, item))
                btn1.grid(row=4, column=0, sticky=W, padx=130)
            elif blockedOrKicked == "Kicked":
                btn1 = Button(blockedAndKickedDevicesTablePopup, text="Restore access", width=20, command=lambda: unBlockDevice(values, blockedAndKickedDevicesTablePopup, item))
                btn1.grid(row=4, column=0, sticky=W, padx=130)

            blockedAndKickedDevicesTablePopup.protocol("WM_DELETE_WINDOW", lambda: onCloseItemBlockedAndKickedDevicesWindow(item, blockedAndKickedDevicesTablePopup))


def updateVisitsLog():
    global visitsLogScrolledText
    global isClosing

    while True:
        if isClosing:
            break

        try:
            linesToInsert = ""
            with open(LastVisitsLogPath, "r", encoding="utf-8") as fileToRead:
                for line in fileToRead:
                    linesToInsert += line.strip() + "\n"
            fileToRead.close()

            if linesToInsert.strip() != visitsLogScrolledText.get("1.0", "end").strip():
                atBottom = visitsLogScrolledText.yview()[1] == 1.0

                newLines = linesToInsert[len(visitsLogScrolledText.get("1.0", "end")):]
                visitsLogScrolledText.config(state=NORMAL)
                visitsLogScrolledText.insert("end", newLines)
                if atBottom:
                    visitsLogScrolledText.yview_moveto(1.0)
                visitsLogScrolledText.config(state=DISABLED)

            if linesToInsert.strip() == "":
                visitsLogScrolledText.config(state=NORMAL)
                visitsLogScrolledText.delete("1.0", "end")
                visitsLogScrolledText.config(state=DISABLED)
                visitsLogScrolledText.yview_moveto(1.0)
        except Exception as e:
            print(e)

        time.sleep(0.5)


def onClose():
    global isClosing
    global serverStatusVar

    print("Closing...")
    isClosing = True

    if serverStatusVar.get().startswith("  The server is online"):
        stopServer()
        root.destroy()
    else:
        root.destroy()
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)


def closeServerOutputs(window):
    global isServerOutputsOpened
    global serverOutputsBtn
    global isUsingOutputsWindow

    isServerOutputsOpened = False
    try:
        serverOutputsBtn.config(state=NORMAL)
        isUsingOutputsWindow = False
    except Exception:
        pass


def updateOutputsSize():
    global isClosing
    global otherInfoLabelText
    global outputsSize
    global serverUptime
    global serverOutputsEntry
    global visitsLogScrolledText

    while True:
        if isClosing:
            break

        try:
            with open(configurationJsonFilePath, "r", encoding="utf-8") as file:
                data = json.load(file)
            file.close()

            sumSizeOfOutputs = os.path.getsize(LastVisitsLogPath) + os.path.getsize(ServerOutputsPath)
            outputsSize = formatSize(sumSizeOfOutputs)
            otherInfoLabelText.config(text=f"  Uptime: {serverUptime}\n  Outputs size: {outputsSize}\n  Logs size limit:\n  Single mouse controller")

            if getSizeOnlyInBytes(data.get("ServerOutputsSizeLimit")) != "OFF":
                if sumSizeOfOutputs > getSizeOnlyInBytes(data.get("ServerOutputsSizeLimit")):
                    print("Logs size limit is hit, clearing outputs...")

                    with open(LastVisitsLogPath, "w", encoding="utf-8") as LastVisitsFileToReWrite:
                        LastVisitsFileToReWrite.write("")
                    LastVisitsFileToReWrite.close()

                    with open(ServerOutputsPath, "w", encoding="utf-8") as ServerOutputsFileToReWrite:
                        ServerOutputsFileToReWrite.write("")
                    ServerOutputsFileToReWrite.close()

                    serverOutputsEntry.config(state=NORMAL)
                    serverOutputsEntry.delete("1.0", "end")
                    serverOutputsEntry.config(state=DISABLED)
                    visitsLogScrolledText.config(state=NORMAL)
                    visitsLogScrolledText.delete("1.0", "end")
                    visitsLogScrolledText.config(state=DISABLED)
        except Exception as e:
            print(e)

        time.sleep(0.5)


def updateServerUptime():
    global isClosing
    global otherInfoLabelText
    global outputsSize
    global serverUptime

    while True:
        if isClosing:
            break

        try:
            with open(ServerUptimePath, "r", encoding="utf-8") as uptimeFile:
                serverUptime = uptimeFile.read().strip()
                otherInfoLabelText.config(text=f"  Uptime: {serverUptime}\n  Outputs size: {outputsSize}\n  Logs size limit:\n  Single mouse controller")
            uptimeFile.close()
        except Exception as e:
            print(e)

        time.sleep(0.5)


def updateServerOutputsText():
    global serverOutputsEntry
    global isServerOutputsOpened
    global isClosing

    while True:
        if isClosing:
            break

        if isUsingOutputsWindow:
            try:
                linesToInsert = ""
                with open(ServerOutputsPath, "r", encoding="utf-8") as fileToRead:
                    for line in fileToRead:
                        linesToInsert += line.strip() + "\n"
                fileToRead.close()

                if linesToInsert.strip() != serverOutputsEntry.get("1.0", "end").strip():
                    atBottom = serverOutputsEntry.yview()[1] == 1.0

                    newLines = linesToInsert[len(serverOutputsEntry.get("1.0", "end")):]
                    serverOutputsEntry.config(state=NORMAL)
                    serverOutputsEntry.insert("end", newLines)
                    if atBottom:
                        serverOutputsEntry.yview_moveto(1.0)
                    serverOutputsEntry.config(state=DISABLED)

                if linesToInsert.strip() == "":
                    serverOutputsEntry.config(state=NORMAL)
                    serverOutputsEntry.delete("1.0", "end")
                    serverOutputsEntry.config(state=DISABLED)
                    serverOutputsEntry.yview_moveto(1.0)
            except Exception as e:
                print(e)

        time.sleep(0.5)


def openServerOutputs():
    global isServerOutputsOpened
    global serverOutputsBtn
    global serverOutputsEntry
    global isUsingOutputsWindow

    isServerOutputsOpened = True
    serverOutputsBtn.config(state=DISABLED)
    isUsingOutputsWindow = True

    serverOutputsRoot = Toplevel(root)
    serverOutputsRoot.title("NA-WirelessMouse64 | Server outputs")

    serverOutputsRoot.geometry("700x350")
    serverOutputsRoot.minsize(580, 250)
    if os.path.exists("Icon.ico"):
        serverOutputsRoot.iconbitmap("Icon.ico")

    serverOutputsEntry = ScrolledText(serverOutputsRoot)
    serverOutputsEntry.pack(expand=True, fill='both')

    threading.Thread(target=updateServerOutputsText).start()

    serverOutputsRoot.bind("<Destroy>", closeServerOutputs)


root = Tk()

serverStatusVar = StringVar()
stl = StringVar()
serverPassVar = StringVar()
startClearEveryStartupCheck = BooleanVar()
singleMouseControllerCheck = BooleanVar()
startClearEveryStartupCheckText = StringVar()
startClearEveryStartupCheckText.set("Yes")
singleMouseControllerCheckText = StringVar()
singleMouseControllerCheckText.set("ON")
serverPortIntVar = IntVar()
outputsSizeLimitEntered = StringVar()
serverStatusVar.set("  Getting server status...\n  ")

root.title("NA-WirelessMouse64")
root.maxsize(width=440, height=730)
root.minsize(width=440, height=730)
if os.path.exists("Icon.ico"):
    root.iconbitmap("Icon.ico")

customFont1 = font.Font(
    family="Arial",
    size=11,
    weight="bold",
    slant="roman",
    underline=False,
    overstrike=False
)

customFont2 = font.Font(
    family="Arial",
    size=10,
    weight="bold",
    slant="roman",
    underline=False,
    overstrike=False
)

customFont3 = font.Font(
    family="Arial",
    size=8,
    weight="bold",
    slant="roman",
    underline=False,
    overstrike=False
)

vcmd = (root.register(onlyNumbers), "%P")

serverStatusLbl = tkinter.Label(root, textvariable=serverStatusVar, font=customFont1, justify="left", anchor="w")
serverStatusLbl.grid(row=0, column=0, sticky=W, pady=4)

serverPortLbl = tkinter.Label(root, text="  Server port", font=customFont1, justify="left", anchor="w")
serverPortLbl.grid(row=1, column=0, sticky=W, pady=4)

serverPortEntry = Entry(root, width=5, font=customFont1, justify="left", textvariable=serverPortIntVar, validate="key", validatecommand=vcmd)
serverPortEntry.grid(row=1, column=0, sticky=W, pady=4, padx=100)

serverPass = tkinter.Label(root, text=" |  Server access key", font=customFont1, justify="left", anchor="w")
serverPass.grid(row=1, column=0, sticky=W, pady=4, padx=150)

serverPassEntry = Entry(root, width=14, font=customFont1, justify="left", textvariable=serverPassVar)
serverPassEntry.grid(row=1, column=0, sticky=W, pady=4, padx=310)

clearEveryStartup = tkinter.Label(root, text="  Clear logs on server startup", font=customFont1, justify="left", anchor="w")
clearEveryStartup.grid(row=3, column=0, sticky=W, pady=4)

clearEveryStartupBtn = Checkbutton(root, width=5, variable=startClearEveryStartupCheck, textvariable=startClearEveryStartupCheckText, command=updateTextStartClearEveryStartupCheck)
clearEveryStartupBtn.grid(row=3, column=0, sticky=W, pady=4, padx=230)

stopServerBtn = Button(root, text="Stop server", width=15, command=stopServerThread)
stopServerBtn.grid(row=4, column=0, sticky=W, pady=4, padx=140)
stopServerBtn.config(state=DISABLED)

saveChangesBtn = Button(root, text="Save changes", width=15, command=saveChangesThread)
saveChangesBtn.grid(row=4, column=0, sticky=W, pady=4, padx=329)
saveChangesBtn.config(state=DISABLED)
serverPortEntry.config(state=DISABLED)

StartServerBtn = Button(root, text="Start server", width=15, command=startServerThread)
StartServerBtn.grid(row=4, column=0, sticky=W, pady=4, padx=20)
StartServerBtn.config(state=DISABLED)
serverPassEntry.config(state=DISABLED)

connectedDevicesTableTextFirstLabel = tkinter.Label(root, text="  Connected devices", font=customFont1, justify="left", anchor="w")
connectedDevicesTableTextFirstLabel.grid(row=5, column=0, sticky=W, pady=4)

connectedDevicesTable = ttk.Treeview(root, height=4)
connectedDevicesTable["columns"] = ("IP", "User agent", "Connection date")
connectedDevicesTable["show"] = "headings"

connectedDevicesTable.tag_configure("greenRow", background="#9AEC97")

connectedDevicesTable.heading("IP", text="IP")
connectedDevicesTable.heading("User agent", text="User agent")
connectedDevicesTable.heading("Connection date", text="Connection date")

connectedDevicesTable.column("IP", width=87, anchor="center")
connectedDevicesTable.column("User agent", width=195, anchor="center")
connectedDevicesTable.column("Connection date", width=132, anchor="center")

connectedDevicesTable.bind("<<TreeviewSelect>>", onSelectColumnInConnectedDevicesTable)
connectedDevicesTable.grid(row=6, column=0, padx=(0,317))

blockedAndKickedDevicesTableFirstTextLabel = tkinter.Label(root, text="  Blocked & Kicked devices", font=customFont1, justify="left", anchor="w")
blockedAndKickedDevicesTableFirstTextLabel.grid(row=7, column=0, sticky=W, pady=4)

blockedAndKickedDevicesTable = ttk.Treeview(root, height=4)
blockedAndKickedDevicesTable["columns"] = ("IP", "User agent", "Status","Blocking or Kicking date")
blockedAndKickedDevicesTable["show"] = "headings"

blockedAndKickedDevicesTable.heading("IP", text="IP")
blockedAndKickedDevicesTable.heading("User agent", text="User agent")
blockedAndKickedDevicesTable.heading("Status", text="Status")
blockedAndKickedDevicesTable.heading("Blocking or Kicking date", text="Blocking or Kicking date")

blockedAndKickedDevicesTable.column("IP", width=87, anchor="center")
blockedAndKickedDevicesTable.column("User agent", width=115, anchor="center")
blockedAndKickedDevicesTable.column("Status", width=55, anchor="center")
blockedAndKickedDevicesTable.column("Blocking or Kicking date", width=152, anchor="center")

blockedAndKickedDevicesTable.bind("<<TreeviewSelect>>", onSelectColumnInBLockedAndKickedDevicesTable)
blockedAndKickedDevicesTable.grid(row=8, column=0, padx=(0,317))

visitsLogLabelText = tkinter.Label(root, text="  Visits log", font=customFont1, justify="left", anchor="w")
visitsLogLabelText.grid(row=9, column=0, sticky=W, pady=4)

visitsLogScrolledText = ScrolledText(root, width=50, height=5, spacing1=3, spacing2=3, spacing3=3)
visitsLogScrolledText.grid(row=10, column=0, padx=(0,306))
visitsLogScrolledText.yview_moveto(1.0)
visitsLogScrolledText.config(state=DISABLED)

othersLabelText = tkinter.Label(root, text="  Requests signals & Other", font=customFont1, justify="left", anchor="w")
othersLabelText.grid(row=11, column=0, sticky=W, pady=4)

inComingRequestsLabelText = tkinter.Label(root, font=customFont2, justify="left", text="  Incoming requests\n\n  Method:   GET\n  Method: POST\n  Method: Other")
inComingRequestsLabelText.grid(row=12, column=0, sticky=W, pady=(0, 250))

canvas = tkinter.Canvas(root, width=15, height=15, highlightthickness=0)
canvas.grid(row=12, padx=110, pady=(0, 246), sticky=W)

canvas2 = tkinter.Canvas(root, width=15, height=15, highlightthickness=0)
canvas2.grid(row=12, padx=110, pady=(0, 216), sticky=W)

canvas3 = tkinter.Canvas(root, width=15, height=15, highlightthickness=0)
canvas3.grid(row=12, padx=110, pady=(0, 186), sticky=W)

signalLight = canvas.create_oval(0, 0, 12, 12, fill="gray", outline="#1e1e1e")
signalLight2 = canvas2.create_oval(0, 0, 12, 12, fill="gray", outline="#1e1e1e")
signalLight3 = canvas3.create_oval(0, 0, 12, 12, fill="gray", outline="#1e1e1e")

otherInfoLabelText = tkinter.Label(root, font=customFont2, justify="left", text=f"  Uptime: {serverUptime}\n  Outputs size: {outputsSize}\n  Logs size limit:\n  Single mouse controller")
otherInfoLabelText.grid(row=12, column=0, sticky=W, pady=(0, 265), padx=140)

sizeLimitEntry = Entry(root, width=8, font=customFont3, justify="left", textvariable=outputsSizeLimitEntered)
sizeLimitEntry.grid(row=12, column=0, sticky=W, pady=(0, 249), padx=250)
sizeLimitEntry.config(state=DISABLED)
sizeLimitEntry.config(state=DISABLED)

singleMouseControllerBtn = Checkbutton(root, width=5, variable=singleMouseControllerCheck, textvariable=singleMouseControllerCheckText, command=updateSingleMouseControllerCheck)
singleMouseControllerBtn.grid(row=12, column=0, sticky=W, pady=(0, 215), padx=310)
singleMouseControllerBtn.config(state=DISABLED)

stLbl = tkinter.Label(root, font=customFont2, justify="left", textvariable=stl)
stLbl.place(rely=0.96)

serverOutputsBtn = Button(root, text="Server outputs", width=13, command=openServerOutputs)
serverOutputsBtn.place(rely=0.95, relx=0.78)

threading.Thread(target=upDatePaths).start()
threading.Thread(target=checkJAVA).start()
threading.Thread(target=updateConnectedDevices).start()
threading.Thread(target=updateBlockedOrKickedDevices).start()
threading.Thread(target=updateVisitsLog).start()
threading.Thread(target=updateOutputsSize).start()
threading.Thread(target=updateServerUptime).start()

root.protocol("WM_DELETE_WINDOW", onClose)
root.mainloop()