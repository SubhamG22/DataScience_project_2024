from flask import Flask, render_template, redirect, url_for, request, session, flash
from markupsafe import Markup
import pickle , requests
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
from FILES.fertilizer import fertilizer_dic
from FILES.disease import disease_dic
from PIL import Image
import torch
import io, os
from FILES.model import ResNet9
from torchvision import transforms



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Loading plant disease classification model

disease_classes = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy']

disease_model_path = 'DataScience_project_2024\Models\plant-disease-model.pth'
disease_model = ResNet9(3, len(disease_classes))
disease_model.load_state_dict(torch.load(disease_model_path, map_location=torch.device('cpu'), weights_only=True))

# disease_model.load_state_dict(torch.load(disease_model_path, map_location=torch.device('cpu')))
# if os.path.exists(disease_model_path):
#     try:
#         disease_model.load_state_dict(torch.load(disease_model_path, map_location=torch.device('cpu')))
#         print("Model loaded successfully.")
#     except Exception as e:
#         print(f"Error loading the model: {e}")
# else:
#     print(f"Model file not found at {disease_model_path}")
disease_model.eval()

# Loading crop recommendation model

crop_recommendation_model_path = 'DataScience_project_2024\Models\RandomForest.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))

# Simulated user database
user_db = {}


def weather_fetch(city_name):
    """
    Fetches and returns the temperature and humidity of a city.
    
    :param city_name: Name of the city.
    :return: temperature, humidity
    """
    api_key = "9d7cde1f6d07ec55650544be1631307e"  # Correctly assign the API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Construct the complete URL with the city name and API key
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name

    # Send the request to OpenWeatherMap API
    response = requests.get(complete_url)
    data = response.json()

    # Check if the response is valid and city is found
    if data["cod"] != "404":
        main_data = data["main"]

        # Convert temperature from Kelvin to Celsius and round it to 2 decimals
        temperature = round(main_data["temp"] - 273.15, 2)
        humidity = main_data["humidity"]
        return temperature,humidity
        # Print temperature and humidity
        #print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
    else:
        # print("City not found.")
        return None
    
def predict_image(img, model=disease_model):
    """
    Transforms image to tensor and predicts disease label
    :params: image
    :return: prediction (string)
    """
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    # Get predictions from model
    yb = model(img_u)
    # Pick index with highest probability
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds[0].item()]
    # Retrieve the class label
    return prediction




        

@app.route('/')
def home():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('landing.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Logic for handling login
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = users_db.get(email)
#         if user and check_password_hash(user['password'], password):
#             session['user'] = email
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid email or password', 'danger')
#             return redirect(url_for('login'))

#     return render_template('login.html')




# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']

#         if password != confirm_password:
#             flash('Passwords do not match!', 'danger')
#             return redirect(url_for('signup'))

#         if email in users_db:
#             flash('Email already exists!', 'danger')
#             return redirect(url_for('login'))

#         users_db[email] = {
#             'email': email,
#             'password': generate_password_hash(password)
#         }
#         flash('Signup successful! Please login.', 'success')
#         return redirect(url_for('login'))

#     return render_template('signup.html')

# Route to handle signup form submission
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the email already exists
        if email in user_db:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('login'))

        # Store the user credentials in the database
        user_db[email] = password
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template("login.html")

# Route to handle signin form submission
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email not in user_db:
            flash('Email not found. Please sign up.', 'danger')
            return redirect(url_for('login'))
        
        # Check if email and password are correct
        if email in user_db and user_db[email] == password:
            session['user'] = email  # Set session to keep the user logged in
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        # If login fails, show an danger message
        flash('Invalid email or password. Please try again.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', email=session['user'])
    else:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    

@app.route('/crop_recommend',  methods=['POST','GET'])
def crop_recommend():
    if request.method == 'POST':
        city = request.form.get("city")
        rainfall = float(request.form['rainfall'])
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        

        # state = request.form.get("stt")
       

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop_result.html', prediction=final_prediction)

        else:

            return render_template('crop_recommend.html', prediction="none")
    return render_template('crop_recommend.html')

@app.route('/ferti_suggest', methods=['POST','GET'])
def ferti_suggest():
    if request.method=="POST":
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        crop_name = str(request.form['cropname'])
        # ph = float(request.form['ph'])

        df = pd.read_csv('DataScience_project_2024\FILES\FertilizerData.csv')

        nr = df[df['Crop'] == crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == crop_name]['K'].iloc[0]

        n = nr - N
        p = pr - P
        k = kr - K
        temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
        max_value = temp[max(temp.keys())]
        if max_value == "N":
            if n < 0:
                key = 'NHigh'
            else:
                key = "Nlow"
        elif max_value == "P":
            if p < 0:
                key = 'PHigh'
            else:
                key = "Plow"
        else:
            if k < 0:
                key = 'KHigh'
            else:
                key = "Klow"

        response = Markup(str(fertilizer_dic[key]))

        flash("Wow","success")
        return render_template('fertiliser_result.html', prediction=response)
    return render_template('ferti_suggest.html')



@app.route('/disease_identify', methods=['POST', 'GET'])
def disease_identify():
     
    if request.method == 'POST':
        
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files.get('file')
        
        if not file:
            return render_template('disease_identify.html')
        
        try:
            # Read the file contents
            img = file.read()
            
            # Call the prediction function
            prediction_result = predict_image(img)
            
            # Get the predicted disease description
            prediction = Markup(str(disease_dic[prediction_result]))
            
            return render_template('disease_result.html', prediction=prediction)
        
        except Exception as e:
            # Print the error for debugging purposes
            print(f"Error occurred: {e}")
            return render_template('disease_identify.html', prediction="An error occurred while processing the image.")
    
    # Default GET request response
    return render_template('disease_identify.html')















@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)
