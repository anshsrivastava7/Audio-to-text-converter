from flask import Flask, request, render_template, flash, redirect
import os
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Folder to store uploaded files
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def upload_form():
    return render_template("index.html")


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

        return render_template("index.html", transcript=transcript)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
