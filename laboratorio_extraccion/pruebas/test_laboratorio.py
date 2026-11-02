"""Pruebas locales: no usan claves ni realizan solicitudes de red."""
import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import comun
import E04_extraer_con_llm as llm
import E05_validar_comparar_exportar as final
from pydantic import ValidationError
from openai import AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError

BUENO = dict(id_solicitud='SOL-123', solicitante='Persona de prueba', area='Docencia',
             tipo='Acceso', descripcion='Habilitar el acceso del laboratorio.')

def datos():
    return comun.Extraccion(**BUENO, observaciones=[])

class ContratoYReglas(unittest.TestCase):
    def test_ausente_null(self):
        d = comun.extraer_reglas('Identificador: SOL-123\nSolicitante: Persona ficticia\nÁrea: Docencia\nDescripción: Revisar equipo de prueba.')
        self.assertIsNone(d.tipo)
        self.assertEqual(comun.validar(d.model_dump())['tipo'],'dato_ausente_o_incierto')

    def test_ids_invalidos(self):
        for ident in ['SOL-12','SOL-1234','S0L-123','SOL-ABC','sol-123','SOL-123\n']:
            with self.subTest(ident=ident):
                self.assertIn('id_solicitud', comun.validar(dict(BUENO,id_solicitud=ident)))

    def test_limites_y_catalogos(self):
        for campo, valor in [('solicitante','ab'),('solicitante','x'*81),('descripcion','corta'),
                              ('descripcion','x'*241),('area','Rectoría'),('tipo','Otro')]:
            self.assertIn(campo,comun.validar(dict(BUENO,**{campo:valor})))
        self.assertEqual(comun.validar(BUENO),{})

    def test_no_inventar_en_parrafo(self):
        d = comun.extraer_reglas('SOL-123: una persona solicita revisar el equipo en Docencia.')
        self.assertEqual(d.id_solicitud,'SOL-123')
        self.assertIsNone(d.solicitante)
        self.assertIsNone(d.tipo)

    def test_etiquetas_repetidas(self):
        d=comun.extraer_reglas('Tipo: Equipo\nTipo: Acceso\nTipo: Mantenimiento')
        self.assertIsNone(d.tipo)
        self.assertTrue(d.observaciones)

    def test_normalizacion_limitada(self):
        self.assertEqual(comun.normalizar('  Administracio\u0301n \n'), 'Administración')
        self.assertNotEqual(comun.normalizar('administracion'),'Administración')
        self.assertIsNone(comun.normalizar(None))

    def test_contrato_rechaza_tipos_y_extras(self):
        for cambio in [dict(tipo=3),dict(otro='inventado')]:
            with self.assertRaises(ValidationError):
                comun.Extraccion(**dict(BUENO,observaciones=[],**cambio))

class Modelo(unittest.TestCase):
    def test_respuesta_valida(self):
        self.assertEqual(llm.interpretar(NS(status='completed',output=[],output_parsed=datos())).id_solicitud,'SOL-123')

    def test_respuesta_incompleta(self):
        with self.assertRaisesRegex(llm.FalloModelo,'incompleta'):
            llm.interpretar(NS(status='incomplete',output=[],output_parsed=None))

    def test_rechazo(self):
        with self.assertRaisesRegex(llm.FalloModelo,'rechazo'):
            llm.interpretar(NS(status='completed', output=[NS(content=[NS(type='refusal')])],output_parsed=None))

    def test_respuesta_sin_estructura(self):
        with self.assertRaisesRegex(llm.FalloModelo,'sin_estructura'):
            llm.interpretar(NS(status='completed',output=[],output_parsed=None))

    def test_respuesta_invalida(self):
        with self.assertRaises(ValidationError):
            llm.interpretar(NS(status='completed',output=[],output_parsed={'id_solicitud':7}))

    def test_integracion_sin_red(self):
        cliente=Mock()
        cliente.responses.parse.return_value=NS(status='completed',output=[],output_parsed=datos(),id='mock-local')
        texto='Documento de prueba, sin referencia.'
        respuesta, ident=llm.llamar(cliente,'modelo-configurable',texto)
        argumentos=cliente.responses.parse.call_args.kwargs
        self.assertEqual(argumentos['input'],[{'role':'user','content':texto}])
        self.assertIs(argumentos['text_format'],comun.Extraccion)
        self.assertFalse(argumentos['store'])
        self.assertEqual(ident,'mock-local')

    def test_categorias_errores_api(self):
        respuesta=Mock(); respuesta.status_code=401
        for error,esperado in [
            (AuthenticationError('prueba',response=respuesta,body=None),'autenticacion_fallida'),
            (RateLimitError('prueba',response=respuesta,body=None),'limite_o_cuota'),
            (APIConnectionError(request=Mock()),'conexion'),
            (APITimeoutError(request=Mock()),'tiempo_agotado')]:
            self.assertEqual(llm.clasificar_error(error),esperado)

