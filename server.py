import boto3
import json
import base64

# Initialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'  # Replace with your region
)

def transcribe_audio(audio_file_path):
    # Read and encode the audio file
    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        encoded_audio = base64.b64encode(audio_data).decode('utf-8')

    # Prepare the payload for Whisper model
    body = json.dumps({
        "audio": encoded_audio,
        "modelId": "openai.whisper-large-v3-turbo"  # Replace with your model ID
        # Optional parameters: language, task (transcribe/translate), etc.
        # "language": "en",  # Specify if known, e.g., "en" for English
        # "task": "transcribe"  # or "translate" for translation to English
    })

    try:
        # Invoke the model
        response = bedrock.invoke_model(
            modelId='openai.whisper-large-v3-turbo',  # Replace with your model ID
            body=body
        )

        # Parse the response
        result = json.loads(response['body'].read().decode('utf-8'))
        transcription = result.get('text', '')
        return transcription

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Example usage
audio_file = "test.mp3"  # Replace with your audio file path
transcription = transcribe_audio(audio_file)
if transcription:
    print("Transcription:", transcription)
else:
    print("Transcription failed.")