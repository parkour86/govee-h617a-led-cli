import asyncio
import sys
from bleak import BleakClient
from typing import Optional

"""
Govee_LED.py

# BlueZ version 5.76 or higher is required
# Bluetooth 5.2 or later adapters

Control and query the state of a Govee LED strip via Bluetooth LE.
Features:
- Turn the LED strip ON or OFF
- Query the current LED state
- Toggle the LED state
- Scan and list all GATT services and characteristics

Tested on Govee LED model H617A.
"""

# How to find your Bluetooth adapter name:
#   • Run: hciconfig or bluetoothctl list
#   • Look for names like "hci0", "hci1", etc.
#   • Enter the correct adapter name below.
ADAPTER = "hci1"

# How to get your Govee MAC address:
#   • Install bluez-tools if you don't have it:
#       sudo apt install bluez-tools
#   • Then list Bluetooth devices:
#       bt-device -l
#   • Find your Govee device in the list and copy its MAC address below.
DEVICE_ADDRESS = "CE:36:35:30:1D:52"

## GATT characteristic UUIDs for your Govee device.
#
# How to discover these UUIDs for your device:
#   • Run this script with the "scan" argument:
#       python3 Govee_LED.py scan
#   • Make sure your device is powered on and nearby.
#   • The script will list all GATT services and characteristics.
#   • Pay attention to the UUIDs of the writable and readable characteristics.
WRITE_CHAR_UUID = "00010203-0405-0607-0809-0a0b0c0d2b11" # Properties: read, write-without-response, write, notify
READ_CHAR_UUID  = "00010203-0405-0607-0809-0a0b0c0d2b10" #Properties: read, notify

# Payloads
# How to obtain these for your device:
#   • Using nRF Connect (Android/iOS):
#       - Connect to your Govee device.
#       - Perform actions (e.g., turn on/off) in the official app.
#       - Observe the "Write" commands sent to the writable characteristic.
#       - Copy the hex payloads shown.
#   • Using Linux tools:
#       - Use `bluetoothctl` or `gatttool` to connect and write to characteristics.
#       - Or, use `btmon` to sniff BLE traffic while controlling the device with the app.
#       - Extract the payloads from the captured packets.
ON_PAYLOAD  = bytes.fromhex("3301010000000000000000000000000000000033")
OFF_PAYLOAD = bytes.fromhex("3301000000000000000000000000000000000032")
STATUS_TRIGGER_PAYLOAD = bytes.fromhex("AA010000000000000000000000000000000000AB")

async def get_led_state(client: BleakClient) -> str:
    notification_received = asyncio.Event()
    state_result: dict[str, str] = {"state": "UNKNOWN"}  # <-- Fixed type

    def notification_handler(sender, data):
        print(f"🔔 Notification from {sender}: {data.hex()}")
        if len(data) >= 3 and data[0] == 0xAA:
            if data[2] == 1:
                state_result["state"] = "ON"
            elif data[2] == 0:
                state_result["state"] = "OFF"
            else:
                print("⚠️ Unknown state byte:", data[2])
            notification_received.set()

    await client.start_notify(READ_CHAR_UUID, notification_handler)
    await client.write_gatt_char(WRITE_CHAR_UUID, STATUS_TRIGGER_PAYLOAD, response=True)

    try:
        await asyncio.wait_for(notification_received.wait(), timeout=8)
    except asyncio.TimeoutError:
        print("⏰ No notification received.")

    await client.stop_notify(READ_CHAR_UUID)
    return state_result["state"]

async def set_led_state(on: bool, client: Optional[BleakClient] = None):
    """Set LED state using an existing client or by creating a new one."""
    if client is not None:
        payload = ON_PAYLOAD if on else OFF_PAYLOAD
        await client.write_gatt_char(WRITE_CHAR_UUID, payload, response=True)
        print(f"✅ Sent {'ON' if on else 'OFF'} command.")
    else:
        async with BleakClient(DEVICE_ADDRESS, adapter=ADAPTER) as client2:
            if not client2.is_connected:
                print("❌ Failed to connect to the device.")
                return
            payload = ON_PAYLOAD if on else OFF_PAYLOAD
            await client2.write_gatt_char(WRITE_CHAR_UUID, payload, response=True)
            print(f"✅ Sent {'ON' if on else 'OFF'} command.")

async def scan_characteristics():
    try:
        print(f"Connecting to {DEVICE_ADDRESS} using adapter {ADAPTER}...")
        async with BleakClient(DEVICE_ADDRESS, adapter=ADAPTER) as client:
            if not client.is_connected:
                print("❌ Failed to connect to the device.")
                return
            print("Listing all GATT characteristics and their properties:")
            for service in client.services:
                print(f"Service: {service.uuid} ({service.description})")
                for char in service.characteristics:
                    props = ', '.join(char.properties)
                    print(f"  Characteristic: {char.uuid} ({char.description})")
                    print(f"    Properties: {props}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    if len(sys.argv) != 2 or sys.argv[1].lower() not in ("on", "off", "check", "toggle", "scan"):
        print(
            "Usage: python3 govee_led.py [on|off|check|toggle|scan]\n"
            "  on     - Turn the LED strip ON\n"
            "  off    - Turn the LED strip OFF\n"
            "  check  - Query and print the current LED state\n"
            "  toggle - Toggle the LED state (ON->OFF or OFF->ON)\n"
            "  scan   - List all GATT services and characteristics with their properties\n"
        )
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "scan":
        await scan_characteristics()
        return

    async with BleakClient(DEVICE_ADDRESS, adapter=ADAPTER) as client:
        if not client.is_connected:
            print("❌ Failed to connect to the device.")
            return

        if command == "check":
            state = await get_led_state(client)
            print(f"🟢 LED state: {state}")

        elif command == "toggle":
            current = await get_led_state(client)
            if current == "ON":
                print("🔁 Toggling OFF...")
                await set_led_state(False, client)
            elif current == "OFF":
                print("🔁 Toggling ON...")
                await set_led_state(True, client)
            else:
                print("⚠️ Could not determine LED state to toggle.")

        elif command in ("on", "off"):
            await set_led_state(on=(command == "on"), client=client)

if __name__ == "__main__":
    asyncio.run(main())
