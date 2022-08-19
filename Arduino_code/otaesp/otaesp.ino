#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include "index.h"

/*
 * usuario y contrasenia par ala conexion al ESP en modo AP
 */
const char* ssid = "ESP32_AP";
const char* password = "123456789";
const char* version = "v3.0.1";
bool updateIsOk = true;

/*
 * Declaramos objeto de la libreria WebServer
 */
 
WebServer server(80);

void update_started() {
  Serial.println("CALLBACK:  HTTP update process started");
}
 
void update_finished() {
  Serial.println("CALLBACK:  HTTP update process finished");
}
 
void update_progress(int cur, int total) {
  Serial.printf("CALLBACK:  HTTP update process at %d of %d bytes...\n", cur, total);
}
 
void update_error(int err) {
  Serial.printf("CALLBACK:  HTTP update fatal error code %d\n", err);
}

/*
 * funcion encargada de realizar el upload
 */ 
void UpdateFile(){
  WiFiClient client;

  /* 
    The line below is optional. It can be used to blink the LED on the board during flashing
    The LED will be on during download of one buffer of data from the network. The LED will
    be off during writing that buffer to flash
    On a good connection the LED should flash regularly. On a bad connection the LED will be
    on much longer than it will be off. Other pins than LED_BUILTIN may be used. The second
    value is used to put the LED on. If the LED is on with HIGH, that value should be passed
  */
  httpUpdate.setLedPin(LED_BUILTIN, LOW);

  // Add optional callback notifiers
  httpUpdate.onStart(update_started);
  httpUpdate.onEnd(update_finished);
  httpUpdate.onProgress(update_progress);
  httpUpdate.onError(update_error);

  // Se configura la libreria para que la actualizacion del firmware no reinicie el ESP
  httpUpdate.rebootOnUpdate(false);

  Serial.println(F("Update start now!"));
  t_httpUpdate_return ret = httpUpdate.update(client, "http://192.168.0.3:16000/get-binary-file"); 
  
    switch (ret) {
      case HTTP_UPDATE_FAILED:
        Serial.printf("HTTP_UPDATE_FAILED Error (%d): %s\n", httpUpdate.getLastError(), httpUpdate.getLastErrorString().c_str());
        updateIsOk = false;
        break;

      case HTTP_UPDATE_NO_UPDATES:
        Serial.println("HTTP_UPDATE_NO_UPDATES");
        updateIsOk = false;
        break;

      case HTTP_UPDATE_OK:
        Serial.println("HTTP_UPDATE_OK");
        break;
    }
}

void SetupServer() { 
  /*
   * Manejo del endpoint '/version' para subir el archivo
   */
  server.on("/version", HTTP_GET, [](){
    server.sendHeader("Connection", "close");
    server.send(200,"text/plain",version);
  });

  /*
   * Manejo del endpoint '/update' para subir el archivo
   */
  server.on("/update", HTTP_GET, []() {
    UpdateFile();
    Serial.println();
    if(updateIsOk){
      server.send(200, "text/plain", String("update success"));
      EspClass ESP;
      ESP.restart();
    } else {
      server.send(408, "text/plain", String("update failed"));
    }
  });

  server.on("/index", HTTP_GET, [](){
    String s = MAIN_page; 
    server.send(200, "text/html", s);
  });

}

void setup(void) {

  Serial.begin(115200);

  /*
   * Se configura el ESP32 como Access Point
   */

  delay(10);
  Serial.print("Seteando WiFi en modo Access Point");
  WiFi.mode(WIFI_AP);
  while(!WiFi.softAP(ssid, password))
  {
   Serial.println(".");
    delay(100);
  }

  Serial.print("Iniciado AP ");
  Serial.println(ssid);
  Serial.print("IP address:\t");
  Serial.println(WiFi.softAPIP());

  SetupServer();

  server.begin();
  

}

void loop() {

  server.handleClient();

}
