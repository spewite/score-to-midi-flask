from scripts.mxl_to_midi import mxl_to_midi
from scripts.image_to_mxl import image_to_mxl
import traceback


def image_to_midi(image_path, _uuid): 

  """
    Converts a IMAGE file into a MIDI file.

    Flow: 
      IMAGE -> MXL (usign Audiveris) -> MIDI (using music21)  

    Args: 
      image_path: Path to the PNG file.
      _uuid: Unique upload identifier

    Returns:
      The path of the generated midi file

  """

  try: 

    xml_path = image_to_mxl(image_path, _uuid)
    midi_path = mxl_to_midi(xml_path, _uuid)
    return midi_path

  except Exception as e:
    tb = traceback.extract_tb(e.__traceback__)
    function_name = tb[-1].name
    print(f"Error in {function_name}: {e}")
    raise e
