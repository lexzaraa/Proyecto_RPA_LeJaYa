"""Extrae texto directamente; esto NO es OCR."""
import pymupdf
from comun import RAIZ, guardar

def main():
    filas = []
    for archivo in sorted((RAIZ/'entradas').glob('*.pdf')):
        with pymupdf.open(archivo) as doc:
            texto = '\n'.join(p.get_text() for p in doc)
            destino = RAIZ/'salidas'/'directo'/f'{archivo.stem}.txt'
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding='utf-8')
            filas.append(dict(archivo=archivo.name, paginas=len(doc), caracteres=len(texto.strip()),
                              clasificacion='texto extraíble' if texto.strip() else 'sin texto extraíble: candidato a OCR'))
    guardar(RAIZ/'salidas'/'inspeccion.json', filas)
    for fila in filas:
        print(fila)
    print('Una capa de texto puede ser OCR previo; inspección y revisión visual se complementan.')

if __name__ == '__main__':
    main()
