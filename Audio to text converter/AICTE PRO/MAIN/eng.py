from flask import Flask, request, render_template_string, flash, redirect
import os
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Folder to store uploaded files
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template with improved styling
HTML_TEMPLATE = '''
<!doctype html>
<title>Audio to Text Transcription</title>
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        text-align: center;
        padding: 50px;
    }
    h1 {
        color: #4CAF50;
    }
    form {
        margin-top: 20px;
        padding: 20px;
        background-color: #fff;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    input[type="file"] {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    button {
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    button:hover {
        background-color: #45a049;
    }
    .result {
        margin-top: 30px;
        padding: 20px;
        background-color: #fff;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    .error {
        color: red;
    }
</style>

<h1>Audio to Text Transcription</h1>

{% if transcript %}
    <div class="result">
        <h2>Transcribed Text:</h2>
        <p>{{ transcript }}</p>
    </div>
{% endif %}

{% if error %}
    <div class="error">
        <p>{{ error }}</p>
    </div>
{% endif %}

<form method="POST" action="/upload" enctype="multipart/form-data">
    <label for="audio_file">Choose an audio file to upload (Supported formats: .mp3, .wav, .ogg)</label><br><br>
    <input type="file" name="audio_file" accept="audio/*" required><br><br>
    <button type="submit">Upload</button>
</form>

{% if message %}
    <p><strong>{{ message }}</strong></p>
{% endif %}
'''

@app.route('/')
def upload_form():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_file' not in request.files:
        flash("No file part", "error")
        return redirect('/')

    file = request.files['audio_file']
    
    if file.filename == '':
        flash("No selected file", "error")
        return redirect('/')

    if file:
        # Save original file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Convert audio file to WAV if needed
        try:
            audio = AudioSegment.from_file(file_path)
            wav_path = file_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format="wav")
        except Exception as e:
            flash(f"Audio conversion failed: {e}", "error")
            return redirect('/')

        # Transcribe the audio using Google Web Speech API
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                transcript = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                transcript = "Sorry, I could not understand the audio."
            except sr.RequestError:
                transcript = "Sorry, I could not request results from the recognition service."

        return render_template_string(HTML_TEMPLATE, transcript=transcript)

if __name__ == '__main__':
    app.run(  host='0.0.0.0', port=8080,debug=True)
