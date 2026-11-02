"""SDK oficial real con transporte HTTP simulado; nunca accede a la red."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import httpx2
from openai import OpenAI
from E04_extraer_con_llm import llamar, FalloModelo, clasificar_error

DATOS=dict(id_solicitud='SOL-124',solicitante='Persona de prueba',area='Docencia',
           tipo='Acceso',descripcion='Habilitar acceso al laboratorio.',observaciones=[])

class SDKSinRed(unittest.TestCase):
    def cliente(self, estado=200, contenido=None, status='completed'):
        def responder(request):
            cuerpo=json.loads(request.content)
            self.assertEqual(cuerpo['model'],'gpt-4.1-mini')
            self.assertEqual(cuerpo['text']['format']['type'],'json_schema')
            esquema=cuerpo['text']['format']['schema']
            self.assertFalse(esquema['additionalProperties'])
            self.assertIn('null',str(esquema['properties']['tipo']))
            self.assertEqual(cuerpo['input'],[{'role':'user','content':'Texto OCR de prueba.'}])
            if estado!=200:
                return httpx2.Response(estado,json={'error':{'message':'Error sintético','type':'prueba','code':None}})
            return httpx2.Response(200,json=dict(id='resp_sintetica',object='response',created_at=0,
                status=status,model='gpt-4.1-mini',error=None,
                incomplete_details={'reason':'max_output_tokens'} if status!='completed' else None,
                output=[dict(type='message',id='msg_sintetico',role='assistant',status='completed',
                    content=contenido if contenido is not None else [dict(type='output_text',text=json.dumps(DATOS),annotations=[])])]))
        return OpenAI(api_key='prueba-sintetica-no-es-una-clave',max_retries=0,
                      http_client=httpx2.Client(transport=httpx2.MockTransport(responder)))

    def test_sdk_serializa_y_parsea_esquema(self):
        with self.cliente() as cliente:
            datos,ident=llamar(cliente,'gpt-4.1-mini','Texto OCR de prueba.')
        self.assertEqual(datos.id_solicitud,'SOL-124')
        self.assertEqual(ident,'resp_sintetica')

    def test_sdk_auth_y_cuota(self):
        for codigo,categoria in [(401,'autenticacion_fallida'),(429,'limite_o_cuota')]:
            with self.subTest(codigo=codigo),self.cliente(estado=codigo) as cliente:
                with self.assertRaises(Exception) as capturado:
                    llamar(cliente,'gpt-4.1-mini','Texto OCR de prueba.')
                self.assertEqual(clasificar_error(capturado.exception),categoria)

    def test_sdk_rechazo(self):
        with self.cliente(contenido=[dict(type='refusal',refusal='Rechazo sintético.')]) as cliente:
            with self.assertRaisesRegex(FalloModelo,'rechazo'):
                llamar(cliente,'gpt-4.1-mini','Texto OCR de prueba.')

    def test_sdk_respuesta_incompleta(self):
        with self.cliente(status='incomplete') as cliente:
            with self.assertRaises(Exception) as capturado:
                llamar(cliente,'gpt-4.1-mini','Texto OCR de prueba.')
            self.assertEqual(clasificar_error(capturado.exception),'respuesta_incompleta')

if __name__=='__main__':unittest.main()
