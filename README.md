# CI/CD en proyectos con microcontroladores
Este sistema es el resultado de mi tesis para la Licenciatura de Informática, UNLP. Hecho bajo la supervisión del director Tinetti, Fernando G.
En resumen, consiste en un servidor Python, el cual se va a encargar de comunicarse con diferentes agentes para intentar automatizar diferentes partes del desarrollo.
Si se configura correctamente, el servidor debe ser capaz de encargarse del proceso de build (compilación del código y creación del binario), test y deploy. El trigger de este proceso automatizado, a priori, es un push sobre el repositorio, pero se puede personalizar.

## Requerimientos
- Python: se requiere instalar python para ejecutar el servidor
- Más de 1 microcontrolador: el sistema, de base, viene preparado para trabajar con 2 microcontroladores. Uno sobre el que va a hacer el testing, y otro, considerado de producción, en donde va a subir el binario ya testeado. Aclaración: por defecto, se asume que los microcontroladores corresponden al ESP32, pero también se puede personalizar. ![image](https://user-images.githubusercontent.com/50599731/204010080-38ca1da6-49f8-4647-b46e-f8f41e7c74ab.png)
- Conexión WiFi (o similares): como el método de actualización de los dispositivos es mediante OTA, es necesario que los mismos puedan comunicarse con el servidor mediante alguna red. La más común es una red WiFi WLAN, pero se pueden combinar con las redes móviles u otras alternativas. Además, el servidor debe tener la posibilidad de comunicarse con GitHub, por lo que necesita acceso a Internet.
- ArduinoIDE: como se detallará en la próxima sección, se deben subir a los microcontroladores una primera versión del programa que habilite el uso de OTA, por lo que se recomienda hacerlo con el IDE de Arduino mediante cable, pero se puede usar una manera alternativa si lo considera adecuado.
- ArduinoCLI: para realizar parte del proceso de build, se va a utilizar la línea de comandos de Arduino, ArduinoCLI.

## Configuración
Como se nombró anteriormente, por default, este sistema trabaja con 2 microcontroladores ESP32. Antes de comenzar con la configuración del servidor, se debe subir a los microcontroladores un código capaz de soportar las actualizaciones OTA. Se recomienda hacerlo con el IDE de Arduino. Para ello se debe abrir, con este IDE, el archivo "otaesp.ino", contenido en el directorio "Arduino_code/otaesp". Una vez abierto el archivo, teniendo conectado el ESP mediante cable, se debe presiona el botón "Subir" en la parte superior del IDE, y con ello comenzará el proceso de actualización. Cuando finalice la actualización, podrá ver el servidor web cargado en el ESP en funcionamiento, accediendo a los endpoints que tiene disponible ("/" y "/version"). Repetir el proceso con el segundo microcontrolador.

Finalizada la configuración de los ESP, se debe configurar el servidor. Como ya se comentó, se debe tener instalado Python. El proyecto tiene 3 dependiencias, la librería "bcrypt", "flask" y "requests". Se las puede instalar de manera tradicional o, como es usual, hacer uso de pip, escribiendo en consola el siguiente comando:
```
pip install -r requirements.txt
```

SET github_token=tokendegithub

Configurar Arduino IDE para que soporte el ESP32
https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html

Instalar drivers
https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads

Instalar Arduino CLI
arduino-cli core update-index
arduino-cli core install esp32:esp32 (esp32:esp32 corresponde al microcontrolador ESP32, puede variar según el microcontrolador que se utilice)

Hay que configurar las ip's de cada ESP, el de producción y el de desarrollo o testing. Ambas se muestran por el monitor cuando se carga el código por primera vez.
