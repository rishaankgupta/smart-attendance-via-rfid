# Assembly Guide

Physical build, start to finish. If you already know your way around an Arduino, use the quick version in README.md instead — this one spells out every step.

## Parts on the table before you start

- Arduino Uno
- RC522 RFID reader module
- 7 jumper wires — **female-to-male**. RC522's pins are male (sticking up); the Uno's headers are female sockets. You need a wire that's female on the RC522 end and male on the Uno end.
  - If your kit only has male-to-male wires: push the RC522's pins into a breadboard first, then run male-to-male wires from the breadboard to the Uno instead.
- USB cable for the Uno (USB-A to USB-B, printer-cable style)
- Laptop with internet access (for the one-time IDE + library install)

## Step 1 — Read the RC522's pin labels

The RC522 has 8 pins in a row along one edge. Each one has a tiny label printed on the board itself: `SDA`, `SCK`, `MOSI`, `MISO`, `IRQ`, `GND`, `RST`, `3.3V`. Read the actual labels on your specific board — don't assume a left-to-right order, it varies between manufacturers.

## Step 2 — Connect the wires, one at a time

Do this one wire at a time so you don't lose track of which is which. Push the wire's female end onto the labeled RC522 pin, and the male end into the matching Uno socket.

| # | RC522 pin | Uno pin | Where it is on the Uno |
|---|---|---|---|
| 1 | 3.3V | 3.3V | Power header block, next to the USB/power jack — grouped with 5V, GND, VIN |
| 2 | RST | 9 | Digital header along the top edge |
| 3 | GND | GND | Any GND pin — there are several, any of them works |
| 4 | MISO | 12 | Digital header |
| 5 | MOSI | 11 | Digital header |
| 6 | SCK | 13 | Digital header |
| 7 | SDA *(sometimes printed as SS)* | 10 | Digital header |
| — | IRQ | *(nothing)* | Leave this pin disconnected — it's not used |

## Step 3 — Double-check before powering on

Before plugging in the USB cable, trace each of the 7 wires back against the table above. The one mistake that actually damages the module: **RC522's 3.3V pin landing on the Uno's 5V pin instead of 3.3V.** They're right next to each other — check that connection twice.

## Step 4 — Install Arduino IDE

Download it from arduino.cc if it's not already installed. Version 1.8.x or 2.x both work fine for this.

## Step 5 — Install the MFRC522 library

- **IDE 2.x:** click the library icon in the left sidebar, search `MFRC522`, install the one by GithubCommunity.
- **IDE 1.x, or as a fallback in either version:** Sketch → Include Library → Manage Libraries → search `MFRC522` → Install. (This same path also exists under the Tools menu in both versions.)

## Step 6 — Flash the sketch

1. Plug the Uno into your laptop with the USB cable.
2. In Arduino IDE, open `attendance_reader/attendance_reader.ino`.
3. Tools → Board → select **Arduino Uno**.
4. Tools → Port → select the port that appeared when you plugged in the Uno (there should only be one new option).
5. Click **Upload** (the right-arrow icon in the toolbar). Wait for "Done uploading" at the bottom.

## Step 7 — Confirm the reader actually works

1. Tools → Serial Monitor.
2. Set the baud rate dropdown (bottom-right corner of the Serial Monitor window) to `9600`.
3. Hold an RFID card or tag within about 1-3cm of the RC522 — this reader has a short range, it's not a wave-from-a-distance scanner.
4. You should see a line print: `UID:XXXXXXXX`.
5. **Nothing printing?** Unplug the USB cable, re-trace every one of the 7 wires against the Step 2 table — don't guess which one is wrong, physically re-check each connection — then plug back in and try again.

## Step 8 — Move on to software setup

Once you're reliably seeing `UID:XXXXXXXX` for every tap, the hardware side is done. Go to README.md for registering students and running the daily logger.
