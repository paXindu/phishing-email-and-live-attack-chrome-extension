# server.py

import re
import nltk
from nltk.corpus import stopwords
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from backend import xss, sql ,csrf

app = Flask(__name__)
CORS(app)

spam_model = joblib.load('spam_model.pkl')
spam_vectorizer = joblib.load('spam_vectorizer.pkl')

nltk.download('stopwords')

def preprocess_message(message):
    message = re.sub(r'http\S+|www.\S+', '', message)
    message = re.sub(r'\S+@\S+', '', message)
    message = re.sub(r'[^\w\s]', '', message)
    message = message.lower()
    stop_words = set(stopwords.words('english'))
    message = ' '.join(word for word in message.split() if word not in stop_words)
    return message

@app.route('/predict/spam', methods=['POST'])
def predict_spam():
    message = request.data.decode('utf-8')
    message = preprocess_message(message)
    print(message)
    message_vectorized = spam_vectorizer.transform([message])
    prediction_proba = spam_model.predict_proba(message_vectorized)[0]
    prediction = spam_model.predict(message_vectorized)[0]
    response = {
        'prediction': prediction,
        'prediction_percentage': max(prediction_proba) * 100
    }
    return jsonify(response)

@app.route('/predict/phishing', methods=['POST'])
def predict_phishing():
    phishing_model = joblib.load('logistic_regression_model.joblib')
    phishing_vectorizer = joblib.load('tfidf_vectorizer.joblib')
    url_data = request.get_json()
    url_list = url_data.get('urls', [])
    predictions = []
    for url in url_list:
        url_vector = phishing_vectorizer.transform([url])
        prediction = phishing_model.predict(url_vector)[0]
        predictions.append(prediction)
    response = {'predictions': predictions}
    return jsonify(response)

@app.route('/scan/xss', methods=['POST'])
def scan_xss():
    data = request.get_json()
    url = data['url']
    result = xss.xss_scan(url)
    return jsonify({'result': result})

@app.route('/scan/sql', methods=['POST'])
def scan_sql():
    data = request.get_json()
    url = data['url']
    result = sql.scan_sql_injection(url)
    return jsonify({'result': result})

@app.route('/scan/csrf', methods=['POST'])
def scan_csrf():
    data = request.get_json()
    url = data['url']
    
    # Check for CSRF vulnerability
    result = csrf.check_csrf_vulnerability(url)
    
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
