import os
from rembg import remove
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import json
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

config_path = './config.json'
login_manager = LoginManager()
db = SQLAlchemy()
app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
login_manager.init_app(app)
db.init_app(app)
upload_folder = app.config.get('UPLOAD_FOLDER')
import model

client = OpenAI(api_key='OPENAI API KEY')


@login_manager.user_loader
def load_user(user_id):
    return model.User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('hello_world'))


@app.route('/')
def hello_world():  # put application's code here
    error = request.args.get('error')
    return render_template('index.html', errors=error)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.query(model.User).filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home', email=email))
        else:
            return redirect(url_for('hello_world', error='Invalid email or password'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        user = model.User()
        user.username = username
        user.email = email
        user.password = password

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('hello_world'))


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    message = request.args.get('message')
    return render_template('OpenAI.html', response=message)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    email = current_user.username
    return render_template('home.html', email=email)


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'picture' not in request.files:
        # Handle error case where no file is provided
        return 'No file part in the request', 400

    file = request.files['picture']

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        # Handle error case where file has no filename
        return 'No selected file', 400
        # Create the uploads folder if it doesn't exist
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Save the file to the uploads folder
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Processing the image
    input = Image.open(file_path)

    filename_parts = os.path.splitext(file.filename)
    new_filename = filename_parts[0] + '-rembg' + filename_parts[1]
    output_path = os.path.join(upload_folder, new_filename)
    # Removing the background from the given Image
    output = remove(input)

    # Saving the image in the given path
    output.save(output_path)

    return send_file(output_path, mimetype='image/*', as_attachment=True)


@app.route('/message', methods=['POST'])
@login_required
def message():
    message = request.form.get('message')

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": message},
        ]
    )

    return redirect(url_for('contact'), message=response.choices[0].message)


if __name__ == '__main__':
    app.run()
