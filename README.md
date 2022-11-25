# CI/CD en proyectos con microcontroladores
Este sistema es el resultado de mi tesis para la Licenciatura de Informática, UNLP. Hecho bajo la supervisión del director Tinetti, Fernando G.
En resumen, consiste en un servidor Python, el cual se va a encargar de comunicarse con diferentes agentes para intentar automatizar diferentes partes del desarrollo.
Si se configura correctamente, el servidor debe ser capaz de encargarse del proceso de build (compilación del código y creación del binario), test y deploy. El trigger de este proceso automatizado, a priori, es un push sobre el repositorio, pero se puede personalizar.

## Requerimientos
- Python: se requiere instalar python para ejecutar el servidor.
- Más de 1 microcontrolador: el sistema, de base, viene preparado para trabajar con 2 microcontroladores. Uno sobre el que va a hacer el testing, y otro, considerado de producción, en donde va a subir el binario ya testeado. Aclaración: por defecto, se asume que los microcontroladores corresponden al ESP32, pero también se puede personalizar. ![image](https://user-images.githubusercontent.com/50599731/204010080-38ca1da6-49f8-4647-b46e-f8f41e7c74ab.png)
- Conexión WiFi (o similares): como el método de actualización de los dispositivos es mediante OTA, es necesario que los mismos puedan comunicarse con el servidor mediante alguna red. La más común es una red WiFi WLAN, pero se pueden combinar con las redes móviles u otras alternativas. Además, el servidor debe tener la posibilidad de comunicarse con GitHub, por lo que necesita acceso a Internet.
- ArduinoIDE: como se detallará en la próxima sección, se deben subir a los microcontroladores una primera versión del programa que habilite el uso de OTA, por lo que se recomienda hacerlo con el IDE de Arduino mediante cable, pero se puede usar una manera alternativa si lo considera adecuado.
- ArduinoCLI: para realizar parte del proceso de build, se va a utilizar la línea de comandos de Arduino, ArduinoCLI.

## Configuración
### Configurando microcontroladores
Como se nombró anteriormente, por default, este sistema trabaja con 2 microcontroladores ESP32. Antes de comenzar con el resto de configuraciones, primero se debe subir a los microcontroladores un código capaz de soportar las actualizaciones OTA. Se recomienda hacerlo con el IDE de Arduino. Para ello se debe abrir, con este IDE, el archivo "otaesp.ino", contenido en el directorio "Arduino_code/otaesp". Una vez abierto el archivo, teniendo conectado el ESP mediante cable, se debe presiona el botón "Subir" en la parte superior del IDE, y con ello comenzará el proceso de actualización. Cuando finalice la actualización, podrá ver el servidor web cargado en el ESP en funcionamiento, accediendo a los endpoints que tiene disponible ("/" y "/version"). Repetir el proceso con el segundo microcontrolador. Recordar que es necesario configurar ArduinoIDE para que reconozca el ESP32. Acá una guia de Espressif, el diseñador de estos microcontroladores: https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html

### Configurando servidor
Finalizada la configuración de los ESP, se debe configurar el servidor. Como ya se comentó, se debe tener instalado Python (https://www.python.org/downloads). El proyecto tiene 3 dependiencias, la librería "bcrypt", "flask" y "requests". Se las puede instalar de manera tradicional o, como es usual, hacer uso de pip, escribiendo en consola el siguiente comando:
```
pip install -r requirements.txt
```

Con las dependencias instaladas, ya se debería poder ejecutar el servidor. Para ello, ejecutar en consola (situada en el directorio "Server") el siguiente comando:
```
python app.py
```
Debería observar el siguiente mensaje en consola, advirtiendo que el servidor está en funcionamiento:
![image](https://user-images.githubusercontent.com/50599731/204010672-59b5e26c-df84-4fbd-be89-a4ef3f3d78bf.png)
Como se puede observar, técnicamente es un servidor web desarrollado sobre Flask.

Sin embargo, esto no significa que el sistema está listo para su uso, todavía tenemos que configurar 2 cosas más.

### Configurando ArduinoCLI
Como se comentó, una de las herramientas que necesitamos para compilar y crear una nueva build es ArduinoCLI (https://github.com/arduino/arduino-cli).
Una vez instalado, mediante consola, se debe configurar para que trabaje con el microcontrolador que se utilice en el sistema, en este caso el ESP32. Para ello, utilizamos los siguientes comandos:
```
arduino-cli core update-index
arduino-cli core install esp32:esp32
```
El primer comando actualiza la lista con las placas que soporta, y el segundo le indica que instale la correspondiente al ESP32. Si usted está utilizando otro microcontrolador, debería reemplazar el texto "esp32:esp32" por el de su placa, el cual lo puede encontrar utilizando el comando:
```
arduino-cli board list --timeout 10s
```
### Configurando integración con GitHub
Se va a hacer uso de 2 herramientas que provee GitHub, y deben ser configuradas correctamente.
Primero, se va a configurar la API, que es la aplicación que se utilizará para obtener el nuevo código cada vez que el desarrollador suba una actualización al repositorio. Para ello, se debe crear un token personal, el cual se utilizará como autenticación a la hora de comunicarse con la API. Para crear el token, se debe seguir los siguientes pasos:
- Acceder a perfil, clickeando el círculo con la imagen del usuario en la parte superior derecha de la pantalla, y luego, en el menú desplegable, la opción "Settings" (https://github.com/settings/profile).
- Dentro del perfil, en el menú listado del lado izquierdo, se debe ir a la última de las opciones, "Developer settings". 
- Presionar la tercer opción, "Personal Access Token", y luego "Tokens (classic)" (https://github.com/settings/tokens).
- Una vez en la sección de tokens, presionar "Generate new token" y elegir "Generate new token (classic)".
- Al generar el token, se puede configurar el alcance del mismo y el tiempo de expiración. Se recomienda dar acceso a los repositorios y los proyectos (tildar opción "repo" y "project").

Una vez generado el token, por cuestiones de seguridad, no se incluye en el código del servidor, sino que este lo obtiene mediante las variables de entorno. En el caso de Windows, para setear una variable de entorno, con el valor del token, se utiliza el siguiente comando en la Powershell:
```
SET github_token=tokendegithub
```
Con todos estos pasos, ya debería poder utilizarse la API de GitHub. Quedaría pendiente la configuración de los Webhooks.

Cada vez que el desarrollador suba nuevo contenido al repositorio, GitHub enviará un webhook (pedido HTTP POST) al servidor, y sistema se encargará de subir la nueva versión al ESP de producción, creando una build y testeando el código. Por default, este mecanismo se activa con cualquier push en el respositorio, pero se puede configurar, por ejemplo, para que sea en una rama específica. Para ello, hay que configurar el webhook según la necesidad que se tenga.
Para configurar un webhook es necesario:
- Ir a “Settings” dentro el repositorio del proyecto
- Dentro del menú desplegado a la izquierda, en la sección de “Code and automation”.
- Presional el botón que dice “Webhooks”. Al presionar esa opción, se listan los webhooks que tengamos configurados.
- En caso de no tener ninguno se puede presionar “Add webhook”, lo que abre una ventana que permite configurar uno nuevo. 

El webhook solicita la dirección URL con la que se debe comunicar ("payload URL") y permite elegir las condiciones a cumplir para enviar el pedido http. La dirección que se le debe proveer es la siguiente: "http://" + dirección ip de la computadora sobre la que se esté ejecutando el servidor + ":" + puerto seleccionado para la aplicación + "/github-webhook". Por ejemplo: "http://1.1.1.1:16000/github-webhook"

Para obtener la dirección ip de la computadora, en el caso de una computadora personal, se puede realizar de diferentes maneras. Una forma fácil es mediante páginas online, como https://www.cual-es-mi-ip.net/ (consultado el 11/11/2022). Para que la ip a la que envíe GitHub el webhook se corresponda con la del servidor, es necesario configurar un Port Forwarding, cuya configuración depende de cada proveedor de Internet. En el caso de Fibertel, se debe acceder el router y tiene una sección de Port Forwarding en donde se pueden asociar fácilmente la ip + puerto de la computadora, supongamos "1.1.1.1:16000", con la del servidor, "192.168.0.121:16000". La ip del servidor puede ser modificada en el propio código Python:
![image](https://user-images.githubusercontent.com/50599731/204017226-725ddf5e-e00c-4e3f-bef6-53eaa1ae9b72.png)


Instalar drivers
https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads
Explicar que puede haber un error con la api si no se pone bien la autenticación


Hay que configurar las ip's de cada ESP, el de producción y el de desarrollo o testing. Ambas se muestran por el monitor cuando se carga el código por primera vez.

Como ya se nombró, es necesario que GitHub notifique los cambios en el repositorio mediante los webhooks. Para configurar un webhook es necesario ir a “Settings” en el repositorio del proyecto, y dentro del menú desplegado a la izquierda, en la sección de “Code and automation”, aparece el botón que dice “Webhooks”. Al presionar esa opción, se listan los webhooks que tengamos configurados, en caso de no tener ninguno se puede presionar “Add webhook”, lo que abre una ventana que permite configurar uno nuevo. El webhook solicita la dirección URL a la que se debe comunicar y da la opción de configurar cuándo debe hacerlo, en el caso de este trabajo lo hará siempre que haya un push sobre el repositorio.

En una computadora personal, si va a ser quien corra el módulo de control, primero es necesario obtener la dirección IP, lo cual se puede realizar de diferentes maneras, una forma es mediante páginas online, como https://www.cual-es-mi-ip.net/ (consultado el 11/11/2022). Una vez obtenida la IP, es necesario elegir el puerto al que se va a comunicar, supongamos el 16000. Esa dirección + puerto es lo que se le tiene que brindar al webhook que se configura en GitHub. Dependiendo del proveedor de internet, es probable que sea necesario acceder al router y habilitar el Port Forwarding, conectando la dirección que ingresamos en el webhook, que es a la que se comunica GitHub, con la que posee el módulo de control (se puede encontrar el su código). Por último, al menos en el sistema operativo Windows, lo más probable es que sea necesario crear una excepción en el Firewall, para que no se rechace el pedido de GitHub.



