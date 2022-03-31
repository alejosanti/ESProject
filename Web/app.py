from flask import Flask, redirect, render_template, request, session, url_for
from flask_pymongo import PyMongo
import datetime, bcrypt, requests, os, time

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "otawebapp"
app.config['MONGO_URI']='mongodb://localhost:27017/otadata'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

ALLOWED_EXTENSIONS = set(['bin'])

@app.route('/')
def land():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    message = 'Por favor ingrese a su cuenta.'
    if 'user' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        user_found = mongo.db.ota_users.find_one({'user': user})
        if user_found:
            user_val = user_found['user']
            passwordcheck = user_found['pwd']

            if bcrypt.checkpw(pwd.encode('utf-8'), passwordcheck):
                session['user'] = user_val
                return redirect(url_for('home'))
        else:
            message = 'Usuario o contraseña incorrectos.'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/home')
def home():
    if 'user' in session:
        user = session['user']
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/upload-file')
def upload_file():
    return render_template('update.html')

@app.route('/show-version')
def show_version():
    r = requests.get('http://192.168.4.1/version', timeout = 1)
    version = r.text
    return render_template('version.html', version = version)

@app.route('/show-data', methods=['GET'])
def show_data():
    if 'user' in session:
        data = mongo.db.ota_transactions.find({})
        return render_template('data.html', data=data)
    else:
        return redirect(url_for('login'))

@app.route('/update', methods=['POST'])
def post_data():
    user = session['user']
    binfile = request.files['binfile']
    if binfile and allowed_file(binfile.filename):
        binfile.save(os.path.join(app.config['UPLOAD_FOLDER'], 'firmware.bin'))
        response = requests.get('http://192.168.4.1/update').text
        if(response != "update success"):
            message = 'Upload fallido.'
            return render_template('update.html', message = message)
        else:     
            mongo.save_file(binfile.filename, binfile)

            for i in range(0, 5):  # try 5 times
                print("Ahi va un try")
                try:
                    version = requests.get('http://192.168.4.1/version').text
                except Exception:
                    pass

                if version is None:
                    time.sleep(2)  # wait for 2 seconds before trying to fetch the data again
                else:
                    break
                
            print("Salio del for")
            mongo.db.ota_transactions.insert_one({'date': datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"), 'user': user, 'filename': binfile.filename, 'version': version})
            return redirect(url_for('show_data'))
    else:
        message = 'Tipo de archivo inválido, intente nuevamente.'
        return render_template('update.html', message = message)

@app.route('/display/firmware.bin')
def display_image():
	return redirect(url_for('static', filename='uploads/firmware.bin'))

@app.route('/add-new-user')
def add_new_user():
    return render_template('register.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    message = ''
    if 'user' in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        user = request.form.get('user')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user_found = mongo.db.ota_users.find_one({'user': user})
        if user_found:
            message = 'Ya existe un usuario con ese nombre.'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Las contraseñas no coinciden.'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'user': user, 'pwd': hashed}
            mongo.db.ota_users.insert_one(user_input)
            return render_template('login.html')
    return render_template('register.html')

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if 'user' in session:
        session.pop('user', None)
        return render_template('login.html')
    else:
        message = 'Aún no se ha identificado, por favor ingrese sus datos.'
        return render_template('login.html', message=message)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(host='192.168.4.2', port=5000, debug=True) #La IP declarada es la local, se declara asi y no como 'localhost' porque el ESP no la detecta para hacer el update.
