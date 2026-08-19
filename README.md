# School RFID Attendance System

Tap-in attendance for a classroom: RC522 RFID reader + Arduino Uno reads a card's ID and sends it over USB to a Python script, which matches it to a student and logs the timestamp to a CSV.

## Read this before you build anything

- **Your classmates' current paper ID cards have no RFID chip in them.** Plain laminated cards don't, unless someone specifically ordered "smart cards." You need real RFID tags. Cheapest fix: buy thin RFID stickers (13.56MHz Mifare) and slide them into the same plastic card holder they already carry — no new object for anyone to hold onto.
- **This does not stop proxy attendance.** Anyone can tap a friend's card for them. No simple card system solves this. Don't market it as fraud-proof.
- **One reader reads one card at a time, with a hard ~1 second gap.** See "Known limitations" for the actual math — for a full class this means a real queue at the door, not instant mass tap-in.
- **Get school permission before mounting anything at a door.** Power, wiring, something physically fixed to a doorframe — all need sign-off first, not after you've already built the enclosure.
- **This is a demo-grade system, not an official register.** Treat it as a side-tracker until it's survived weeks of real daily use. If the laptop's off, or you're absent, nothing gets logged that day — there's no automatic fallback.

## Hardware

**Already in your kit:**
- Arduino Uno
- RC522 RFID reader (13.56MHz) — ships with only 1-2 tags, not enough for a class
- Jumper wires, breadboard, battery packs

