# CI/CD en proyectos con microcontroladores
Este sistema es el resultado de mi tesis de Licenciatura de Informática, Facultad de Informática, UNLP. Hecho bajo la supervisión del director Tinetti, Fernando G.

Para explicarlo de forma breve, el sistema consiste en un servidor Python, el cual se va a encargar de comunicarse con diferentes agentes para intentar automatizar algunas partes del desarrollo, en aquellos trabajos que se hagan sobre microcontroladores.
Si se configura correctamente, el servidor debe ser capaz de encargarse del proceso de build (compilación del código y creación del binario), test y deploy. Este proceso automatizado, si bien se puede cambiar, se realiza cada vez que un programador sube código al repositorio.

## Requerimientos
- Python: se requiere instalar python para ejecutar el servidor.
- Más de 1 microcontrolador (recomendado): el sistema, de base, viene preparado para trabajar con 2 microcontroladores. Uno sobre el que va a hacer el testing, y otro, considerado de producción, en donde va a subir el binario ya testeado. En caso de no poseer 2 dispositivos, se puede utilizar uno solo, en donde se llevarán a cabo las dos acciones (test y deploy). Aclaración: por defecto, se asume que los microcontroladores corresponden al ESP32, pero se puede personalizar para utilizar otros.
![image](https://user-images.githubusercontent.com/50599731/204010080-38ca1da6-49f8-4647-b46e-f8f41e7c74ab.png)
- Conexión WiFi (o similares): como el método de actualización de los dispositivos es mediante OTA, es necesario que los mismos puedan comunicarse con el servidor mediante alguna red. Lo más común es utilizar una red WiFi WLAN, pero también se pueden utilizar redes móviles u otras alternativas. Además, el servidor debe tener la posibilidad de comunicarse con GitHub, por lo que necesita acceso a Internet.
- ArduinoIDE: como se detallará en la próxima sección, se deben subir a los microcontroladores una primera versión del programa que habilite el uso de OTA, por lo que se recomienda hacerlo con el IDE de Arduino mediante cable, pero se puede usar una manera alternativa si lo considera adecuado.
- ArduinoCLI: para realizar parte del proceso de build, se va a utilizar la línea de comandos de Arduino, ArduinoCLI.

## Configuración
### Configurando microcontroladores
Como se nombró anteriormente, por default, este sistema trabaja con 2 microcontroladores ESP32. Antes de comenzar con el resto de configuraciones, primero se debe subir a los microcontroladores un código capaz de soportar las actualizaciones OTA. Se recomienda hacerlo con el IDE de Arduino. Para ello se debe abrir, con este IDE, el archivo "otaesp.ino", contenido en el directorio "Arduino_code/otaesp". Una vez abierto el archivo, teniendo conectado el ESP mediante cable, se debe presiona el botón "Subir" en la parte superior del IDE, y con ello comenzará el proceso de actualización. Cuando finalice la actualización, podrá ver el servidor web cargado en el ESP en funcionamiento, accediendo a los endpoints que tiene disponibles ("/" y "/version"). Repetir el proceso con el segundo microcontrolador. Recordar que es necesario configurar ArduinoIDE para que reconozca el ESP32. Acá una guía de Espressif, el diseñador de estos microcontroladores: https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html
Si esa guía no resulta suficiente, puede buscar más información en las sección de errores.

Comentar que al subir el código "otaesp.ino" a los microcontroladores se les asigna automáticamente una IP a cada uno. Esta IP se puede ver monitoreando su salida con la opción "Monitor Serie" de Arduino. Es importante que las IP de los microcontroladores coincidan con las que están indicadas en las variables del servidor:

![image](https://user-images.githubusercontent.com/50599731/204021239-fe21ea9e-78c3-4488-9e91-d03812044e46.png)
En la variable ipDesarrollo debe ir IP del microcontrolador de testeo y en ipProducción la IP del microcontrolador de producción. En caso de disponer con un solo dispositivo, escribir la misma IP en ambas variables.

### Configurando servidor
Finalizada la configuración de los ESP, se debe configurar el servidor. Como ya se comentó, se debe tener instalado Python (https://www.python.org/downloads). El proyecto tiene 3 dependencias, la librería "bcrypt", "flask" y "requests". Se las puede instalar de manera tradicional o, como es usual, haciendo uso de administrador de paquetes de Python, pip, escribiendo en consola el siguiente comando:
```
pip install -r requirements.txt
```

Con las dependencias instaladas, ya se debería poder ejecutar el servidor. Para ello, ejecutar en consola (situada en el directorio "Server") el siguiente comando:
```
python app.py
```
Debería ver el siguiente mensaje en consola, advirtiendo que el servidor está en funcionamiento:

![image](https://user-images.githubusercontent.com/50599731/204010672-59b5e26c-df84-4fbd-be89-a4ef3f3d78bf.png)

Como se puede observar, técnicamente el servidor corresponde a un servidor web desarrollado sobre Flask.

Sin embargo, esto no significa que el sistema está listo para su uso, todavía hay que configurar 2 cosas más.

### Configurando ArduinoCLI
Como se comentó, una de las herramientas que necesitamos para compilar y crear una nueva build es ArduinoCLI (https://github.com/arduino/arduino-cli).
Una vez instalado, mediante consola, se debe configurar para que trabaje con el microcontrolador que se utilice en el sistema, por defecto el ESP32. Para ello, utilizamos los siguientes comandos:
```
arduino-cli core update-index
arduino-cli core install esp32:esp32
```
El primer comando actualiza la lista de placas de Arduino, y el segundo le indica que instale la correspondiente al ESP32. Si usted está utilizando otro microcontrolador, debería reemplazar el texto "esp32:esp32" por el de su placa. Para listar las placas aceptadas por Arduino, y así buscar el código de la suya, puede utilizar el comando:
```
arduino-cli board list --timeout 10s
```
Además de cambiar la placa en el comando anterior, debe incluir el tipo de placa dentro de las variables globales del servidor. En el caso del ESP32:

![image](https://user-images.githubusercontent.com/50599731/204021446-6a80bf95-1b43-440f-bf9d-dc19f183b36f.png)

Ya que se utilizará posteriormente en el comando que compila el código y crea el archivo binario:

![image](https://user-images.githubusercontent.com/50599731/204021553-e92a5589-d46c-4e6c-b56f-29fba5621fcc.png)

### Configurando integración con GitHub
Se va a hacer uso de 2 herramientas que provee GitHub, pero antes deben ser configuradas correctamente.
Primero, se va a configurar la API, que es la aplicación que se utilizará para obtener el nuevo código cada vez que el desarrollador suba una actualización al repositorio. Para ello, se debe crear un token personal, el cual se utilizará como autenticación a la hora de comunicarse. Para crear el token, se debe seguir los siguientes pasos:
- Acceder a perfil, clickeando el círculo con la imagen del usuario en la parte superior derecha de la pantalla, y luego, en el menú desplegable, la opción "Settings" (https://github.com/settings/profile).
- Dentro del perfil, en el menú listado del lado izquierdo, se debe ir a la última de las opciones, "Developer settings". 
- Presionar la tercer opción, "Personal Access Token", y luego "Tokens (classic)" (https://github.com/settings/tokens).
- Una vez en la sección de tokens, presionar "Generate new token" y elegir "Generate new token (classic)".
- Al generar el token, se puede configurar el alcance del mismo y el tiempo de expiración. Se recomienda dar acceso a los repositorios y los proyectos (tildar opción "repo" y "project").

Una vez generado el token, por cuestiones de seguridad, no se incluye en el código del servidor, sino que éste lo obtiene mediante las variables de entorno. En el caso de Windows, para setear una variable de entorno con el valor del token, se utiliza el siguiente comando en la Powershell:
```
SET github_token=tokendegithub
```
Por último, dentro de las variables globales del servidor, es necesario indicar el nombre de usuario de GitHub y el nombre del repositorio:

![image](https://user-images.githubusercontent.com/50599731/204021874-4e624167-6955-42a0-8f2b-ffb9997e18f9.png)

Con todos estos pasos, ya debería poder utilizarse la API de GitHub. Quedaría pendiente la configuración de los Webhooks.

Cada vez que el desarrollador suba nuevo contenido al repositorio, GitHub enviará un webhook (pedido HTTP POST) al servidor, y el servidor se encargará de poner en marcha el sistema de CI/CD. Por defecto, los webhooks se enviarán con cualquier push en el repositorio, pero se puede configurar, por ejemplo, para que sea en una rama específica. Para ello, hay que preparar el webhook según la necesidad que se tenga.
Para configurar un webhook es necesario:
- Ir a “Settings” dentro el repositorio del proyecto
- Dentro del menú desplegado a la izquierda, en la sección de “Code and automation”.
- Presionar el botón que dice “Webhooks”. Al presionar esa opción, se listan los webhooks que tengamos configurados.
- En caso de no tener ninguno se puede presionar “Add webhook”, lo que abre una ventana que permite configurar uno nuevo. 

El webhook solicita la dirección URL con la que se debe comunicar ("payload URL") y permite elegir las condiciones a cumplir para enviar el pedido HTTP. La dirección que se le debe proveer es la siguiente: "http://" + dirección IP de la computadora sobre la que se esté ejecutando el servidor + ":" + puerto seleccionado para la aplicación + "/github-webhook". Por ejemplo: "http://1.1.1.1:16000/github-webhook"

Para obtener la dirección IP de la computadora, en el caso de una computadora personal, se puede realizar de diferentes maneras. Una forma fácil es mediante páginas online, como https://www.cual-es-mi-ip.net/ (consultado el 11/11/2022). Para que la IP a la que envíe GitHub el webhook se corresponda con la del servidor, es necesario configurar un Port Forwarding, cuya configuración depende de cada proveedor de Internet. En el caso de Fibertel, se debe acceder el router y tiene una sección de Port Forwarding en donde se pueden asociar fácilmente la IP + puerto de la computadora, supongamos "1.1.1.1:16000", con la del servidor, "192.168.0.121:16000". La IP del servidor puede ser modificada en el propio código Python:

![image](https://user-images.githubusercontent.com/50599731/204017226-725ddf5e-e00c-4e3f-bef6-53eaa1ae9b72.png)


## Errores
### Arduino no detecta el ESP32
Recordar que para utilizar un microcontrolador en ArduinoIDE es necesario configurarlo. Al menos en el caso del ESP32, hay que seguir los pasos descritos a continuación.
Primero es necesario incluir al ESP a las tarjetas de ArduinoIDE, para ello vamos a:
- Archivo
- Preferencias
- En el campo "Gestor de URLs adicionales de tarjetas" agregamos el siguiente enlace: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

Luego se debe instalar la tarjeta, siguiendo las siguientes indicaciones:
- Seleccionamos "Herramientas"
- Placa
- Gestor de tarjetas
- En el buscador escribimos "ESP32"
- Buscamos la creada por Espressif Systems y seleccionamos "instalar"

Una vez instalada la placa, debemos seleccionarla:
- Seleccionamos "Herramientas" nuevamente
- Placa
- Dentro del menú que se extiende, seleccionamos una que corresponda al ESP32, por ejemplo "ESP32 Dev Module".

Para esta placa en particular, hay que setear la "Upload speed" en "115200". Lo cual se puede realizar yendo a:
- Herramientas
- Upload speed
- Y en el menú desplegable seleccionar "115200"

### Arduino no detecta los puertos del ESP32
Para realizar las actualizaciones mediante cable, Arduino se comunica con los puertos identificados como "COMx", con x un número, generalmente del 1 al 10 (por ejemplo: COM3). En ciertas situaciones, hay puertos por los cuales no se puede realizar la actualización, problema que se soluciona cambiando de puerto, pero aquí viene el problema. Algunas veces Arduino solo reconoce 1 puerto, por lo que no se puede cambiar a otro para realizar la actualización. En mi propia experiencia, esto ocurre porque la computadora no detecta correctamente al ESP, lo cual se soluciona instalando los siguientes drivers:
https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads
Después de instalar correctamente los drivers, aparecerán en Arduino los diferentes puertos del ESP, y ahí se podrá cambiar el puerto para realizar la actualización.

### Cuota de uso de la API de GitHub alcanzado
Se puede encontrar en la situación de que GitHub no le permita utilizar la API porque alcanzó el límite de usos, los cuales se reinician al pasar de unas cuantas horas. Este problema no debería ocurrir, ya que el límite es muy amplio, generalmente el error viene por un problema en la autenticación. 
Puede pasar que el servidor no haya podido leer correctamente la variable de entorno correspondiente al token del usuario. En ese caso, enviará los pedidos a la API  sin autenticación, lo cual está permitido, pero la comunicación sin autenticación tiene una cuota de uso mucho menor. En un uso normal, de todas maneras, no debería representar un problema, pero si se da un uso intensivo puede ocurrir que se alcance la cuota y se genere el error comentado previamente.
Para solucionarlo, asegurarse de configurar correctamente, como ya se explicó, la variable de entorno correspondiente al token de GitHub. Si el servidor lee la variable, hará los pedidos a la API con una autenticación correcta, lo que aumentará ampliamente la cuota de uso.
