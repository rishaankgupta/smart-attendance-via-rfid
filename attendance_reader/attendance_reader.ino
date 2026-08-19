/*
  Attendance RFID Reader
  Board:  Arduino Uno
  Reader: RC522 (13.56MHz, SPI)

  WIRING (RC522 -> Uno):
    SDA/SS -> Pin 10
    SCK    -> Pin 13
    MOSI   -> Pin 11
    MISO   -> Pin 12
    RST    -> Pin 9
    GND    -> GND
    3.3V   -> 3.3V   <-- NOT 5V. 5V can damage this module.
    IRQ    -> leave disconnected

  SETUP:
    Arduino IDE -> Tools -> Manage Libraries -> search "MFRC522"
    (by GithubCommunity / miguelbalboa) -> Install.

  WHAT THIS DOES:
    Waits for a card, reads its unique ID (UID), and prints it
    over USB as: UID:XXXXXXXX

    It does NOT know student names. That mapping lives in the
    Python script on your laptop (students.csv), not here, so
    you can add or remove students without re-uploading code.

  KNOWN LIMITATION (see README):
    The 1-second delay() below is blocking — it caps this reader
    at roughly one scan per second, and it means a card presented
    during that window is missed entirely. That's a deliberate
    simple design, not an oversight. A non-blocking version using
    millis() instead of delay() would remove this cap, but that
    needs testing on real hardware to get right, so it isn't
    included here.
*/

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("READY");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  Serial.print("UID:");
  Serial.println(uid);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(1000); // one tap = one scan, not twenty — see limitation note above
}
