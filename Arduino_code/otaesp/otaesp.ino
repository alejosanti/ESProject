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
const char* version = "v3.0.9";
bool updateIsOk = true;

/*
 * Declaramos objeto de la libreria WebServer
 */
 
WebServer server(80);

/*
 * funcion encargada de realizar el upload
 */
void UpdateFile(){
  WiFiClient client;
  /*
   *Se permiten las redirecciones enviadas en el headder para la libreria httpUpdate
   */
  httpUpdate.setFollowRedirects(HTTPC_FORCE_FOLLOW_REDIRECTS);
  /*
   *Se configura la libreria para que la actualizacion del firmware no reinicie el ESP
   */
  httpUpdate.rebootOnUpdate(false);
  /*
   *incia la carga del archivo y si hay un error en la subida o conexion se imprime el error
    Serial.printf("pre");
   */
  t_httpUpdate_return ret = httpUpdate.update(client, "http://192.168.4.2:5000/display/firmware.bin"); 
  
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
