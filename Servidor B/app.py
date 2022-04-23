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
# file_path = 'Arduino_code'


@app.route('/github-webhook', methods=["POST"])
def land():
    print("\nLlego un github webhook\n")
    print()
    tree_sha = "7ba231fed19a0879ea90e00d0a459a2511d64ff7"
    files = github_read_file(username, repository_name, tree_sha, github_token)
    requests.post('http://192.168.4.2:5000/github-webhook', json = files)
    return "Done"

# def github_read_file(username, repository_name, file_path, github_token=None):
def github_read_file(username, repository_name, tree_sha, github_token=None):
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
        
    url = f'https://api.github.com/repos/{username}/{repository_name}/git/trees/{tree_sha}?recursive=1'

    # url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{file_path}'
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    # Agregando los bytes correspondientes al contenido real de los archivos y su codificacion
    for file in data['tree']:
        if file['type'] == 'blob':
            print("\nObteniendo archivo: " + file['path'])
            path = file['path']
            url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{path}'
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            file_data = r.json()
            file['content'] = file_data['content']
            file['encoding'] = file_data['encoding']

    return {"files" : data['tree']}
    
if __name__ == "__main__":
    app.run(host='192.168.0.2', port=16000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
    github_token = os.environ.get('GITHUB_TOKEN')
