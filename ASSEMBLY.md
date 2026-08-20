# Assembly Guide

This is my actual build log — every wire, every menu, exactly where I clicked. If I already know my way around an Arduino I'd just use the quick version in README.md, but I wrote this one out in full so I wasn't guessing at anything mid-build.

## What I need on the table before starting

- Arduino Uno
- RC522 RFID reader module
- 7 jumper wires, female-to-male — the RC522's pins are male, sticking up, and the Uno's headers are female sockets, so I need a wire that's female on the RC522 end and male on the Uno end
  - If I only have male-to-male wires, I push the RC522 into a breadboard first, then run male-to-male wires from the breadboard to the Uno instead
- USB cable for the Uno
- Laptop, connected to the internet for the one-time software install

## First, I read the RC522's pin labels

There are 8 pins in a row along one edge of the board, each with a tiny label printed right on it: SDA, SCK, MOSI, MISO, IRQ, GND, RST, 3.3V. I read the actual labels on my specific board instead of assuming a left-to-right order — apparently this varies between manufacturers.

## Then I connect the wires, one at a time

I do this one wire at a time so I don't lose track. For each one, I push the wire's female end onto the labeled RC522 pin, and the male end into the matching Uno socket.

| # | RC522 pin | Uno pin | Where I find it on the Uno |
|---|---|---|---|
| 1 | 3.3V | 3.3V | Power header block, next to the USB/power jack — grouped with 5V, GND, VIN |
| 2 | RST | 9 | Digital header along the top edge |
| 3 | GND | GND | Any GND pin works, there are a few |
| 4 | MISO | 12 | Digital header |
| 5 | MOSI | 11 | Digital header |
| 6 | SCK | 13 | Digital header |
| 7 | SDA (sometimes printed as SS) | 10 | Digital header |
| — | IRQ | *(nothing)* | I leave this one alone, it's not used |

## Before I power anything on, I double-check

I trace all 7 wires back against the table above before plugging in the USB cable. The one mistake that actually damages the module is landing the RC522's 3.3V pin on the Uno's 5V pin instead — they sit right next to each other, so I check that specific connection twice.

## I install Arduino IDE

I grab it from arduino.cc if I don't already have it. Either 1.8.x or 2.x works fine for this.

## I install the MFRC522 library

- On IDE 2.x, I click the library icon in the left sidebar, search `MFRC522`, and install the one by GithubCommunity.
- On IDE 1.x, or as a backup on either version, I go Sketch → Include Library → Manage Libraries, search `MFRC522`, and install it there instead. (Same option's also under the Tools menu on both versions.)

## I flash the sketch

1. I plug the Uno into my laptop with the USB cable
2. I open `attendance_reader/attendance_reader.ino` in the IDE
3. Tools → Board → I select Arduino Uno
4. Tools → Port → I pick whichever port showed up when I plugged the Uno in
5. I click Upload and wait for "Done uploading" at the bottom

## I confirm the reader's actually working

1. Tools → Serial Monitor
2. I set the baud rate dropdown, bottom-right of that window, to 9600
3. I hold a card within about 1-3cm of the reader — it's short range, not going to pick up anything from across the desk
4. I should see a line print: `UID:XXXXXXXX`
5. If nothing shows up, I unplug the USB, go back through every one of the 7 wires against the table above, and physically re-check each one before trying again — no guessing which one's wrong

## Once that's working, I move to the README

Once I'm reliably seeing `UID:XXXXXXXX` every time I tap, the hardware side's done. Software setup — registering students, running the daily logger — is back in README.md.