**Buy separately:**
- ~40-45 RFID tags/cards/stickers, 13.56MHz Mifare (must match the RC522's frequency). Roughly ₹10-25/piece in India depending on vendor and quantity — get an actual quote before ordering in bulk.

**Not used in this project** — ignore the rest of a general kit (motors, wheels, keypad, ultrasonic sensor, micro:bit, etc.) if you have one; none of it is needed here.

## Wiring — RC522 to Arduino Uno

| RC522 pin | Uno pin |
|---|---|
| SDA/SS | 10 |
| SCK | 13 |
| MOSI | 11 |
| MISO | 12 |
| RST | 9 |
| GND | GND |
| 3.3V | 3.3V — **not 5V**, this is the #1 way people fry this module |
| IRQ | leave unconnected |

## Setup — step by step

### 1. Arduino side

Full physical walkthrough — exact wires, exact menus, exact locations on the board — is in **[ASSEMBLY.md](ASSEMBLY.md)**. Quick version:

1. Wire the RC522 to the Uno per the table above.
2. Install the `MFRC522` library (Library Manager).
3. Upload `attendance_reader/attendance_reader.ino`.
4. Confirm in Serial Monitor (9600 baud) that tapping a card prints `UID:XXXXXXXX`.

If any of that isn't already familiar, use ASSEMBLY.md instead of this — it doesn't skip steps.

### 2. Python side

1. Install Python 3 if you don't have it, then: `pip install pyserial`
2. Copy `students.example.csv` to a new file named `students.csv` in the same folder. Columns are UID, Name, RollNumber, Class.
3. Find your Arduino's port (Arduino IDE → Tools → Port). Open `attendance_logger.py` and set `PORT` at the top to match — e.g. `"COM5"` on Windows, `"/dev/ttyUSB0"` or `"/dev/ttyACM0"` on Mac/Linux.
4. Run: `python attendance_logger.py`
5. **Registration session:** go through the collected ID cards one at a time. Tap each card — an unregistered one prints `Unknown card — UID: XXXX` in the console. Read that student's name, roll number, and class straight off their card, and add the row to `students.csv`. Once every card's added, save the file and restart the script (it loads `students.csv` once at startup, not live, so a restart is required after editing).
6. From then on, taps log to `attendance_log.csv` as UID, Name, RollNumber, Class, Date, Time. A second tap by the same card on the same day is skipped automatically — this resets at midnight, not on a rolling timer (see "What I actually checked and fixed" for why that's the better choice here).

### 3. Test before rolling out to the full class

- [ ] Card is detected reliably within ~1-3cm of the reader (that's the real range — this is not a long-range scanner)
- [ ] The same card gives the same UID every time
- [ ] Script connects to the correct port without errors
- [ ] A repeat tap on the same day is correctly skipped, not double-logged
- [ ] `attendance_log.csv` opens cleanly in Excel/Google Sheets afterward
- [ ] Try it with 3-4 people before the full class

## What I actually checked and fixed

You asked for a line-by-line pass — here's what was really wrong in the first version, not a rubber stamp:

1. **Case-sensitivity bug (real, silent-failure risk).** The Arduino sends UIDs in uppercase, but the Python script wasn't forcing incoming text to uppercase before comparing it to the student list. It worked, purely because the Arduino always happened to send uppercase — one small future change on either side and matching would silently break. Fixed: both sides now force uppercase explicitly.
2. **Missing reboot delay (real bug).** Opening a serial connection resets an Arduino Uno — it reboots and takes a moment. The script could start reading before the board was ready. Fixed: added a 2-second pause right after connecting.
3. **Inefficient duplicate-check (real, gets worse over time).** The original re-read the entire `attendance_log.csv` from disk on every single tap just to check for a duplicate. Fine on day one; by the end of a school year that file has thousands of rows being re-scanned on every tap. Fixed: today's attendance now loads into memory once at startup and is checked from memory after that.
4. **No handling for a dropped USB cable (real gap).** If the cable came loose mid-run, the script crashed with a raw traceback. Fixed: it now catches that and shuts down with a plain message instead.
5. **Minor cleanup.** UID parsing now uses direct slicing instead of find-and-replace, and rows in `students.csv` missing a name or UID are skipped with a warning instead of crashing the script.
6. **Name-collision bug (real, found while adding Roll Number/Class).** The duplicate-check was keying off the student's *Name* string. Two students with the same first name — genuinely likely in a class of 35-40 — would have collided: the second one to tap would get wrongly told "already marked present," even though they hadn't tapped at all. Fixed: the duplicate-check and the in-memory tracking now key off *UID*, which is guaranteed unique, and `attendance_log.csv` now stores UID as a column too so this stays correct even after a restart mid-day.

We also discussed and deliberately rejected an exact-24-hour rolling cooldown in favor of the calendar-day reset that was already here — a rolling window would've blocked a student from tapping in if they arrived even a few minutes earlier than their tap time the previous day. Calendar-day reset doesn't have that failure mode, since nobody's tapping in near midnight anyway.

The Arduino sketch checked out with no bugs — its one real limitation is below, left as-is on purpose.

## Known limitations

- **Throughput is capped at roughly 1 scan/second.** The sketch blocks for a full second after every read so it doesn't spam-read the same card. That's a deliberate simple choice, not an oversight — but it means 40 students tapping perfectly back-to-back, zero fumbling, still take at least 40 seconds. Add realistic walk-up time and it's closer to 2-3 minutes for a full class. A non-blocking rewrite (using `millis()` instead of `delay()`) would remove this cap, but it needs testing on your actual board to get right — don't take an untested version of that fix from anyone, this repo included.
- **No protection against proxy tapping.** Not solvable with this hardware — anyone can tap someone else's card.
- **MIFARE Classic cards are clone-able.** The RC522 authenticates by UID, and MIFARE Classic's Crypto1 encryption is broken — a cheap cloner can copy a UID onto a blank card. Irrelevant risk for a class attendance demo, but don't describe this system as tamper-proof to your school.
- **Single point of failure.** One laptop has to be running the script for anything to log. No laptop running = no record for that day, with no automatic fallback.

## Before you push this to GitHub

Once you're actually using this, `students.csv` and `attendance_log.csv` will contain your classmates' **real names paired with timestamps**. Publishing that on a public repo puts their personal data online, indexed by search engines, without them agreeing to it.

The included `.gitignore` already excludes both files — only `students.example.csv` (fake data) gets committed. Don't remove that exclusion, and run `git status` before your first commit to confirm no real data is staged.

## Files

- `ASSEMBLY.md` — full physical build guide: exact wires, exact IDE menus, exact board locations
- `attendance_reader/attendance_reader.ino` — Arduino sketch, reads card UIDs over SPI and sends them via Serial
- `attendance_logger.py` — Python script, matches UIDs to student records and logs attendance
- `students.example.csv` — template showing the expected format: UID, Name, RollNumber, Class (copy to `students.csv`, fill in real data, never commit it)
- `.gitignore` — keeps real student data out of the public repo
