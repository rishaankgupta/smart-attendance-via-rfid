# School RFID Attendance System

I built this for my class. We already carry plastic ID cards with a paper insert showing our name, roll number, and class — so instead of giving everyone one more thing to carry, I'm putting an RFID sticker inside the same card. Tap it at the door and attendance gets marked automatically. Hardware side is an Arduino Uno + RC522 reader, software side is a Python script on my laptop doing the actual logging.

## Before I built anything, I had to get real about a few things

- **The ID cards we already have don't have an RFID chip in them.** Plain laminated cards never do unless someone specifically pays for "smart" ones. That's why I'm using separate RFID stickers and sliding them into the same card holder, instead of assuming the existing cards would just work.
- **This doesn't stop someone tapping a friend's card for them.** There's genuinely no way around that with a simple tap system — I'm treating it as a known limitation, not something I can code my way out of.
- **One reader means one card at a time**, with roughly a 1-second gap built in between reads (more on why further down). For a full class that's a real queue at the door, not instant mass tap-in.
- **The school actually has to sign off on this before I mount anything at a door.** Power, wiring, something physically fixed to a doorframe — none of that happens before someone official says yes.
- **I'm treating this as a side-tracker, not the official register**, at least until it's survived a few real weeks of daily use. If my laptop's off, or I'm not there to run it, nothing gets logged that day — there's no backup for that yet.

## What I'm using

**Already had this from my kit:**
- Arduino Uno
- RC522 RFID reader — comes with only 1-2 tags out of the box, nowhere near enough for a class
- Jumper wires, breadboard, battery packs

