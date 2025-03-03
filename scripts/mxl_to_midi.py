from music21 import converter
from pathlib import Path
from os.path import join
import os
from flask import current_app

def mxl_to_midi(mxl_path, _uuid): 

  """
    Converts a MXL file into a MIDI file.

    Args:
      mxl_path: Path to the input MXL.
      _uuid: Unique upload identifier

    Returns:
      The path of the generated MIDI file. 
  
  """

  current_app.logger.info("\n\nStarting mxl_to_midi()...")

  midi_output_dir = join(current_app.config.get("MIDI_FOLDER"), _uuid)
  os.makedirs(midi_output_dir)

  # Check if the file exists
  mxl_file = Path(mxl_path)

  if not mxl_file.exists(): 
    raise FileNotFoundError(f'{mxl_path} does not exist.')

  # Load the XML file
  current_app.logger.info("Parsing the MXL file: ", mxl_path)
  score = converter.parse(mxl_path)

  # Save the MIDI file
  current_app.logger.info("Saving the MIDI file.")
  mxl_filename_base = mxl_file.stem
  midi_file_path = join(midi_output_dir, f'{mxl_filename_base}.midi')
  score.write('midi', fp=midi_file_path)
    
  current_app.logger.info("Midi file saved in: ", midi_file_path)
  current_app.logger.info("Finished mxl_to_midi() successfully...")
  return midi_file_path