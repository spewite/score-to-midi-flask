import cairosvg
from os.path import basename
from flask import current_app

def convert_svg_to_png(input_svg, output_png):
    try:
        input_name = basename(input_svg)
        output_name = basename(output_png)
        cairosvg.svg2png(url=input_svg, write_to=output_png, background_color='white')
        current_app.logger.info(f"Successfully converted {input_name} to {output_name}")
    except Exception as e:
        current_app.logger.error(f"An error occurred: {e}")
