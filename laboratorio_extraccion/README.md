# Laboratorio: OCR, reglas y LLM

Sesión de tres horas. Comienza por GUIA_ESTUDIANTE.md o output/pdf/GUIA_ESTUDIANTE.pdf. Completa la instalación antes de clase.

Secuencia obligatoria: inspección de PDF → OCR → extracción por reglas → extracción con LLM real o simulación explícita → mismo validador → comparación → revisión humana → CSV. La captura posterior en PAD es opcional.

Requisitos: Windows o macOS, Python 3.12, VS Code, Tesseract 5 y spa. requirements.txt instala paquetes Python, no el motor OCR. La guía contiene los comandos completos para ambos sistemas sin activar el entorno.

En scripts se encuentran E01-E05 y comun.py. entradas contiene tres PNG, sus PDF escaneados sin texto y un PDF digital. configuracion/referencia.json es solo para evaluar en E05, nunca para extraer. salidas está vacía al distribuir. PLANTILLA_RESULTADOS.md y RUBRICA.md establecen las evidencias.

Sin API: ejecuta E04 con --modo simulado. No hay llamadas ni lectura de claves. Es una simulación del circuito basada en reglas, excluida de conclusiones sobre LLM. La API real requiere aprobación docente y --autorizar-costo. No incluyas .env ni claves en entregas.

El CSV se exporta desde un solo método explícito y solo con revisión de los cinco campos contra el original. Por defecto contendrá únicamente los encabezados. Repetir E02 no sobrescribe el OCR; preserva el ensayo anterior renombrando la carpeta.

Las reglas de negocio se contrastaron con Registro.Validar de laboratorios/pad_solicitudes/app/Solicitudes.cs. El laboratorio adelanta OCR y LLM; no modifica automáticamente el calendario de 48 horas. Véase ESTADO_VALIDACION.md.
