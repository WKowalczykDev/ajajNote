import os
from flask import Flask, request, jsonify
from transform import transform  # Import twojej istniejącej funkcji transform
import config

app = Flask(__name__)

# Konfiguracja ścieżek z ENV (ważne dla Dockera)
BASE_DATA_DIR = os.getenv('DATA_DIR', '/app/data')

@app.route('/process', methods=['POST'])
def process_audio():
    data = request.get_json()
    
    # Backend przekaże nam relatywne ścieżki lub ID
    filename = data.get('filename')
    user_id = data.get('user_id')
    
    if not filename or not user_id:
        return jsonify({'error': 'Missing parameters'}), 400

    # Odtworzenie ścieżek wewnątrz kontenera (takie same jak w backendzie dzięki wolumenowi)
    user_dir = os.path.join(BASE_DATA_DIR, str(user_id))
    input_dir = os.path.join(user_dir, 'uploads')
    transcript_dir = os.path.join(user_dir, 'transcripts')
    note_dir = os.path.join(user_dir, 'notes')

    # Twoja funkcja transform (musi przyjmować te argumenty)
    msg, status = transform(
        input=input_dir,
        transcript_dir=transcript_dir,
        note=note_dir,
        filename=filename
    )

    return jsonify({'message': msg}), status

if __name__ == '__main__':
    # Uruchomienie na porcie 5001
    app.run(host='0.0.0.0', port=5001)
