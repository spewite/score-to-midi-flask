
from flask import current_app
import os, shutil

def clean_data():
  upload_dir = current_app.config.get("UPLOAD_FOLDER")
  midi_dir = current_app.config.get("MIDI_FOLDER")
  mxl_dir = current_app.config.get("MXL_FOLDER")
  audiveris_dir = current_app.config.get("AUDIVERIS_OUTPUT")

  paths = [upload_dir, midi_dir, mxl_dir, audiveris_dir]

  for path in paths:
    cleanup_directory(path)

def cleanup_directory(dir):
  
  for filename in os.listdir(dir):
      file_path = os.path.join(dir, filename)
      try:
          if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
          elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
      except Exception as e:
          print('Failed to delete %s. Reason: %s' % (file_path, e))
