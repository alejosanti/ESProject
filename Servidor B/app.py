import json
from urllib import request
from flask import Flask
from flask_pymongo import PyMongo
import requests, os
import base64
import requests
import os

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "otawebapp"
app.config['MONGO_URI']='mongodb://localhost:27017/otadata'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

github_token = os.environ.get('github_token')
username = 'alejosanti'
repository_name = 'ESProject'
file_path = ''
tree_sha = '7ba231fed19a0879ea90e00d0a459a2511d64ff7' # Configurar con la api de github, depende de cada repositorio
placa = "esp32:esp32:nodemcu-32s"


@app.route('/github-webhook', methods=["POST"])
def atender_webhook():
    print("\nLlego un github webhook\n")

    # Leyendo archivos de GitHub
    files = github_read_file(username, repository_name, tree_sha, github_token)
    
    # Escribiendo archivos localmente
    write_files_localy(files)
    
    # Creando binario
    create_binary_file()

    # Subiendo binarios
    upload_binary_file()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def github_read_file(username, repository_name, tree_sha, github_token=None):
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
        
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
                file_content = base64.b64decode(file_content).decode()
            
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
        os.system("arduino-cli compile -b " + placa + " ./CodeFromGithub/otaesp/otaesp.ino -e")
        print("\nCompilacion del ino finalizada")
    except Exception as e:
        print("\n\n\n\n\n Ocurrió una excepción: \n")
        print(e)

def upload_binary_file():
    """ 
        Datos necesarios para subir a GitHub:
            En la ruta: 
                -owner --> username
                -repo --> repository_name
                -path --> gitPath
            En el encabezado:
                -Authorization --> github_token
            En el cuerpo:
                -message --> mensaje de commit
                -content --> contenido del binario en base64
                -sha --> codigo sha del archivo a reemplazar (se obtiene en https://api.github.com/repos/alejosanti/ESProject/contents/Binaries/otaesp.ino.bin)
    """
    # Datos del header
    headers = {}
    if os.environ.get('github_token'):
        headers['Authorization'] = f"token {github_token}"
        headers['Content-Type'] = "application/json"
    
    # Datos de la ruta
    gitPath = "Binaries/otaesp.ino.bin"

    url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{gitPath}'

    # Datos del cuerpo
    cwd =  os.getcwd()
    path = cwd + "/CodeFromGithub/otaesp/build/esp32.esp32.nodemcu-32s/otaesp.ino.bin"
    path = path.replace("/", os.sep)
    print("\nBuscando binario en:  " + path)
    
    
    binario = open(path, "rb").read()
    content = base64.b64encode(binario)
        
    # Buscando sha del archivo binario     
    binary_sha = requests.get(url, headers=headers).json()['sha']

    data = {"message":"Automatic upload of the binary file from Server B", "content":str(content.decode("UTF-8")), "sha":binary_sha}

    # Realizando el PUT para subir el binario
    print('\nSubiendo binario a GitHub...\n')
    r = requests.put(url, json=data, headers=headers)

    print(r.raise_for_status())

if __name__ == "__main__":
    app.run(host='192.168.0.3', port=16000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
    github_token = os.environ.get('GITHUB_TOKEN')
