"""Evaluación independiente y exportación con aprobación humana vinculada al resultado."""
import argparse
import csv
from collections import Counter
from comun import (RAIZ, CAMPOS, CASOS, Extraccion, leer, guardar, normalizar, validar,
                   coherente, firma_revision)

def aprobado(entrada, resultado):
    return (resultado['estado'] == 'ok' and resultado['modo'] != 'simulado'
            and not validar(resultado['datos'])
            and entrada.get('firma') == firma_revision(resultado)
            and entrada.get('aprobado') is True
            and bool(str(entrada.get('revisor','')).strip())
            and all(entrada.get('campos_verificados',{}).get(c) is True for c in CAMPOS))

def cargar_resultado(caso, carpeta):
    try:
        resultado = leer(RAIZ/'salidas'/carpeta/f'{caso}.json')
        if resultado['estado'] != 'ok':
            return resultado, 'fallo_tecnico:' + str(resultado.get('error'))
        Extraccion.model_validate(resultado['datos'])
        if not coherente(resultado, caso):
            return resultado, 'fallo_tecnico:entrada_modificada_o_distinta'
        return resultado, None
    except (OSError, ValueError, KeyError, TypeError):
        return None, 'fallo_tecnico:resultado_ausente_o_invalido'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--metodo', choices=['reglas','llm'], required=True)
    p.add_argument('--llm-modo', choices=['simulado','real'], default='simulado')
    args = p.parse_args()
    salida = RAIZ/'salidas'
    salida.mkdir(exist_ok=True)
    csv_ruta = salida/'solicitudes_para_pad.csv'
    # Invalidar cualquier exportación anterior incluso si después falla la evaluación.
    with csv_ruta.open('w', encoding='utf-8-sig', newline='') as archivo:
        csv.writer(archivo).writerow(CAMPOS)
    referencia = leer(RAIZ/'configuracion'/'referencia.json')
    revision_ruta = salida/'revision_humana.json'
    revisiones = leer(revision_ruta) if revision_ruta.exists() else {}
    reporte, pendientes, candidatos, plantilla = [], [], [], {}
    for caso in CASOS:
        for metodo, carpeta in [('reglas','reglas'), ('llm',f'llm_{args.llm_modo}')]:
            resultado, fallo = cargar_resultado(caso, carpeta)
            clave = f'{caso}:{carpeta}'
            if fallo:
                reporte.append(dict(caso=caso, metodo=carpeta, categoria='fallo_tecnico', detalle=fallo))
                pendientes.append(dict(caso=caso, metodo=carpeta, motivos=[fallo]))
                continue
            datos = resultado['datos']
            errores = validar(datos)
            texto = (salida/'ocr'/f'{caso}.txt').read_text(encoding='utf-8')
            texto_norm = normalizar(texto)
            coincidencias = {}
            categorias = {}
            for campo in CAMPOS:
                esperado = referencia[caso]['campos'][campo]
                observado = datos[campo]
                coincide = normalizar(esperado) == normalizar(observado)
                coincidencias[campo] = coincide
                if esperado is None:
                    categoria = 'dato_ausente_o_incierto' if observado is None else 'error_extraccion_dato_inventado'
                elif observado is None:
                    categoria = ('error_extraccion' if normalizar(esperado) in texto_norm
                                 else 'posible_error_ocr_requiere_original')
                elif coincide:
                    categoria = 'coincide_con_referencia'
                elif normalizar(esperado) in texto_norm:
                    categoria = 'error_extraccion'
                else:
                    categoria = 'posible_error_ocr_requiere_original'
                categorias[campo] = categoria
            evaluable = resultado['modo'] != 'simulado'
            reporte.append(dict(caso=caso, metodo=carpeta, modo=resultado['modo'],
                evaluable_para_rendimiento=evaluable, errores_validacion=errores,
                comparacion_por_campo={c:dict(esperado=referencia[caso]['campos'][c],
                    observado=datos[c], coincide=coincidencias[c], categoria=categorias[c]) for c in CAMPOS},
                aciertos_sobre_cinco=sum(coincidencias.values()) if evaluable else None))
            plantilla[clave] = dict(firma=firma_revision(resultado), aprobado=False, revisor='',
                    campos_verificados=dict.fromkeys(CAMPOS,False),
                    diagnostico=dict.fromkeys(CAMPOS,'pendiente'), notas='Comparar cada campo con el documento original.')
            motivos = list(errores.values())
            if resultado['modo'] == 'simulado': motivos.append('resultado_simulado_no_exportable')
            if not aprobado(revisiones.get(clave,{}), resultado): motivos.append('falta_aprobacion_humana_vigente')
            if motivos:
                pendientes.append(dict(caso=caso, metodo=carpeta, motivos=sorted(set(motivos))))
            if metodo == args.metodo and aprobado(revisiones.get(clave,{}), resultado):
                candidatos.append((caso, datos))
    conteo = Counter(d['id_solicitud'] for _, d in candidatos)
    aceptados = []
    for caso, datos in candidatos:
        if conteo[datos['id_solicitud']] > 1:
            pendientes.append(dict(caso=caso, metodo=args.metodo, motivos=['id_duplicado_en_exportacion']))
        else:
            aceptados.append({c:datos[c] for c in CAMPOS})
    with csv_ruta.open('w', encoding='utf-8-sig', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(aceptados)
    guardar(salida/'comparacion.json', reporte)
    guardar(salida/'pendientes_revision.json', pendientes)
    if not revision_ruta.exists(): guardar(revision_ruta, plantilla)
    guardar(salida/'revision_plantilla_actual.json', plantilla)
    guardar(salida/'exportacion.json', dict(metodo=args.metodo, llm_modo=args.llm_modo,
            filas=len(aceptados), duplicados=[i for i,n in conteo.items() if n>1],
            aviso='El formato válido no prueba fidelidad. La aprobación humana es obligatoria.'))
    lineas = ['# Comparación observada', '', 'La simulación se excluye de métricas de LLM real.',
              'Normalización: NFC y espacios únicamente; null coincide solo con null.',
              'Las etiquetas de OCR son hipótesis: confirmar en el original y registrar diagnóstico humano.', '']
    for fila in reporte:
        if 'comparacion_por_campo' not in fila:
            lineas.append(f"- {fila['caso']} / {fila['metodo']}: fallo técnico.")
        else:
            puntuacion = fila['aciertos_sobre_cinco']
            lineas.append(f"- {fila['caso']} / {fila['metodo']}: " +
                (f'{puntuacion}/5 coincidencias.' if puntuacion is not None else 'SIMULADO, sin puntuación de rendimiento.'))
            for campo, detalle in fila['comparacion_por_campo'].items():
                lineas.append(f"  - {campo}: {detalle['categoria']}; formato: {fila['errores_validacion'].get(campo,'válido')}.")
    lineas.extend(['',f'CSV: {len(aceptados)} filas aprobadas mediante {args.metodo}.'])
    (salida/'REPORTE.md').write_text('\n'.join(lineas)+'\n', encoding='utf-8')
    print(f'Reporte y pendientes generados. CSV: {len(aceptados)} filas; método: {args.metodo}.')

if __name__ == '__main__':
    main()
