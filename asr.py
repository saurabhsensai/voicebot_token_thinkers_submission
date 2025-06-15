from flask import Flask, render_template, request, jsonify
from google.cloud import speech_v1p1beta1 as speech
import os
import io

app = Flask(__name__)


if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
    print("Please set it to the path of your Google Cloud service account key file.")

@app.route('/')
def index():
    """
    Renders the main HTML page for the speech-to-text application.
    """
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Receives audio data, sends it to Google Speech-to-Text API,
    and returns the transcribed text.
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_content = audio_file.read()

    try:
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code='en-US',  # You can change this to your desired language
            enable_automatic_punctuation=True, # Enable automatic punctuation for better readability
        )

        audio = speech.RecognitionAudio(content=audio_content)

        # Perform the synchronous speech recognition
        response = client.recognize(config=config, audio=audio)

        transcript = ""
        for result in response.results:
            # The first alternative is usually the most confident one.
            transcript += result.alternatives[0].transcript + " "

        return jsonify({'transcript': transcript.strip()})

    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)