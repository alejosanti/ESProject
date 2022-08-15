from flask import Flask, redirect, render_template, request, session, url_for
from flask_pymongo import PyMongo
import datetime, bcrypt, requests, os, time
import base64
import json
import requests
import os

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "otawebapp"
app.config['MONGO_URI']='mongodb://localhost:27017/otadata'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

github_token = ''
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
    # requests.post('http://192.168.4.2:5000/github-webhook', json = files)
    return "Done"

def github_read_file(username, repository_name, tree_sha, github_token=None):
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
        
    url = f'https://api.github.com/repos/{username}/{repository_name}/git/trees/{tree_sha}?recursive=1'

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    # Agregando los bytes correspondientes al contenido real de los archivos y su codificacion
    for file in data['tree']:
        if file['type'] == 'blob': # blob son los archivos con contenido real (no metadatos)
            print("\nObteniendo archivo: " + file['path'])
            path = "Arduino_code/" + file['path']
            url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{path}'
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            file_data = r.json()
            file['content'] = file_data['content']
            file['encoding'] = file_data['encoding']

    return {"files" : data['tree']}

def write_files_localy(files):
    for file in files:
        if file['type'] == 'blob': # Creo que esta comprobacion está obsoleta
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

    # Generando archivo binario
    try:
        print("\nEmpezando compilacion del ino")
        os.system("arduino-cli compile -b " + placa + " ./CodeFromGithub/otaesp/otaesp.ino -e")
        print("\nCompilacion del ino finalizada")
    except Exception as e:
        print("\n\n\n\n\n Ocurrió una excepción: \n")
        print(e)


if __name__ == "__main__":
    app.run(host='192.168.0.3', port=16000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
    github_token = os.environ.get('GITHUB_TOKEN')
