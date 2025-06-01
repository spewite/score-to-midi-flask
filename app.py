from flask import Flask, current_app, request, jsonify, send_from_directory
import os
from os.path import join
from werkzeug.utils import secure_filename
from flask_cors import CORS
import uuid
from pathlib import Path
from dotenv import load_dotenv
from utils.Exceptions import ScoreQualityError, ScoreStructureError, ScoreTooLargeImageError, MidiNotFound
from utils.validation import validate_file
from utils.config import configure_logging
from utils.email import send_email_notification

# SCRIPTS
from scripts.image_to_midi import image_to_midi

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
configure_logging(app)

CORS(app)

if os.getenv('FLASK_ENV') == 'development':
    CORS(app)
else:
    CORS(app, resources={
        r"/api/upload": {"origins": "https://score-to-midi.com"},
        r"/health": {"origins": "*"}
    })
    

# Setup upload directory configuration
app.config['UPLOAD_FOLDER'] = join(app.root_path, os.getenv('UPLOAD_FOLDER'))
app.config['MIDI_FOLDER'] = join(app.root_path, os.getenv('MIDI_FOLDER'))
app.config['MXL_FOLDER'] = join(app.root_path, os.getenv('MXL_FOLDER'))
app.config['AUDIVERIS_PATH'] = join(app.root_path, os.getenv('AUDIVERIS_PATH'))
app.config['AUDIVERIS_OUTPUT'] = join(app.root_path, os.getenv('AUDIVERIS_OUTPUT'))


# API Routes
@app.route('/health')
def health():
    current_app.logger.info("/health")
    return {'status': 'healthy'}, 200


@app.route("/api/upload", methods = ["POST"])
def upload_file():
  
    current_app.logger.info("/api/upload:")

    if 'file' not in request.files:
        return jsonify({'error': 'No file found in the request. Please, try again.'}), 400

    file = request.files['file']

    if secure_filename(file.filename) == '':
        return jsonify({'error': 'No file found in the request. Please, try again.'}), 400
    
    # Validate the file
    is_valid, error_message = validate_file(file)
    if not is_valid:
        current_app.logger.warning(f"File validation failed: {error_message}")
        return jsonify({'error': error_message}), 400

    current_app.logger.info(f"The file passed all the validations.")


    if file:
        filepath = None
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
            current_app.logger.info(f"File saved: {filepath}")

            # Convert image into MIDI
            midi_path = image_to_midi(filepath, _uuid)
            midi_file = Path(midi_path)

            # Validate if the MIDI exists
            if not midi_file.exists():
                raise 

            # Get the midi files path MIDI
            midi_folder = app.config.get("MIDI_FOLDER")
            midi_dir = join(midi_folder, _uuid)
        
            # Send success email notification
            send_email_notification(
                subject="[🎵 NEW] File Upload Successful",
                body=f"The file '{filename}' was uploaded and processed successfully. MIDI file: {midi_file.name}",
                attachment_path=filepath
            )

            # Build the download URL for the MIDI file
            midi_url = f"{request.host_url.rstrip('/')}/api/download/{_uuid}"
            return jsonify({
                "file_uuid": _uuid,
                "midi_url": midi_url,
                "original_filename": filename,
                "midi_filename": midi_file.name
            }), 200

        except MidiNotFound:
            error_msg = "The server could not find the generated MIDI. Please, try again."
            current_app.logger.error("MidiNotFound exception")
            send_email_notification("[🎵 ERROR] File Upload Failed", error_msg, filepath)
            return jsonify({'error': error_msg}), 400

        except ScoreQualityError:
            error_msg = "Could not read the score. Please, upload the image with higher quality."
            current_app.logger.error("ScoreQualityError exception")
            send_email_notification("[🎵 ERROR] File Upload Failed", error_msg, filepath)
            return jsonify({'error': error_msg}), 400

        except ScoreStructureError:
            error_msg = "Could not parse the score. Please, check if the structure of the score is correct."
            current_app.logger.error("ScoreStructureError exception")
            send_email_notification("[🎵 ERROR] File Upload Failed", error_msg, filepath)
            return jsonify({'error': error_msg}), 400

        except ScoreTooLargeImageError:
            error_msg = "The uploaded image was too large. Please, upload a smaller image."
            current_app.logger.error("ScoreTooLargeImageError exception")
            send_email_notification("[🎵 ERROR] File Upload Failed", error_msg, filepath)
            return jsonify({'error': error_msg}), 400

        except Exception as exception:
            error_msg = f"There has been an unexpected error in the conversion: {exception}"
            current_app.logger.error(f"General exception: {exception}")
            send_email_notification("[🎵 ERROR] File Upload Failed", error_msg, filepath)
            return jsonify({'error': "There has been an unexpected error in the conversion. Please, try again."}), 500


@app.route('/api/download/<uuid>', methods=['GET'])
def download_midi(uuid):
    """
    Download the MIDI file for a given UUID as an attachment.
    """
    midi_folder = app.config.get("MIDI_FOLDER")
    midi_dir = join(midi_folder, uuid)
    # Find the MIDI file in the directory
    if not os.path.exists(midi_dir):
        return jsonify({'error': 'MIDI file not found.'}), 404
    midi_files = [f for f in os.listdir(midi_dir) if f.lower().endswith('.mid') or f.lower().endswith('.midi')]
    if not midi_files:
        return jsonify({'error': 'MIDI file not found.'}), 404
    midi_file = midi_files[0]  # Assume only one MIDI per upload
    return send_from_directory(
        directory=midi_dir,
        path=midi_file,
        as_attachment=True,
        download_name=midi_file
    )

if __name__ == '__main__':
    # Solo para desarrollo
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        # Configuración básica para pruebas de producción locales
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))