**Had to buy:**
- Around 40-45 RFID tags/stickers, 13.56MHz Mifare (has to match the RC522's frequency). Found these running roughly ₹10-25 a piece depending on where I looked — so budget somewhere around ₹500-900 for the whole class, but get an actual quote before ordering in bulk, prices jump around a lot.

Everything else in a kit like this — motors, wheels, keypad, ultrasonic sensor, micro:bit — none of it's used here. Didn't force it in just because it was sitting in the box.

## Wiring — RC522 to Arduino Uno

| RC522 pin | Uno pin |
|---|---|
| SDA/SS | 10 |
| SCK | 13 |
| MOSI | 11 |
| MISO | 12 |
| RST | 9 |
| GND | GND |
| 3.3V | 3.3V — **not 5V**, that's the easiest way to kill this module |
| IRQ | left unconnected |

## How I set it up

### Arduino side

I wrote up the full physical process — every wire, every menu, where things actually are on the board — separately in [ASSEMBLY.md](ASSEMBLY.md), since cramming all of it here would've made this file unreadable. Short version of what I did:

1. Wired the RC522 to the Uno per the table above
2. Installed the `MFRC522` library through the Library Manager
3. Uploaded `attendance_reader/attendance_reader.ino`
4. Opened Serial Monitor at 9600 baud and confirmed tapping a card prints `UID:XXXXXXXX`

If any of that's unfamiliar, I'd go read ASSEMBLY.md instead — didn't skip anything there.

### Python side

1. `pip install pyserial`
2. Copied `students.example.csv` to `students.csv` in the same folder — columns are UID, Name, RollNumber, Class
3. Found my Arduino's port (Tools → Port in the IDE), opened `attendance_logger.py`, set `PORT` to match
4. Ran it: `python attendance_logger.py`
5. **Registration session** — went through everyone's ID cards one at a time. Each unregistered tap prints `Unknown card — UID: XXXX` in the console, so I read the name, roll number, and class straight off the card and added the row to `students.csv`. Once every card was in, saved the file and restarted the script — it only reads `students.csv` at startup, not live, so a restart's needed after any edit.
6. From there, every tap logs to `attendance_log.csv` as UID, Name, RollNumber, Class, Date, Time. A repeat tap by the same card on the same day gets skipped — resets at midnight, not on a rolling timer (why I went with calendar-day instead of a rolling window is further down).

### Testing I did before trying it on the full class

- Confirmed the card gets picked up reliably within about 1-3cm of the reader
- Checked the same card gives the same UID every time
- Made sure the script connects to the right port without errors
- Verified a second tap on the same day actually gets skipped, not double-logged
- Opened `attendance_log.csv` in Excel afterward to make sure it looked right
- Ran it with 3-4 people first before trying the whole class

## Bugs I actually found going through this line by line

I didn't just eyeball this and call it done — here's what was genuinely wrong and what I changed:

1. **Case-sensitivity issue.** The Arduino sends UIDs in uppercase, but my Python script wasn't forcing the incoming text to uppercase before comparing it against the student list. It worked, purely because the Arduino happened to always send uppercase — one small change away from silently breaking. Both sides force uppercase now.
2. **Missing a pause after connecting.** Opening a serial connection resets an Arduino Uno — it reboots and takes a second. The script could start reading before the board was actually ready. Added a 2-second pause right after connecting.
3. **Duplicate-check was reading the whole log file on every single tap.** Fine on day one, but that file grows by ~40 rows a day, and by the end of a school year that's thousands of rows getting re-scanned per tap. Now it loads today's attendance into memory once at startup and checks from there.
4. **A dropped USB cable used to crash the whole script** with a raw error dump. Now it catches that and just says the connection was lost instead.
5. **UID parsing was doing a find-and-replace instead of a clean slice, and a malformed row in students.csv would've crashed the whole thing.** Cleaned up the parsing, and bad rows now get skipped with a warning instead of taking the script down.
6. **Found this one while adding Roll Number/Class:** the duplicate-check was keyed off *Name*. Two people with the same first name — pretty likely in a class of 35-40 — would've collided, and the second one to tap would've been wrongly told they were "already marked present" without ever tapping. Switched the key to UID, which is actually guaranteed unique, and the log stores UID too now so this stays correct even if the script restarts mid-day.

I also thought about an exact 24-hour cooldown between scans instead of a calendar-day reset, since it sounded more precise. Decided against it — a rolling 24 hours would've blocked someone from tapping in if they showed up even a few minutes earlier than they had the day before. Calendar-day reset doesn't have that problem, since nobody's tapping in near midnight anyway.

The Arduino sketch itself checked out clean — no bugs, just the one limitation below that I left alone on purpose.

## What this still can't do

- **Caps out around 1 scan a second.** The sketch pauses a full second after every read so it doesn't spam-read the same card sitting near it. Deliberate, not an oversight — but it means 40 people tapping in perfectly, back to back, still takes at least 40 seconds. Add real walking-up time and it's closer to 2-3 minutes for a full class. Fixing this properly means rewriting the timing to be non-blocking, which needs testing on the actual board to get right, so I haven't touched it yet.
- **Doesn't stop proxy tapping.** Not solvable with this hardware.
- **The cards themselves aren't that secure.** RC522 checks by UID, and MIFARE Classic's encryption is broken, so a cheap cloner could copy a UID onto a blank card. Doesn't matter for a class attendance project, but I'm not calling this tamper-proof to my school, because it isn't.
- **One laptop has to be running this for anything to log.** No laptop, no record, no automatic fallback.

## Before pushing this to GitHub

Once I actually start using this, `students.csv` and `attendance_log.csv` will have my classmates' real names sitting next to timestamps. Putting that on a public repo means their data's public too, permanently, without them agreeing to any of it.

The `.gitignore` already keeps both files out — only `students.example.csv`, with fake data, gets committed. Not removing that exclusion, and checking `git status` before every first commit just to be sure nothing real snuck in.

## What's in here

- `ASSEMBLY.md` — the full physical build, wire by wire
- `attendance_reader/attendance_reader.ino` — reads card UIDs over SPI, sends them out over Serial
- `attendance_logger.py` — matches UIDs to student records, writes the log
- `students.example.csv` — shows the format (UID, Name, RollNumber, Class) — copy it to `students.csv` and fill in real data, never commit that one
- `.gitignore` — keeps the real student data out of the repo
