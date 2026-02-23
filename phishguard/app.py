import os
import joblib
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "models", "phishguard_model.pkl")
model = joblib.load(model_path)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    url = request.form.get("url")

    if not url:
        return render_template("result.html", result="⚠ Invalid URL", probability=0, url="")

    try:
        from utils.feature_extraction import extract_features

        features = extract_features(url)
        features = np.array(features).reshape(1, -1)

        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][prediction] * 100)

        result = "🚨 Phishing Website Detected" if prediction == 1 else "✅ Legitimate Website"

        return render_template(
            "result.html",
            result=result,
            probability=round(probability, 2),
            url=url
        )

    except Exception:
        return render_template("result.html", result="❌ Error", probability=0, url="")


# Required for Vercel
def handler(request, context):
    return app(request.environ, lambda status, headers: None)
