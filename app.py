# This file sets up a Flask web application for mushroom recognition. It includes routes for user authentication, 
# image upload and prediction, and database interaction.

from flask import Flask, g, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os
from recognizer import predict, load_model
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging
from models import Base, User, Image  
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

config.bcrypt.init_app(app)
logging.basicConfig(level=logging.DEBUG)

engine = config.engine
model = load_model()
class_names = ['Agaricus', 'Amanita', 'Boletus', 'Cortinarius', 'Entoloma', 'Hygrocybe', 'Lactarius', 'Russula', 'Suillus']

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

# Home route: renders the home page
@app.route('/')
def home():
    return render_template('home.html')

# Uploads route: serves uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# Signin route: handles user registration
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            error_message = 'User already exists.Please '
            redirect_link = url_for("login")
            link = "log in"
            return render_template('error.html', error_message=error_message, redirect_link=redirect_link, link=link), 400
        
        hashed_password = config.bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.add(new_user)

        try:
            db.commit()
            session['username'] = username  
            return redirect(url_for('recognizer')), 201
        except Exception as e:
            db.rollback()
            error_message = f"Error registering user: {e}"
            return render_template('error.html', error_message=error_message), 500
    
    return render_template('signin.html')

# Login route: handles user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        
        user = db.query(User).filter_by(username=username).first()
        if user:
            if config.bcrypt.check_password_hash(user.password, password):
                session['username'] = username 
                return redirect(url_for('recognizer'))
            else:
                error_message = "Invalid password. Please try again."
                return render_template('error.html', error_message=error_message)
        else:
            error_message = "User does not exist. Please "
            redirect_link = url_for("signin")
            link = "sign in"
            return render_template('error.html', error_message=error_message, redirect_link=redirect_link, link=link)
    
    return render_template('login.html')

# Recognizer route: handles image upload and prediction
@app.route('/recognizer', methods=['GET', 'POST'])
def recognizer():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('recognizer.html')
    elif request.method == 'POST':
        if 'files' not in request.files:
            return jsonify({'error': 'No file part'})
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No selected files'})
        
        predictions = []
        confidences = []
        db = get_db()
        user = db.query(User).filter_by(username=session['username']).first()

        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            prediction, confidence = predict(filepath, class_names)
            predictions.append(prediction)
            confidences.append(confidence)
            new_image = Image(filename=filename, prediction=prediction, confidence=confidence, user=user)
            db.add(new_image)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({'error': f"Error saving image details: {e}"}), 500
        
        return jsonify({'predictions': predictions, 'confidences': confidences})

# Get analyzed images route: retrieves analyzed images for the logged-in user
@app.route('/get_analyzed_images')
def get_analyzed_images():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    db = get_db()
    user = db.query(User).filter_by(username=session['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    images = db.query(Image).filter_by(user_id=user.id).all()
    image_data = [{'filename': image.filename, 'prediction': image.prediction, 'confidence': image.confidence} for image in images]

    return jsonify({'images': image_data})

# Check DB route: checks the database connection
@app.route('/check_db')
def check_db():
    try:
        db = get_db()
        db.execute(text('SELECT 1'))
        return "Database connection is working!", 200
    except Exception as e:
        return f"Database connection failed: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)