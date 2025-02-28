import sys
from flask import Flask, logging, request, jsonify, send_from_directory, send_file
import os
from os import listdir, abort
from os.path import isfile, join, exists
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
from pathlib import Path
from dotenv import load_dotenv
from utils.Exceptions import ScoreQualityError, ScoreStructureError, ScoreTooLargeImageError, MidiNotFound
from scripts.cleanup_data import clean_data

# SCRIPTS
from scripts.image_to_midi import image_to_midi

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Disable Debug Mode
app.config["DEBUG"] = False

# Set up logging for production
if not app.debug:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    # If running locally without Gunicorn, set up manual logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)  # Change to DEBUG for more details
    app.logger.addHandler(handler)

# Setup upload directory configuration
app.config['UPLOAD_FOLDER'] = join(app.root_path, os.getenv('UPLOAD_FOLDER'))
app.config['MIDI_FOLDER'] = join(app.root_path, os.getenv('MIDI_FOLDER'))
app.config['MXL_FOLDER'] = join(app.root_path, os.getenv('MXL_FOLDER'))
app.config['AUDIVERIS_PATH'] = join(app.root_path, os.getenv('AUDIVERIS_PATH'))
app.config['AUDIVERIS_OUTPUT'] = join(app.root_path, os.getenv('AUDIVERIS_OUTPUT'))

# API Routes

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

# @app.route("/cleanup")
# def cleanup():
#     print("/cleanup GET")
#     try: 
#         clean_data()
#         return "Data folders cleaned up successfully", 200
#     except Exception as error:
#         return f"There has been an error cleaning the data: {error}", 500
        

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
            midi_path = image_to_midi(filepath, _uuid)
            midi_file = Path(midi_path)

            # Validate if the MIDI exists
            if not midi_file.exists():
                raise 

            # Get the midi files path MIDI
            midi_folder = app.config.get("MIDI_FOLDER")
            midi_dir = join(midi_folder, _uuid)
        
            return send_from_directory(directory=str(midi_dir), path=midi_file.name, as_attachment=True, download_name=midi_file.name), 200
        
        except MidiNotFound:
            return jsonify({'error': "The server could not find the generated MIDI. Please, try again."}), 400

        except ScoreQualityError:
            return jsonify({'error': "Could not read the score. Please, upload the image with higher quality."}), 400

        except ScoreStructureError:
            return jsonify({'error': "Could not parse the score. Please, check if the structure of the score is correct."}), 400

        except ScoreTooLargeImageError:
            return jsonify({'error': "The uploaded image was too large. Please, upload a smaller image"}), 400

        except Exception:
            return jsonify({'error': "There has been an unexpected error in the conversion. Please, try again."}), 500

if __name__ == '__main__':
    # Solo para desarrollo
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        # Configuración básica para pruebas de producción locales
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))