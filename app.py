from flask import Flask, request, jsonify, send_from_directory, send_file
import os
from os import listdir, abort
from os.path import isfile, join, exists
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
from pathlib import Path

app = Flask(__name__)
CORS(app)


# Setup upload directory configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MIDI_FOLDER = 'midi'
app.config['MIDI_FOLDER'] = MIDI_FOLDER


# API Routes
@app.route("/", methods = ["POST", "GET"])
def hello_world():

  response = jsonify(message="Simple server is running")
  return response


@app.route("/api/upload", methods = ["POST"])
def upload_file():
  
    print("/api/upload: ")

    if 'file' not in request.files:
        return jsonify({'error': 'File not found in request'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print("Directory: ", app.config['UPLOAD_FOLDER'])
        print("Path: ", filename)
       
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=filename), 200
    
        # path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # return send_file(path, as_attachment=True)

        # return jsonify({'message': 'Archivo subido exitosamente', 'filename': filename}), 200
    

@app.route("/api/download/<uuid_str>")
def download_midi(uuid_str: str):
    
    # Validate UUID format
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    # Get the configured MIDI folder
    midi_folder = app.config.get("MIDI_FOLDER")
    if not midi_folder:
        return jsonify({"error": "Server misconfiguration"}), 500

    # Build the path to the directory containing MIDI files
    midi_dir = Path(join(midi_folder, uuid_str))
    if not midi_dir.exists():
        return jsonify({"error": "Could not link the UUID with any generated MIDI"}), 404

    # Find MIDI files in the directory
    midi_files = list(midi_dir.glob("*.midi"))
    if not midi_files:
        return jsonify({"error": "Could not find the generated MIDI file"}), 404

    # Pick the first MIDI file found
    midi_file = midi_files[0]

    print(midi_file)

    # Attempt to send the file
    try:
        return send_from_directory(directory=str(midi_dir), path=midi_file.name)
    except Exception as exc:
        app.logger.exception("Failed to send MIDI file: %s", midi_file.name)
        return jsonify({"error": "Server error while sending the file"}), 500

    

if __name__ == '__main__':
    app.run(debug=True) 