import subprocess
import os
from os.path import join
from pathlib import Path
import shutil
from flask import current_app
from scripts.svg_to_png import convert_svg_to_png

def image_to_mxl(image_path, _uuid):

    """
    Converts a image file of a musical score to a MXL file using Audiveris.

    Args:
        image_path: Path to the input image.
        _uuid: Unique upload identifier
        
    Returns:
        The path of the generated MXL file. 

    """

    print("\n\nStarting image_to_mxl()...")

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

    try:

        # Execute the command.
        print(f"Running audiveris process: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Audiveris stdout:", result.stdout)
        print("Audiveris processing complete.")

        # Copy the generated MXL file into MXL_FOLDER/uuid/file_name.mxl
        audiveris_mxl_path = join(audiberis_output_dir, f"{filename}.mxl")
        print("audiveris_mxl_path: ", audiveris_mxl_path)

        if os.path.exists(audiveris_mxl_path):
            print(f"Copying the MXL file into {mxl_output_dir} directory")
            os.makedirs(mxl_output_dir)
            final_mxl_path = join(mxl_output_dir, f"{filename}.mxl")
            shutil.copy(audiveris_mxl_path, final_mxl_path)

            print("MXL file saved correctly in:",  final_mxl_path)
            print("Finished image_to_mxl() successfully...") 
             
            return final_mxl_path
        else:
            raise Exception(f"Could not find generated MXL file in {audiveris_mxl_path}")

    except subprocess.CalledProcessError as e:
        raise Exception("Error running Audiveris: ", e.stdout)
