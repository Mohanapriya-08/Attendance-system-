import asyncio
import requests
from datetime import datetime
from bleak import BleakScanner

# ─────────────────────────────────────────
#  CONFIG — change these as needed
# ─────────────────────────────────────────
API_BASE    = "http://127.0.0.1:8000"
SESSION_ID  = None   # Will be set when class starts
SCAN_INTERVAL = 15   # seconds between each scan

# ─────────────────────────────────────────
#  STEP 1: Fetch all registered students
#          (so we can match device_id → student_id)
# ─────────────────────────────────────────
def get_registered_students():
    try:
        res = requests.get(f"{API_BASE}/get-students")
        if res.status_code == 200:
            return res.json().get("students", [])
    except Exception as e:
        print(f"[ERROR] Could not fetch students: {e}")
    return []

# ─────────────────────────────────────────
#  STEP 2: Start a class session
# ─────────────────────────────────────────
def start_class(teacher_id: int, subject: str, section: str):
    try:
        res = requests.post(f"{API_BASE}/start-class", params={
            "teacher_id": teacher_id,
            "subject": subject,
            "section": section
        })
        data = res.json()
        session_id = data.get("session_id")
        print(f"[✅] Class started! Session ID: {session_id}")
        return session_id
    except Exception as e:
        print(f"[ERROR] Could not start class: {e}")
        return None

# ─────────────────────────────────────────
#  STEP 3: Mark attendance via API
# ─────────────────────────────────────────
def mark_attendance(student_id: int, session_id: int, device_id: str):
    try:
        res = requests.post(f"{API_BASE}/mark-attendance", params={
            "student_id": student_id,
            "session_id": session_id,
            "device_id": device_id
        })
        return res.json().get("message", "")
    except Exception as e:
        print(f"[ERROR] Could not mark attendance: {e}")
        return None

# ─────────────────────────────────────────
#  STEP 4: Bluetooth scan + match
# ─────────────────────────────────────────
async def scan_and_mark(session_id: int, students: list):
    # Build a lookup: device_id (MAC) → student info
    device_map = {
        s["device_id"].upper(): s
        for s in students
        if s.get("device_id")
    }

    print(f"\n[📡] Scanning Bluetooth devices... ({datetime.now().strftime('%H:%M:%S')})")

    detected = await BleakScanner.discover(timeout=8.0)

    found_addresses = [d.address.upper() for d in detected]
    print(f"[🔍] Detected {len(found_addresses)} BT device(s): {found_addresses}")

    matched = 0
    for address in found_addresses:
        if address in device_map:
            student = device_map[address]
            msg = mark_attendance(student["id"], session_id, address)
            print(f"[✅] {student['name']} ({student['roll_no']}) — {msg}")
            matched += 1

    if matched == 0:
        print("[ℹ️ ] No registered students detected in this scan.")

# ─────────────────────────────────────────
#  STEP 5: End class
# ─────────────────────────────────────────
def end_class(session_id: int):
    try:
        res = requests.post(f"{API_BASE}/end-class/{session_id}")
        print(f"[✅] {res.json().get('message')}")
    except Exception as e:
        print(f"[ERROR] Could not end class: {e}")

# ─────────────────────────────────────────
#  MAIN — Interactive runner
# ─────────────────────────────────────────
async def main():
    print("=" * 50)
    print("  📡 BT Attendance Scanner")
    print("=" * 50)

    # --- Start class ---
    teacher_id = int(input("Enter Teacher ID     : "))
    subject    = input("Enter Subject        : ")
    section    = input("Enter Section        : ")

    session_id = start_class(teacher_id, subject, section)
    if not session_id:
        print("[ERROR] Failed to start class. Exiting.")
        return

    # --- Fetch students ---
    students = get_registered_students()
    if not students:
        print("[⚠️ ] No students found in database. Register students first via /register-student")
        return

    print(f"\n[📋] {len(students)} student(s) registered.")
    print(f"[🔄] Scanning every {SCAN_INTERVAL}s. Press Ctrl+C to end class.\n")

    # --- Scan loop ---
    try:
        while True:
            await scan_and_mark(session_id, students)
            await asyncio.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\n\n[🛑] Stopping scanner...")
        end_class(session_id)
        print(f"[📊] View attendance at: http://127.0.0.1:8000/get-attendance/{session_id}")
        print(f"[🖥️ ] Open dashboard and use Session ID: {session_id}")

if __name__ == "__main__":
    asyncio.run(main())