class Exportacion(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.raiz=Path(self.tmp.name)
        self.parches=[patch.object(comun,'RAIZ',self.raiz),patch.object(final,'RAIZ',self.raiz)]
        for p in self.parches:p.start()
        self.resultados={}
        ref={}
        for i,caso in enumerate(comun.CASOS):
            fuente=self.raiz/'entradas'/f'{caso}.png';fuente.parent.mkdir(exist_ok=True);fuente.write_bytes(b'original sintetico'+caso.encode())
            texto=self.raiz/'salidas'/'ocr'/f'{caso}.txt';texto.parent.mkdir(parents=True,exist_ok=True);texto.write_text('Texto de prueba',encoding='utf-8')
            comun.guardar(texto.with_suffix('.json'),dict(fuente=str(fuente.relative_to(self.raiz)),fuente_sha256=comun.huella(fuente)))
            for metodo in ['reglas','llm']:
                d=datos(); d.id_solicitud=f'SOL-{801+i}'
                resultado=comun.sobre(caso,metodo,'real',d)
                carpeta='reglas' if metodo=='reglas' else 'llm_real'
                comun.guardar(self.raiz/'salidas'/carpeta/f'{caso}.json',resultado)
                self.resultados[f'{caso}:{carpeta}']=resultado
            ref[caso]={'campos':d.model_dump()}
        comun.guardar(self.raiz/'configuracion'/'referencia.json',ref)

    def tearDown(self):
        for p in reversed(self.parches):p.stop()
        self.tmp.cleanup()

    def ejecutar(self):
        with patch.object(sys,'argv',['E05','--metodo','reglas','--llm-modo','real']),contextlib.redirect_stdout(io.StringIO()):
            final.main()
        with (self.raiz/'salidas'/'solicitudes_para_pad.csv').open(encoding='utf-8-sig',newline='') as f:
            lector=csv.DictReader(f);self.assertEqual(lector.fieldnames,list(comun.CAMPOS));return list(lector)

    def aprobar(self):
        revision={k:dict(firma=comun.firma_revision(r),aprobado=True,revisor='Revisor de prueba',campos_verificados=dict.fromkeys(comun.CAMPOS,True)) for k,r in self.resultados.items()}
        comun.guardar(self.raiz/'salidas'/'revision_humana.json',revision)

    def test_sin_revision_csv_vacio(self):
        self.assertEqual(self.ejecutar(),[])

    def test_aprobados_exporta_un_metodo(self):
        self.aprobar(); self.assertEqual(len(self.ejecutar()),3)

    def test_duplicados_excluidos(self):
        r=self.resultados['C02:reglas'];r['datos']['id_solicitud']='SOL-801'
        comun.guardar(self.raiz/'salidas'/'reglas'/'C02.json',r)
        self.aprobar(); filas=self.ejecutar()
        self.assertEqual([f['id_solicitud'] for f in filas],['SOL-803'])

    def test_resultado_modificado_invalida_aprobacion(self):
        self.aprobar()
        r=self.resultados['C01:reglas'];r['datos']['solicitante']='Otra persona'
        comun.guardar(self.raiz/'salidas'/'reglas'/'C01.json',r)
        self.assertEqual(len(self.ejecutar()),2)

    def test_fuente_modificada_bloquea(self):
        self.aprobar();(self.raiz/'entradas'/'C01.png').write_bytes(b'modificacion')
        self.assertEqual(len(self.ejecutar()),2)

    def test_simulado_no_exportable(self):
        self.aprobar()
        r=self.resultados['C01:reglas'];r['modo']='simulado'
        self.assertFalse(final.aprobado(dict(firma=comun.firma_revision(r),aprobado=True,revisor='X',campos_verificados=dict.fromkeys(comun.CAMPOS,True)),r))

    def test_fallo_no_usa_resultado_anterior(self):
        self.aprobar();self.assertEqual(len(self.ejecutar()),3)
        comun.guardar(self.raiz/'salidas'/'reglas'/'C01.json',{'estado':'fallo_tecnico','error':'cuota','datos':None})
        self.assertEqual(len(self.ejecutar()),2)

    def test_dato_ausente_bloquea_aun_aprobado(self):
        r=self.resultados['C03:reglas'];r['datos']['tipo']=None
        comun.guardar(self.raiz/'salidas'/'reglas'/'C03.json',r)
        self.aprobar();self.assertEqual(len(self.ejecutar()),2)

if __name__=='__main__':unittest.main()
