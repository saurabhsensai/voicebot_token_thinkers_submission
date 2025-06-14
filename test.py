import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from a .env file (optional, for local development)
load_dotenv()

app = Flask(__name__)

# It's highly recommended to set your API key as an environment variable
# for security reasons, rather than hardcoding it.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") 
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@app.route('/')
def index():
    """
    Renders the main chat page.
    """
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles the chat logic. It receives a prompt and chat history from the
    frontend, calls the Gemini API, and returns the AI's response.
    """
    if not GEMINI_API_KEY:
        return jsonify({
            "error": "API key not configured. Please set the GEMINI_API_KEY environment variable."
        }), 500
        
    try:
        data = request.json
        prompt = data.get("prompt")
        chat_history = data.get("history", [])

        if not prompt:
            return jsonify({"error": "Prompt is missing"}), 400

        # Construct the payload for the Gemini API
        # The history is sent to provide context to the model
        payload = {
            "contents": chat_history + [{"role": "user", "parts": [{"text": prompt}]}]
        }

        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make the request to the Gemini API
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        
        # Extract the text from the response
        ai_response_content = result.get("candidates", [{}])[0].get("content", {})
        ai_text = ai_response_content.get("parts", [{}])[0].get("text", "Sorry, I could not get a response.")

        return jsonify({
            "response_text": ai_text,
            "response_content": ai_response_content # Send the full content back to update history
        })

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Failed to communicate with the AI model: {e}"}), 502
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    # Use port 5001 to avoid conflicts with other common services
    app.run(debug=True, port=5001)
