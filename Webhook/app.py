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
file_path = 'Arduino_code/otaesp/otaesp.ino'

@app.route('/github-webhook', methods=["POST"])
def land():
    print("\nLlego un github webhook\n")
    print()
    github_read_file(username, repository_name, file_path, github_token)
    requests.get('http://192.168.4.2:5000/github-webhook')
    return "Done"

def github_read_file(username, repository_name, file_path, github_token=None):
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"
        
    url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{file_path}'
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    file_content = data['content']
    file_content_encoding = data.get('encoding')
    if file_content_encoding == 'base64':
        file_content = base64.b64decode(file_content).decode()

    # data = json.loads(file_content)

    file = open(r"C:/Users/Ale/Desktop/otaesp.ino", "a")
    file.write(file_content)
    file.close()

    return file_content
    
if __name__ == "__main__":
    app.run(host='192.168.0.2', port=16000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
    github_token = os.environ['GITHUB_TOKEN']
