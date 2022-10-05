import json
import time
from flask import Flask
import requests, os
import base64
import requests
import os
import hashlib
from test import test

app = Flask(__name__)

github_token = os.environ.get('github_token')
username = 'alejosanti'
repository_name = 'ESProject'
file_path = ''
placa = "esp32:esp32:nodemcu-32s"
estado_test = 'Sin realizar'
ipDesarrollo = '192.168.0.206'
ipProduccion = '192.168.0.151'

@app.route('/github-webhook', methods=["POST"])
def atender_webhook():
    """
    Atiende los webhook que realiza git al subir código al repositorio
    """

    print("\nLlego un github webhook\n")

    # Leyendo archivos de GitHub
    files = github_read_file()
    
    # Copiando los archivos localmente
    write_files_localy(files)
    
    # Creando binario 
    create_binary_file()

    try:
        print("\nSubiendo al ESP de testeo...")
        upload_to_ESP(ipDesarrollo)

        print("\nComenzando el testeo: ")
        test_new_firmware()

        if(estado_test == "Everything is ok"):
            estado = "Test correcto"
            print("\nSubiendo a produccion...")
            upload_to_ESP(ipProduccion)
        else:
            estado = "Test fallido"
            print("\n" + estado)
            return json.dumps({'state':'Test fallido'}), 200, {'ContentType':'application/json'} 

        return json.dumps({'state':'Ok'}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        print(e)
        print("\nHubo un problema subiendo o testeando el firmware")
        return json.dumps({'state':'Error'}), 200, {'ContentType':'application/json'} 
    
def github_read_file():
    """
    Guarda en un json los archivos del ESP (como el .ino o cualquier .h) y su información, los que están contenidos en el directorio "Arduino_code"
    """

    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
    
    # Obteniendo el código sha del directorio (necesario para pedir los archivos que contiene)
    url = f'https://api.github.com/repos/{username}/{repository_name}/contents'
    root = requests.get(url, headers=headers).json()
    tree_sha = list(filter(lambda file: file['path'] == "Arduino_code" , root))[0]['sha']

    # Pidiendo listado de archivos
    url = f'https://api.github.com/repos/{username}/{repository_name}/git/trees/{tree_sha}?recursive=1'
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    # Pidiendo el contenido de los archivos
    for file in data['tree']:
        if file['type'] == 'blob': # blob son los archivos con contenido (no directorios)
            print("\nObteniendo archivo: " + file['path'])
            path = "Arduino_code/" + file['path']
            url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{path}'
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            file_data = r.json()
            file['content'] = file_data['content']
            file['encoding'] = file_data['encoding']

    return data['tree']

def write_files_localy(files):
    """
    A partir de un json con la información de archivos, los escribe localmente en el directorio "CodeFromGithub"
    """

    for file in files:
        if file['type'] == 'blob':
            # Decodificando contenido
            file_content = file['content']
            file_content_encoding = file['encoding']
            if file_content_encoding == 'base64':
                try:
                    file_content = base64.b64decode(file_content).decode()
                except UnicodeDecodeError:
                    # file_content = file_content.decode(encoding='UTF-8')
                    pass

            # Guardando path del archivo
            file_path = ("CodeFromGithub/" + file['path']).replace("/", os.sep)
            
            # Guardando path del directorio
            dir_path = file_path.split(os.sep)
            dir_path = dir_path[:-1]
            dir_path = os.sep.join(dir_path)
                            
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            print("\nWritting on:")
            print(file_path)
            fileWriter = open(file_path, "w")
            fileWriter.write(file_content)
            fileWriter.close()

def create_binary_file():
    """
    Compila el binario con ArduinoCLI
    """

    try:
        print("\nEmpezando compilacion del ino")
        os.system("arduino-cli compile -b " + placa + " ./CodeFromGithub/otaesp/otaesp.ino -e  --clean")
        print("\nCompilacion del ino finalizada")
    except Exception as e:
        print("\n\n\n\n\n Ocurrió una excepción: \n")
        print(e)

def upload_to_ESP(ip):
    """
    Usando AsyncElegantOTA, sube mediante OTA el binario al ESP indicado en la ip
    """

    # Para cargar el binario hay que hacer un POST con el binario y con su hash MD5
    cwd =  os.getcwd()
    path = cwd + "/CodeFromGithub/otaesp/build/esp32.esp32.nodemcu-32s/otaesp.ino.bin"
    path = path.replace("/", os.sep)
    print("\nBuscando binario en:  " + path)

    binario = open(path, "rb")
    
    md5 = hashlib.md5(binario.read()).hexdigest()
    print("\nHash MD5 del binario: " + md5)

    data = {'filename': 'firmware', 'name': 'firmware', 'MD5': md5} 

    binario.close()

    files = {"file": open(path, "rb")}

    print("\nSubiendo binario al ESP...")
    post_resp = requests.post("http://" + ip + "/update", data=data, files=files)

    time.sleep(5) # Pequeña pausa para esperar que el ESP cargue el binario

    print(post_resp.text)

def test_new_firmware():
    """
    Llama a la función main_test() del archivo test.py
    """

    global estado_test
    estado_test = test.main_test()

if __name__ == "__main__":
    app.run(host='192.168.0.121', port=16000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
    github_token = os.environ.get('GITHUB_TOKEN') 
