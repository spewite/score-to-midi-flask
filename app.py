from flask import Flask, request, jsonify, send_from_directory, send_file
import os
from os import listdir, abort
from os.path import isfile, join, exists
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
from pathlib import Path
from dotenv import load_dotenv
from utils.Exceptions import ScoreQualityError, ScoreStructureError
from scripts.cleanup_data import clean_data

# SCRIPTS
from scripts.image_to_midi import image_to_midi

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Setup upload directory configuration
app.config['UPLOAD_FOLDER'] = join(app.root_path, os.getenv('UPLOAD_FOLDER'))
app.config['MIDI_FOLDER'] = join(app.root_path, os.getenv('MIDI_FOLDER'))
app.config['MXL_FOLDER'] = join(app.root_path, os.getenv('MXL_FOLDER'))
app.config['AUDIVERIS_PATH'] = join(app.root_path, os.getenv('AUDIVERIS_PATH'))
app.config['AUDIVERIS_OUTPUT'] = join(app.root_path, os.getenv('AUDIVERIS_OUTPUT'))

# API Routes
@app.route("/", methods = ["POST", "GET"])
def hello_world():

  response = jsonify(message="Simple server is running")
  return response

@app.route("/cleanup")
def cleanup():
    print("/cleanup GET")
    try: 
        clean_data()
        return "Data folders cleaned up successfully", 200
    except Exception as error:
        return f"There has been an error cleaning the data: {error}", 500
        

@app.route("/api/upload", methods = ["POST"])
def upload_file():
  
    print("/api/upload: ")

    if 'file' not in request.files:
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if file:

        try:
                
            # Create a UUID to distuinguish the directory.
            _uuid = str(uuid.uuid4())

            # Create the directory to store the image
            file_dir = join(app.config['UPLOAD_FOLDER'], _uuid)

            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

            # Get the file attributes
            filename = secure_filename(file.filename)
            filepath = join(file_dir, filename)
            
            # Save the file in its corresponding directory.
            file.save(filepath)
        
            # Convert image into MIDI
            print(filepath)
            image_to_midi(filepath, _uuid)

            return jsonify({'_uuid': _uuid}), 200
        
        except ScoreQualityError as error:
            return jsonify({'error': "Could not read the score. Upload the image with higher quality."}), 400
        
        except ScoreStructureError as error:
            return jsonify({'error': "Could parse the score. Check if the structure of the score is correct."}), 400

        except Exception as error:
            return jsonify({'error': error}), 500
    

    

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

    # Attempt to send the file
    try:
        return send_from_directory(directory=str(midi_dir), path=midi_file.name, as_attachment=True, download_name=midi_file.name)
        
    except Exception as exc:
        return jsonify({"error": "Server error while sending the file"}), 500

    

if __name__ == '__main__':
    app.run(debug=True) 