// This example code is in the Public Domain (or CC0 licensed, at your option.)
// By Evandro Copercini - 2018
//
// This example creates a bridge between Serial and Classical Bluetooth (SPP)
// and also demonstrate that SerialBT have the same functionalities of a normal Serial
// Note: Pairing is authenticated automatically by this device

#include <Arduino.h>
#include "BluetoothSerial.h"

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>



//#include <Fonts/Org_01.h>
#include <Fonts/Picopixel.h>



#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C






String device_name = "NavMyBike";
String message = "";
String range ="";
String direction="";
int new_update = 0;
int newlineIndex = -1;

String extractDirection(String msg);
String extractRange(String msg);

// Check if Bluetooth is available
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

// Check Serial Port Profile
#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Port Profile for Bluetooth is not available or not enabled. It is only available for the ESP32 chip.
#endif

BluetoothSerial SerialBT;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);



void setup() {
  Serial.begin(9600);
  SerialBT.begin(device_name);  //Bluetooth device name
  //SerialBT.deleteAllBondedDevices(); // Uncomment this to delete paired devices; Must be called after begin
  Serial.printf("The device with name \"%s\" is started.\nNow you can pair it with Bluetooth!\n", device_name.c_str());


if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
        Serial.println("SSD1306 не найден!");
        while (true);
    }
    
    //display.setFont(&Picopixel);
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(3);
    display.setCursor(0, 0);
    display.println("NavMyBike");
    display.display();









}

void loop() 
{

if (SerialBT.available())  
      {
      message = "";
 
      }
delay(200);

 while (SerialBT.available()) 
        {
           message += (char)SerialBT.read();
                new_update = 1 ;
        }
        
 if (new_update == 1 )
  
       {
        // Обрезать всё после \n
      newlineIndex = message.indexOf('\n');
      if (newlineIndex != -1) message = message.substring(0, newlineIndex);

       direction = extractDirection(message);
       range     = extractRange(message);


          display.setCursor(0, 0);
          display.clearDisplay();
          display.display();  
          display.println(direction + " "+ range +" "+ direction  );
          //display.println(message);
          display.display();

       
       Serial.println(message + "   ****   " + direction +" "+range);
       Serial.println(" ");
        message = "";
        new_update = 0;
       }
 
}






String extractDirection(String msg) {
    String lower = msg;
    lower.toLowerCase();
    
if (lower.indexOf("right")    != -1) return "\x1A";
if (lower.indexOf("left")     != -1) return "\x1B";
if (lower.indexOf("straight") != -1) return "\x18";
if (lower.indexOf("head") != -1)     return "\x18";
if (lower.indexOf("arrive")   != -1) return "[X]";
    return "UNKNOWN";
}



String extractRange(String msg) {
    msg.trim();  // trim на месте
    
    String unit = "";
    int unitIndex = -1;
    
    int kmIndex = msg.lastIndexOf("km");
    int mIndex  = msg.lastIndexOf(" m");
    
    if (kmIndex != -1 && kmIndex > mIndex) {
        unit      = "km";
        unitIndex = kmIndex;
    } else if (mIndex != -1) {
        unit      = "m";
        unitIndex = mIndex + 1;
    }
    
    if (unitIndex == -1) return "UNKNOWN";
    
    // Исправлено — trim отдельно
    String before = msg.substring(0, unitIndex);
    before.trim();  // ← отдельной строкой!
    
    int lastSpace = before.lastIndexOf(' ');
    String number = (lastSpace != -1) ? before.substring(lastSpace + 1) : before;
    
    return number + unit;
}



