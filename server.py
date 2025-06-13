from flask import Flask, render_template, request, jsonify
from googletrans import Translator
import logging

app = Flask(__name__)
translator = Translator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'auto')
        
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        # Detect language if auto
        if source_lang == 'auto':
            detected = translator.detect(text)
            source_lang = detected.lang
            confidence = detected.confidence
            logger.info(f"Detected language: {source_lang} (confidence: {confidence})")
        
        # Translate to English
        if source_lang == 'en':
            translated_text = text
            logger.info("Text is already in English")
        else:
            result = translator.translate(text, src=source_lang, dest='en')
            translated_text = result.text
            logger.info(f"Translated from {source_lang} to English")
        
        return jsonify({
            'original_text': text,
            'translated_text': translated_text,
            'source_language': source_lang,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'multilingual-stt'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)