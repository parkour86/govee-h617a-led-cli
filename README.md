# Govee_LED.py

**Requirements:**
- Python 3
- The `bleak` library (`pip install bleak`)
- BlueZ version 5.76 or higher is required
- Bluetooth 5.2 or later adapters

Control and query the state of a Govee LED strip via Bluetooth LE.

This script allows you to:
- Turn the LED strip ON or OFF
- Query the current LED state
- Toggle the LED state
- Scan and list all GATT services and characteristics

Tested on Govee LED model H617A.

If you have a different Govee model, see Setup step 3 and 4 below to discover the correct UUIDs for your device.

---

## Setup

### 1. Find Your Bluetooth Adapter Name

- Run: `hciconfig` or `bluetoothctl list`
- Look for names like `hci0`, `hci1`, etc.
- Enter the correct adapter name in the script (`ADAPTER = "hciX"`).

### 2. Get Your Govee MAC Address

- Install bluez-tools if you don't have it:
  ```sh
  sudo apt install bluez-tools
  ```
- List Bluetooth devices:
  ```sh
  bt-device -l
  ```
- Find your Govee device in the list and copy its MAC address.
- Set `DEVICE_ADDRESS` in the script.

### 3. Discover GATT Characteristic UUIDs

- Run this script with the `scan` argument:
  ```sh
  python3 Govee_LED.py scan
  ```
- Make sure your device is powered on and nearby.
- The script will list all GATT services and characteristics.
- Pay attention to the UUIDs of the writable and readable characteristics.
- Update `WRITE_CHAR_UUID` and `READ_CHAR_UUID` in the script as needed.

### 4. Obtain Payloads for Your Device

#### Using nRF Connect (Android/iOS):
- Connect to your Govee device.
- Perform actions (e.g., turn on/off) in the official app.
- Observe the "Write" commands sent to the writable characteristic.
- Copy the hex payloads shown.

#### Using Linux Tools:
- Use `bluetoothctl` or `gatttool` to connect and write to characteristics.
- Or, use `btmon` to sniff BLE traffic while controlling the device with the app.
- Extract the payloads from the captured packets.

---

## Usage

```sh
python3 Govee_LED.py [on|off|check|toggle|scan]
```

- `on`     - Turn the LED strip ON
- `off`    - Turn the LED strip OFF
- `check`  - Query and print the current LED state
- `toggle` - Toggle the LED state (ON→OFF or OFF→ON)
- `scan`   - List all GATT services and characteristics with their properties

**Example:**
```sh
python3 Govee_LED.py on
```

---

## Notes

- The payloads and UUIDs provided in the script are for the Govee H617A model. Other models may require different values.
- If you have a different Govee device, follow the discovery steps above to obtain the correct values.


---
