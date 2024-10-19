from flask import Flask, g, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from recognizer import predict, load_model
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from flask_bcrypt import Bcrypt
import logging

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

engine = create_engine('mysql://root:SOLpo90567&%@127.0.0.1:3306/MushroomDB')

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }

def get_db():
    if 'db' not in g:
        g.db = sessionmaker(bind=engine)()
    return g.db

@app.teardown_appcontext
def shutdown_session(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

Base.metadata.create_all(engine)

app.config['UPLOAD_FOLDER'] = 'uploads/'

model = load_model()
class_names = ['Agaricus', 'Amanita', 'Boletus', 'Cortinarius', 'Entoloma', 'Hygrocybe', 'Lactarius', 'Russula', 'Suillus']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signin', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        
        # Check if user already exists
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            error_message = "User already exists. Please log in."
            return render_template('error.html', error_message=error_message), 400
        
        # Encrypt the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(username=username, password=hashed_password)
        db.add(new_user)
        try:
            db.commit()
            return redirect(url_for('recognizer')), 201
        except Exception as e:
            db.rollback()
            error_message = f"Error registering user: {e}"
            return render_template('error.html', error_message=error_message), 500
    
    return render_template('signin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        
        # Check if user exists
        user = db.query(User).filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return redirect(url_for('recognizer')), 200
        else:
            error_message = "Invalid username or password."
            return render_template('error.html', error_message=error_message), 400
    
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
    
#for DB
@app.route('/check_db')
def check_db():
    try:
        db = get_db()
        db.execute(text('SELECT 1'))
        return "Database connection is working!", 200
    except Exception as e:
        return f"Database connection failed: {e}", 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)