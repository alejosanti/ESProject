# ESProject
Este sistema integra las prácticas de CI/CD en proyectos con microcontroladores

## Requerimientos
instalar python

instalar mongo

Dentro del repositorio
pip install -r requirements.txt

SET github_token=tokendegithub

Configurar Arduino IDE para que soporte el ESP32
https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html

Instalar drivers
https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads

Instalar Arduino CLI
arduino-cli core update-index
arduino-cli core install esp32:esp32 (esp32:esp32 corresponde al microcontrolador ESP32, puede variar según el microcontrolador que se utilice)

Hay que configurar las ip's de cada ESP, el de producción y el de desarrollo o testing. Ambas se muestran por el monitor cuando se carga el código por primera vez.
