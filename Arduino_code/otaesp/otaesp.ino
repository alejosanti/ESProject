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
  WiFiClientSecure client;

  const char* test_root_ca= "-----BEGIN CERTIFICATE-----\n" \
                            "MIIF2TCCA8GgAwIBAgIUPB+zAfZLXWgj0OR6DX0WNJsEZY0wDQYJKoZIhvcNAQEL\n" \
                            "BQAwfDELMAkGA1UEBhMCQVIxFDASBgNVBAgMC0J1ZW5vc0FpcmVzMREwDwYDVQQH\n" \
                            "DAhMYSBQbGF0YTEOMAwGA1UECgwFQWxlam8xDjAMBgNVBAsMBUFsZWpvMQ4wDAYD\n" \
                            "VQQDDAVBbGVqbzEUMBIGCSqGSIb3DQEJARYFQWxlam8wHhcNMjIwODIzMTU0MzUz\n" \
                            "WhcNMjMwODIzMTU0MzUzWjB8MQswCQYDVQQGEwJBUjEUMBIGA1UECAwLQnVlbm9z\n" \
                            "QWlyZXMxETAPBgNVBAcMCExhIFBsYXRhMQ4wDAYDVQQKDAVBbGVqbzEOMAwGA1UE\n" \
                            "CwwFQWxlam8xDjAMBgNVBAMMBUFsZWpvMRQwEgYJKoZIhvcNAQkBFgVBbGVqbzCC\n" \
                            "AiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKQe/+DoxBRolGgNaCziG2wy\n" \
                            "zzH/1HKg6wDXUy6Dm3s8wu5Z4QM3n+4G8PMd7ZxwCvF89m+QaSNuGoDzYXVwKOx8\n" \
                            "sFok9IIKvBX62M4wMUjjSjrmzXdlsWsgTlFdkJQkC113mjBhnmqWPL749Mu42ARo\n" \
                            "u3B4wnbXvaeW+EP4tYCj1kga9CmUNYUyv9+VnqklCaAdMV33xW8cfRbhUc/+mDvU\n" \
                            "Iwbi88b/mo5mznwF+te7n8bXeMHzW2MBNugdv+uvMjtI09nKa3V8iqbmch6ePj8h\n" \
                            "Y3ezhVQHukaxjCN8qNomE1E5TflPq0qDo1AzfcXM+iPBz929PIozqIUKYrC/jB7c\n" \
                            "vS0OmSAowMnwHP8dhuJPtY4FjX7+iNCUz9dKUNEkDSXMxuH0+tBo+zF0mlnr3Rlr\n" \
                            "dnkJDgNh0NfroZFeJoDLsOM9yiesnYVXMIOxPr3dnZ6feR9FjCxOZ2ne2Fm4M68r\n" \
                            "7PPs04Km+1NlU1dJTjguGbeFYk7CHcyabs+7sn8SekoclNkegmhBBX4vuIDhVj1E\n" \
                            "0k+XmO678sdRWFJ00iTJUQ0Bh24HutVwl5VjTajWZu09MyJ12y40uKeIjqwhj9SX\n" \
                            "hqYz912/K++tSnmJzZA6bpSlonp9NiL2xV/BDVjm/bFF3KgN8O/FuC51VdlOipvA\n" \
                            "SymAjp8rcIsPNPQ0EJwDAgMBAAGjUzBRMB0GA1UdDgQWBBT19rqdLsg7EJiD35kn\n" \
                            "9UreIKD/BjAfBgNVHSMEGDAWgBT19rqdLsg7EJiD35kn9UreIKD/BjAPBgNVHRMB\n" \
                            "Af8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4ICAQB9EacC2JuSBG20pLsg2UI8Gy6t\n" \
                            "mudNfO7SkdyDUGHEVJm4sRvUYVFFwQdBQPgW9stG8DwrkZ5K/AfxRcZf+dXFz5px\n" \
                            "h6MAAv9WwmqUThtG/aHQF4a/T1WPXyb6s8UIkRR84JP4hAOhohYl9y49W6wE1P85\n" \
                            "FNFCRR10Ds/rGgNE6g+Z6JZnkr7HpoFJ46b89rumV1qkLoNzJDuMUu1wMI8q2cuc\n" \
                            "mGHcsVZChwN70NgtFqskbuyDYH2vDBHyb1/IbiG8fmmQa7sf2CbtZyIC18vy7Tib\n" \
                            "DiNsQhOUW8iMNF6+SDZn4NWCbXsxfzxAliXmtrba63CqvJBS4780t3+dUKF8mTp5\n" \
                            "DTaFV2BQw1mf5uNFFodmOJlbmRLiD7rFVpersNCHEADL7sHjGVvKMBHguTrcRcBT\n" \
                            "OZGvyal26yPkCUHiom7YXVzdPoLfGYkCQF2xK/9uIOOhaauUnfW+htUzIAi86s35\n" \
                            "JaA//C0ZYfAR52viPsXtdZlVs+yGspqWlCuj2Afy1pb1B4xBmKlvqtjmYJ5Kyqpk\n" \
                            "xLHa6Jpugk8V7vDLuMr8mlSHEZNIEWYLXvauyb0NpQLFV5MemTNQs69s7j+U6I1p\n" \
                            "KV3c519kNjUsFxj1/HwsEkZbk9oT12pUXjccXuM8nCe7nk2lSGFkpFq2GtW2xLLa\n" \
                            "PRiKfLSBZQX9b0xM4g==\n" \
                            "-----END CERTIFICATE-----\n";
                            
  client.setCACert(test_root_ca); 
 

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
  t_httpUpdate_return ret = httpUpdate.update(client, "https://192.168.0.3:16000/static/uploads/firmware.bin"); 
  
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
