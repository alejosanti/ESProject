import datetime
import json
import time
from flask import Flask, render_template
from flask_pymongo import PyMongo
import requests, os
import base64
import requests
import os
import hashlib
from test import test

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['bin'])


app = Flask(__name__)
app.secret_key = "otawebapp"
app.config['MONGO_URI']='mongodb://localhost:27017/otadata'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

github_token = os.environ.get('github_token')
username = 'alejosanti'
repository_name = 'ESProject'
file_path = ''
placa = "esp32:esp32:nodemcu-32s"
estado_test = 'Sin realizar'

@app.route('/github-webhook', methods=["POST"])
def atender_webhook():
    print("\nLlego un github webhook\n")

    # Leyendo archivos de GitHub
    files = github_read_file()
    
    # Escribiendo archivos localmente
    write_files_localy(files)
    
    # Creando binario
    create_binary_file()

    # Cargando binario al ESP
    estado = upload_to_ESP()
    
    # Testeando
    if(estado == "Ok"):
        test_new_firmware()
        if(estado_test == "Everything is ok"):
            estado = "Test correcto"
        else:
            estado = "Test fallido"
        print("\n" + estado)


    return json.dumps({'state':estado}), 200, {'ContentType':'application/json'} 
    
def github_read_file():
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
    
    # Obteniendo el sha del directorio
    url = f'https://api.github.com/repos/{username}/{repository_name}/contents'
    root = requests.get(url, headers=headers).json()
    tree_sha = list(filter(lambda file: file['path'] == "Arduino_code" , root))[0]['sha']

    url = f'https://api.github.com/repos/{username}/{repository_name}/git/trees/{tree_sha}?recursive=1'

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    # Agregando el contenido real de los archivos y su codificacion
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
    try:
        print("\nEmpezando compilacion del ino")
        os.system("arduino-cli compile -b " + placa + " ./CodeFromGithub/otaesp/otaesp.ino -e  --clean")
        print("\nCompilacion del ino finalizada")

        # Guardando archivo en un lugar alcanzable por el ESP
        cwd =  os.getcwd()
        path = cwd + "/CodeFromGithub/otaesp/build/esp32.esp32.nodemcu-32s/otaesp.ino.bin"
        path = path.replace("/", os.sep)
        binario_content = open(path, "rb").read()

        newBinPath = os.path.join(app.config['UPLOAD_FOLDER'], 'firmware.bin')
        newBinFile = open(newBinPath, "wb")
        newBinFile.write(binario_content)
        print("\nBinario guardado...")

    except Exception as e:
        print("\n\n\n\n\n Ocurrió una excepción: \n")
        print(e)

def upload_to_ESP():
    print("\nCargando binario al ESP...")

    # Para cargar el binario hay que hacer un POST con el binario y con su hash MD5
    cwd =  os.getcwd()
    path = cwd + "/CodeFromGithub/otaesp/build/esp32.esp32.nodemcu-32s/otaesp.ino.bin"
    path = path.replace("/", os.sep)
    print("\nBuscando binario en:  " + path)

    binario = open(path, "rb")
    
    # files = {'firmware': binario}
    
    # binarySize = os.path.getsize(path)
    # print("El tamaño del binario es: " + str(binarySize))

    md5 = hashlib.md5(binario.read()).hexdigest()
    print("\nHash MD5 del binario: " + md5)

    data = {'filename': 'firmware', 'name': 'firmware', 'MD5': md5} 

    binario.close()

    files = {"file": open(r"C:/Users/Ale/OneDrive/Escritorio/Facultad/Tesis/PD/ESPCI/ESProject/Servidor B/CodeFromGithub/otaesp/build/esp32.esp32.nodemcu-32s/otaesp.ino.bin", "rb")}

    post_resp = requests.post("http://192.168.0.206/update", data=data, files=files)

    print(post_resp.text)

def test_new_firmware():
    estado_test = test.main_test()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(host='192.168.0.3', port=16000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
    github_token = os.environ.get('GITHUB_TOKEN') 
