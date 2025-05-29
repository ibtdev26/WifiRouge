# WiFiRogue

A powerful Python-based RTL8720DN WiFi Deauther tool by IBTDEV

CODE WONT BE OBFUSCATED IN THE NEXT UPDATE!

---

## About

WiFiRogue is a command-line tool designed to interface with RTL8720DN WiFi chipset-based devices to scan nearby WiFi networks and launch deauthentication attacks. This tool helps demonstrate vulnerabilities in WiFi networks and can be used for educational and authorized penetration testing purposes.

WiFiRogue communicates with the device through a local web interface, sending commands to scan networks, launch deauth attacks, and stop attacks. The tool uses Python libraries such as Requests for HTTP communication and BeautifulSoup for parsing network scan results.

---

## Features

- Scan for nearby WiFi networks with details including SSID, BSSID, channel, and signal strength (RSSI).
- Launch deauthentication attacks on one or more selected networks.
- Stop ongoing attacks.
- User-friendly terminal interface with colored output.
- Built-in connection check to ensure the tool is connected to the correct device network before performing operations.

---

## Installation

### Prerequisites

- Python 3.7 or later
- RTL8720DN device with its default WiFi network (usually something like `RTL8720DN-xxxxxx`)

### Steps

Clone the repository:

```bash
git clone https://github.com/ibtdev26/WiFiRogue.git
cd WiFiRogue
pip install -r requirements.txt
python ./WifiRouge.py
```

### Run The File

```bash
python ./WifiRouge.py
```




