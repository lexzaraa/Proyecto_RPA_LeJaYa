"""Funciones compartidas. Los extractores nunca cargan la referencia de evaluación."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from pydantic import BaseModel, ConfigDict

RAIZ = Path(__file__).resolve().parents[1]
CAMPOS = ('id_solicitud', 'solicitante', 'area', 'tipo', 'descripcion')
AREAS = ('Administración', 'Docencia', 'Biblioteca')
TIPOS = ('Acceso', 'Equipo', 'Mantenimiento')
CASOS = ('C01', 'C02', 'C03')

class Extraccion(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id_solicitud: str | None
    solicitante: str | None
    area: str | None
    tipo: str | None
    descripcion: str | None
    observaciones: list[str]

def leer(ruta):
    return json.loads(Path(ruta).read_text(encoding='utf-8'))

def guardar(ruta, datos):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()

def normalizar(valor):
    # Solo NFC y espacios. No cambiar mayúsculas, acentos, dígitos o vocabulario.
    return None if valor is None else ' '.join(unicodedata.normalize('NFC', valor).split())

def validar(datos):
    errores = {}
    for campo in CAMPOS:
        valor = datos.get(campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            errores[campo] = 'dato_ausente_o_incierto'
        elif not isinstance(valor, str):
            errores[campo] = 'tipo_incorrecto'
    ident = datos.get('id_solicitud')
    if 'id_solicitud' not in errores and re.fullmatch(r'SOL-\d{3}', ident) is None:
        errores['id_solicitud'] = 'incumplimiento_de_reglas'
    for campo, minimo, maximo in [('solicitante',3,80),('descripcion',10,240)]:
        if campo not in errores:
            valor = datos[campo]
            # Mismas comprobaciones de Trim y longitud máxima del C#.
            longitud = len(valor.encode('utf-16-le')) // 2
            if len(valor.strip().encode('utf-16-le')) // 2 < minimo or longitud > maximo:
                errores[campo] = 'incumplimiento_de_reglas'
    for campo, catalogo in [('area',AREAS), ('tipo',TIPOS)]:
        if campo not in errores and datos[campo] not in catalogo:
            errores[campo] = 'incumplimiento_de_reglas'
    return errores

# Patrones de redacción en párrafo (texto libre). No contienen datos de ningún caso.
PATRONES_LIBRES = {
    'solicitante': r'(?:fue\s+)?presentad[ao]\s+por\s+(.+?)(?=\s+para\s+(?:el\s+)?[áa]rea\b|[.;:]|$)',
    'area': r'\b[áa]rea\s+de\s+(.+?)(?=[.;,]|\s+corresponde\b|$)',
    'tipo': r'\b(?:corresponde\s+al\s+)?tipo\s+(?!de\b)([^\s.;,:]+(?:\s+[^\s.;,:]+)*?)(?=[.;,]|\s+se\s+solicita\b|$)',
    'descripcion': r'\bse\s+solicita\s*:\s*(.+)$',
}
def extraer_reglas(texto):
    """Una etiqueta inicia el campo; la siguiente lo termina. Respaldo por redacción libre. No memoriza casos."""
    etiquetas = r'Identificador|Solicitante|Área|Tipo|Descripción'
    patron = re.compile(rf'^\s*({etiquetas})\s*:\s*(.*?)(?=^\s*(?:{etiquetas})\s*:|\Z)', re.M | re.S | re.I)
    mapa = {'identificador':'id_solicitud','solicitante':'solicitante','área':'area','tipo':'tipo','descripción':'descripcion'}
    datos = dict.fromkeys(CAMPOS)
    observaciones = []
    vistos = set()
    for coincidencia in patron.finditer(texto):
        campo = mapa[coincidencia[1].lower()]
        if campo in vistos:
            datos[campo] = None
            observaciones.append(f'Etiqueta repetida: {campo}; requiere revisión.')
        else:
            datos[campo] = ' '.join(coincidencia[2].split()) or None
        vistos.add(campo)
    # Permite identificar SOL en texto libre; no infiere nombres ni catálogos.
    if 'id_solicitud' not in vistos:
        ids = re.findall(r'(?<![\w-])SOL-\d{3}(?![\w-])', texto)
        datos['id_solicitud'] = ids[0] if len(ids) == 1 else None

    # Respaldo para redacción en párrafo: solo campos sin etiqueta y solo si el patrón coincide.
    plano = ' '.join(texto.split())
    for campo, regex in PATRONES_LIBRES.items():
        if campo in vistos or datos[campo] is not None:
            continue
        m = re.search(regex, plano, re.I)
        if m:
            datos[campo] = m.group(1).strip() or None
            observaciones.append(f'Campo {campo} extraído de redacción libre; requiere revisión humana.')

    
    return Extraccion(**datos, observaciones=observaciones)

def sobre(caso, metodo, modo, datos=None, error=None):
    texto = RAIZ / 'salidas' / 'ocr' / f'{caso}.txt'
    meta = leer(texto.with_suffix('.json'))
    return dict(caso=caso, metodo=metodo, modo=modo,
                estado='fallo_tecnico' if error else 'ok', error=error,
                ocr_sha256=huella(texto), fuente=meta['fuente'],
                fuente_sha256=meta['fuente_sha256'],
                datos=datos.model_dump() if datos is not None else None)

def coherente(resultado, caso):
    texto = RAIZ/'salidas'/'ocr'/f'{caso}.txt'
    meta = leer(texto.with_suffix('.json'))
    fuente = RAIZ / meta['fuente']
    return (resultado.get('ocr_sha256') == huella(texto)
            and resultado.get('fuente') == meta['fuente']
            and resultado.get('fuente_sha256') == huella(fuente) == meta['fuente_sha256'])

def firma_revision(resultado):
    contenido = json.dumps(resultado, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(contenido).hexdigest()
