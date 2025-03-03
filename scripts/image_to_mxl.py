import subprocess
import os
from os.path import join
from pathlib import Path
import shutil
from flask import current_app
from scripts.svg_to_png import convert_svg_to_png
from utils.Exceptions import ScoreQualityError, ScoreStructureError, ScoreTooLargeImageError

def image_to_mxl(image_path, _uuid):

    """
    Converts a image file of a musical score to a MXL file using Audiveris.

    Args:
        image_path: Path to the input image.
        _uuid: Unique upload identifier
        
    Returns:
        The path of the generated MXL file. 

    """

    current_app.logger.info("\n\nStarting image_to_mxl()...")

    # Check if the file exists
    image_file = Path(image_path)

    if not image_file.exists(): 
        raise FileNotFoundError(f'{image_path} does not exist.')

    # If the image is a .svg convert into .png
    filename = os.path.splitext(os.path.basename(image_path))[0]
    extension = os.path.splitext(os.path.basename(image_path))[1]

    if extension == '.svg':
        png_path = join(image_file.parent.resolve(), f'{filename}.png')
        convert_svg_to_png(image_path, png_path)
        image_path = png_path
        image_file = Path(png_path)

    # Setup Audiveris
    audiveris_path = current_app.config.get("AUDIVERIS_PATH")

    if not os.path.exists(audiveris_path):
        raise FileNotFoundError(f"Audiveris path not found at: {audiveris_path}")

    # Construct the Audiveris command.
    base_audiveris_dir = current_app.config.get("AUDIVERIS_OUTPUT")
    audiberis_output_dir = os.path.join(base_audiveris_dir, _uuid)
    Path(audiberis_output_dir).mkdir(parents=True, exist_ok=True)

    command = [
      audiveris_path,
      "-batch",
      "-export", 
      "-output",
      audiberis_output_dir,
      "--",
      image_path
    ]

    mxl_output_dir = join(current_app.config.get("MXL_FOLDER"), _uuid)

    # Execute the command.
    current_app.logger.info(f"Running audiveris process: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        current_app.logger.error("Command failed!")
        current_app.logger.error("Return code:", result.returncode)
        current_app.logger.error(result.stdout)

    checkCorrectExport(result.stdout)

    # Copy the generated MXL file into MXL_FOLDER/uuid/file_name.mxl
    audiveris_mxl_path = join(audiberis_output_dir, f"{filename}.mxl")

    if os.path.exists(audiveris_mxl_path):
        current_app.logger.info(f"Copying the MXL file into {mxl_output_dir} directory")
        os.makedirs(mxl_output_dir)
        final_mxl_path = join(mxl_output_dir, f"{filename}.mxl")
        shutil.copy(audiveris_mxl_path, final_mxl_path)

        current_app.logger.info("MXL file saved correctly in:",  final_mxl_path)
        current_app.logger.info("Finished image_to_mxl() successfully...") 
            
        return final_mxl_path
    else:
        raise Exception(f"Could not find generated MXL file in {audiveris_mxl_path}")



def checkCorrectExport(stdout):

    java_exception = "java.lang.NullPointerException"
    low_resolution = "try 300 DPI"
    too_large_image = "Too large image"

    if java_exception in stdout:
        raise ScoreStructureError()

    if low_resolution in stdout:
        raise ScoreQualityError()
    
    if too_large_image in stdout:
        raise ScoreTooLargeImageError()

        

