# 🌉 OSC to MIDI Bridge

A Python-based command-line tool that translates Open Sound Control (OSC) messages into MIDI Note On/Off commands. This is perfect for controlling DAWs, VJ software, or other MIDI-enabled applications using OSC controllers (like TouchOSC or applications like Ableton Live's OSC integration).

Built by **Felix Hardt** - [github.com/Felix2180](https://github.com/Felix2180)

---

## ✨ Features

* **OSC to MIDI Translation:** Converts a specific OSC address format into MIDI Note On/Off messages.
* **Command Line Configuration:** Easy setup via an interactive console menu.
* **Network Setup:** Select the local network interface and custom OSC listening port (UDP).
* **MIDI Output Selection:** Select any available virtual or phsyical MIDI output port (e.g., from LoopMIDI).
* **Persistence:** Automatically saves and loads the last used settings (`config.json`).
* **Multilingual:** Supports English and German interfaces.
* **Clean Interface:** Clears the console after each menu selection for a tidy experience.
* **Portable:** Can be packaged into a single executable (`.exe`) file using PyInstaller.

---

## 🚀 Getting Started

### Prerequisites

1.  **Python 3:** Required to run the script directly.
2.  **Loop Midi (Windows Only):** Since Python cannot natively host a virtual MIDI output port on Windows, you must install a third-party tool **LoopMIDI** and create a virtual port (e.g., named "OSC-MIDI").

### Installation

Install the necessary Python libraries:

```bash
pip install python-osc mido python-rtmidi
```

### Usage
1. Start the script from your command line:
```bash
python converter.py
```
2. The script will launch the Midi Port Selection menu first.
3. The Main menu will guide you through the setup:
     1. Network Interface (Listen): Select your local IP address or 0.0.0.0 to listen on all interfaces.
     2. OSC Port (Listen): Select the port on the network interface that you want to listen for OSC Data on.
     3. MIDI Port (Send): Select the virtual MIDI port you created (e.g. "OSC-MIDI")
     4. Verbose/Logging: Here you can turn logging the OSC input and Midi Output on/off.
     5. Language/Sprache: Here you can switch your language from English to German or vice versa.
     6. START Converter: This will start the application and the converter will start converting.
     7. Exit: Should be self explanatory.

  ---

  ## 📌 OSC Mapping Standard

  The converter expects OSC messages in the following structured format:
  /CHANNEL/NOTE/VELOCITY

| OSC Path  Segment | Description      | Value  Range | Midi Effect                                               |
|-------------------|------------------|--------------|-----------------------------------------------------------|
| CHANNEL           | MIDI Channel     | 1 to 16      | Controls the target MIDI channel  (0-indexed internally). |
| NOTE              | MIDI Note Number | 0 to 127     | Controls the pitch (e.g., 60 is Middle C).                |
| Velocity          | Note Intensity   | 1 to 127     | Note On (Activates the note).                             |
| Velocity          | Note Intensity   | 0            | Note Off (Deactivates the note).                          |


### Examples

| OSC Message | Action                                               |
|-------------|------------------------------------------------------|
| /1/60/127   | MIDI Channel 1, Note 60 (C4), Velocity 127 (Note ON) |
| /1/60/0     | MIDI Channel 1, Note 60 (C4), Velocity 0 (Note OFF)  |
| /1/10/48    | MIDI Channel 10, Note 48 (C3), Velocity 90 (Note ON) |

---

## 🖼️ User Interface Preview
<img width="1115" height="628" alt="image" src="https://github.com/user-attachments/assets/89e5da0d-9a39-42be-8c37-1182ba95ce35" />

---

## ⚙️ Building the Executable (.exe)

You can package the script and all dependecies into a standalone Windows executable using PyInstaller.
1. Install PyInstaller
```bash
pip install pyinstaller
```
2. Navigate to your script directory and run the command, ensuring you include the necessary hidden import for MIDI functionality:
```bash
pyinstaller --onefile --hidden-import mido.backends.rtmidi converter.py
```
3. The executable (`converter.exe`) will be found in the newly created `dist` folder.
