# OmniSched AI - Enterprise Version
# Backend: Flask | Frontend: Lovable JSON (connects via API)

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set your OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# Root route for health check
@app.route('/', methods=['GET'])
def home():
    return "OminiSched AI Backend is Running ✅"

# POST endpoint to generate content calendar
@app.route('/api/generate', methods=['POST'])
def generate_content():
    data = request.json

    brand = data.get('brand')
    industry = data.get('industry')
    audience = data.get('audience')
    tone = data.get('tone')
    platform = data.get('platform')
    goal = data.get('goal')

    prompt = f"""
    You are OmniSched AI – a content strategist.
    Generate a 7-days content calendar for:
    Brand: {brand}
    Industry: {industry}
    Target Audience: {audience}
    Tone: {tone}
    Content Platform: {platform}
    Main Goal: {goal}

    Format:
    7 Days | Content Idea | Format | Hook | CTA
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.0",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        output = response['choices'][0]['message']['content']

        return jsonify({"calendar": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET endpoint for trend-based content (placeholder)
@app.route('/api/trends', methods=['GET'])
def get_trends():
    return jsonify({"trends": ["AI in marketing", "Instagram Reels SEO", "LinkedIn hooks"]})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
