 /*
  Important Notice: Star the repository on Github if you like the library! :)
  Repository Link: https://github.com/ayushsharma82/AsyncElegantOTA
*/


#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <AsyncElegantOTA.h>

#include "index.h"

const char* version = "v3.0.0";
const char* ssid = "Fibertel WiFi250 2.4GHz";
const char* password = "00442301230";

AsyncWebServer server(80);


void setup(void) {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/version", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain", version);
  });

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    String s = MAIN_page; 
    request->send(200, "text/html", s);
  });

  AsyncElegantOTA.begin(&server);    // Start AsyncElegantOTA
  server.begin();
  Serial.println("HTTP server started");
}

void loop(void) {
}
