from flask import Flask, request, jsonify
import os
from modules.asr_module import transcribe_audio

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Voicebot Chat</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chat-container { max-width: 600px; margin: auto; }
            #transcription { margin-top: 10px; padding: 10px; border: 1px solid #ccc; min-height: 50px; }
            #recordButton { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div id="chat-container">
            <h2>Voicebot Chat</h2>
            <button id="recordButton">🎤 Record</button>
            <div id="transcription">Your speech will appear here...</div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/recorderjs/recorder.min.js"></script>
        <script>
            let recorder;
            let audioContext;

            document.getElementById("recordButton").addEventListener("click", function() {
                if (!recorder) {
                    audioContext = new AudioContext();
                    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                        const input = audioContext.createMediaStreamSource(stream);
                        recorder = new Recorder(input);
                        recorder.record();
                        this.textContent = "⏹ Stop";
                    }).catch(err => console.error("Error accessing microphone:", err));
                } else {
                    recorder.stop();
                    recorder.exportWAV(function(blob) {
                        sendAudioToServer(blob);
                    });
                    recorder = null;
                    this.textContent = "🎤 Record";
                }
            });

            function sendAudioToServer(blob) {
                const formData = new FormData();
                formData.append("audio", blob, "recording.wav");
                fetch("/transcribe", {
                    method: "POST",
                    body: formData
                }).then(response => response.json()).then(data => {
                    document.getElementById("transcription").textContent = data.transcription;
                }).catch(err => console.error("Error sending audio:", err));
            }
        </script>
    </body>
    </html>
    """

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Receive audio from the client, transcribe it, and return the text."""
    audio_file = request.files["audio"]
    temp_path = "temp_audio.wav"
    audio_file.save(temp_path)
    transcription = transcribe_audio(temp_path)
    os.remove(temp_path)
    return jsonify({"transcription": transcription})

if __name__ == "__main__":
    app.run(debug=True)