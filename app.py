from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from recognizer import predict, load_model

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads/'

model = load_model()
class_names = ['Agaricus', 'Amanita', 'Boletus', 'Cortinarius', 'Entoloma', 'Hygrocybe', 'Lactarius', 'Russula', 'Suillus']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signin')
def register():
    return render_template('signin.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recognizer', methods=['GET', 'POST'])
def recognizer():
    if request.method == 'GET':
        return render_template('recognizer.html')
    elif request.method == 'POST':
        if 'files' not in request.files:
            return jsonify({'error': 'No file part'})
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No selected files'})
        predictions = []
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            prediction = predict(filepath, class_names)
            predictions.append(prediction)
        return jsonify({'predictions': predictions})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)