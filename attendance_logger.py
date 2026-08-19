"""
Attendance Logger

Reads "UID:XXXX" lines from the Arduino over USB serial, matches
each UID to a student record using students.csv, and logs
attendance to attendance_log.csv (one entry per student per day).

SETUP
  1. pip install pyserial
  2. Copy students.example.csv to students.csv and fill in real
     student rows (UID, Name, RollNumber, Class). students.csv is
     gitignored on purpose — see the README for why.
  3. To find a student's UID: run this script, have them tap their
     card once. Unknown cards get printed to the console — copy
     that UID into students.csv next to their name.
  4. Set PORT below to your Arduino's port.
     Windows:   something like "COM5"
     Mac/Linux: something like "/dev/ttyUSB0" or "/dev/ttyACM0"
     (Arduino IDE -> Tools -> Port shows the right one)
"""

import serial
import csv
import os
import time
from datetime import datetime

PORT = "COM5"  # <-- change this to match your setup
BAUD_RATE = 9600
STUDENTS_FILE = "students.csv"
LOG_FILE = "attendance_log.csv"


def load_students(path):
    """Returns {uid: {"name":..., "roll":..., "class":...}}."""
    students = {}
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Copy students.example.csv to "
              f"{path} and fill in real student rows first.")
        return students
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = (row.get("UID") or "").strip().upper()
            name = (row.get("Name") or "").strip()
            roll = (row.get("RollNumber") or "").strip()
            cls = (row.get("Class") or "").strip()
            if not uid or not name:
                print(f"Skipping bad row in {path}: {row}")
                continue
            students[uid] = {"name": name, "roll": roll, "class": cls}
    return students


def load_today_attendance(path):
    """Set of UIDs already logged today. Read once at startup, then
    kept in memory. Keyed by UID, not name — two students can share
    a first name (or even a full name), and a name-based key would
    wrongly skip the second one as a 'duplicate.'"""
    logged = set()
    if not os.path.exists(path):
        return logged
    today = datetime.now().strftime("%Y-%m-%d")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Date") == today:
                logged.add((row.get("UID") or "").strip().upper())
    return logged


def log_attendance(uid, student, path):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["UID", "Name", "RollNumber", "Class", "Date", "Time"])
        now = datetime.now()
        writer.writerow([
            uid,
            student["name"],
            student["roll"],
            student["class"],
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
        ])


def main():
    students = load_students(STUDENTS_FILE)
    print(f"Loaded {len(students)} students from {STUDENTS_FILE}")

    logged_today = load_today_attendance(LOG_FILE)
    print(f"{len(logged_today)} students already marked present today")

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Could not open {PORT}: {e}")
        print("Check the port name in Arduino IDE -> Tools -> Port")
        return

    # Opening the serial port resets an Arduino Uno — it reboots and
    # takes a moment. Without this pause, a card tapped in the first
    # second or two after starting can be missed.
    time.sleep(2)
    print("Listening for scans... (Ctrl+C to stop)")

    try:
        while True:
            try:
                raw = ser.readline()
            except serial.SerialException:
                print("Lost connection to the Arduino — check the USB cable.")
                break

            line = raw.decode("utf-8", errors="ignore").strip()
            if not line.startswith("UID:"):
                continue

            uid = line[4:].strip().upper()

            if uid not in students:
                print(f"Unknown card — UID: {uid}. Add this to {STUDENTS_FILE}.")
                continue

            student = students[uid]

            if uid in logged_today:
                print(f"{student['name']} already marked present today — skipped.")
                continue

            log_attendance(uid, student, LOG_FILE)
            logged_today.add(uid)
            print(
                f"Marked present: {student['name']} "
                f"(Roll {student['roll']}, Class {student['class']}) "
                f"at {datetime.now().strftime('%H:%M:%S')}"
            )

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
