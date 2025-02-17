from pathlib import Path
from os.path import join
import os
from flask import current_app
import partitura as pt

def mxl_to_midi(mxl_path, _uuid):
    """
    Convierte un archivo MXL (MusicXML comprimido) en un archivo MIDI utilizando Partitura.

    Args:
        mxl_path: Ruta del archivo MXL de entrada.
        _uuid: Identificador único para la subida.

    Returns:
        La ruta del archivo MIDI generado.
    """
    print("\n\nIniciando mxl_to_midi()...")

    # Verificar que el archivo exista
    mxl_file = Path(mxl_path)
    if not mxl_file.exists():
        raise FileNotFoundError(f'{mxl_path} no existe.')

    # Parsear el archivo MusicXML usando Partitura
    print("Analizando el archivo MXL:", mxl_path)
    try:
        score = pt.load_score(mxl_path)
    except Exception as e:
        raise ValueError(f"Error al analizar MusicXML: {e}")

    # Crear la carpeta de salida para el MIDI
    midi_output_dir = join(current_app.config.get("MIDI_FOLDER"), _uuid)
    os.makedirs(midi_output_dir, exist_ok=True)

    print("Guardando el archivo MIDI.")
    mxl_filename_base = mxl_file.stem
    midi_file_path = join(midi_output_dir, f'{mxl_filename_base}.mid')
    try:
        # Convertir el score a un archivo MIDI
        pt.save_score_midi(score, midi_file_path)
    except Exception as e:
        print(f"Advertencia: Error al guardar el archivo MIDI - {e}. El archivo MIDI podría estar incompleto o corrupto.")

    print("Archivo MIDI guardado en:", midi_file_path)
    print("mxl_to_midi() finalizó exitosamente.")
    return midi_file_path
