"""Renderiza páginas completas de PDF a 300 dpi y aplica OCR español."""
import argparse
import os
import shutil
import sys
import pymupdf
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from comun import RAIZ, CASOS, guardar, huella

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--formato', choices=['pdf','png'], default='pdf')
    p.add_argument('--ensayo', default='principal', choices=['principal','png'])
    args = p.parse_args()
    load_dotenv(RAIZ/'.env')
    motor = os.getenv('TESSERACT_CMD') or shutil.which('tesseract')
    if not motor:
        sys.exit('Falta Tesseract. Instálalo y configura TESSERACT_CMD; consulta GUIA_ESTUDIANTE.md.')
    pytesseract.pytesseract.tesseract_cmd = motor
    if 'spa' not in pytesseract.get_languages(config=''):
        sys.exit('Falta spa.traineddata. Comprueba tesseract --list-langs y la guía.')
    destino = RAIZ/'salidas'/('ocr' if args.ensayo == 'principal' else 'ocr_png')
    destino.mkdir(parents=True, exist_ok=True)
    # Nunca sobrescribir OCR: preservar el texto de cada ensayo.
    if any((destino/f'{c}.txt').exists() or (destino/f'{c}.json').exists() for c in CASOS):
        sys.exit(f'El ensayo ya existe: {destino}. Renombra la carpeta para preservar el OCR anterior.')
    for caso in CASOS:
        archivo = RAIZ/'entradas'/f'{caso}.{args.formato}'
        imagenes = []
        if args.formato == 'pdf':
            with pymupdf.open(archivo) as doc:
                for i, pagina in enumerate(doc, 1):
                    pix = pagina.get_pixmap(dpi=300, alpha=False)
                    ruta = destino/f'{caso}_pagina_{i}.png'
                    pix.save(ruta)
                    imagenes.append(ruta)
        else:
            imagenes.append(archivo)
        textos = []
        for ruta in imagenes:
            with Image.open(ruta) as imagen:
                textos.append(pytesseract.image_to_string(imagen, lang='spa', config='--psm 6', timeout=90))
        texto = '\n\f\n'.join(textos)
        (destino/f'{caso}.txt').write_text(texto, encoding='utf-8')
        guardar(destino/f'{caso}.json', dict(fuente=str(archivo.relative_to(RAIZ)),
                fuente_sha256=huella(archivo), idioma='spa', dpi_pdf=300,
                motor=str(pytesseract.get_tesseract_version()), configuracion='--psm 6'))
        print(f'{caso}: {len(texto)} caracteres; {destino.name}/{caso}.txt')

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, pytesseract.TesseractError) as error:
        sys.exit(f'OCR falló ({type(error).__name__}). Revisa motor, idioma, rutas y permisos; conserva el ensayo parcial.')
