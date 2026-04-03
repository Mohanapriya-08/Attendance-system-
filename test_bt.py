import asyncio
from bleak import BleakScanner

async def scan():
    print("Scanning for 10 seconds...")
    devices = await BleakScanner.discover(timeout=10.0)
    if devices:
        for d in devices:
            print(f"Found: {d.name} | Address: {d.address}")
    else:
        print("No devices found!")

asyncio.run(scan())