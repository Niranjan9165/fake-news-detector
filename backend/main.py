from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import re
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Create FastAPI app
app = FastAPI(title="Fake News Detector API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load our trained AI model
with open("../models/fake_news_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("../models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

# Your News API key
NEWS_API_KEY = "9a67294dd7f14fcea752bbcbc3e34056"

print("AI Model loaded successfully!")

# Define input
class NewsInput(BaseModel):
    text: str

# Clean text function
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if w not in stop_words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w) for w in words]
    return " ".join(words)

# Get related news from internet
def get_related_news(query):
    try:
        # Take first 5 words as search query
        search_query = " ".join(query.split()[:5])
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": search_query,
            "apiKey": NEWS_API_KEY,
            "pageSize": 3,
            "language": "en",
            "sortBy": "relevancy"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "ok" and data["totalResults"] > 0:
            articles = []
            for article in data["articles"][:3]:
                articles.append({
                    "title": article["title"],
                    "source": article["source"]["name"],
                    "url": article["url"]
                })
            return articles
        return []
    except:
        return []

# Home route
@app.get("/")
def home():
    return {
        "message": "Fake News Detector API is running!",
        "status": "active"
    }

# Prediction route
@app.post("/predict")
def predict(news: NewsInput):
    # Clean the text
    cleaned = clean_text(news.text)
    
    # Convert to numbers
    text_tfidf = vectorizer.transform([cleaned])
    
    # Get prediction
    prediction = model.predict(text_tfidf)[0]
    probability = model.predict_proba(text_tfidf)[0]
    confidence = round(max(probability) * 100, 2)
    
    # Get related news from internet
    related_news = get_related_news(news.text)
    
    # Return result
    return {
        "prediction": prediction,
        "confidence": confidence,
        "message": "Likely FAKE news!" if prediction == "FAKE" else "Appears to be REAL news!",
        "related_news": related_news
    }