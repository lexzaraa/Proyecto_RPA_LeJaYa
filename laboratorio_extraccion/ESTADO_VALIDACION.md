# Estado de validación · 13 de octubre de 2026

Probado realmente en macOS, Apple Silicon, Python 3.12.14 y Tesseract 5.5.3 con idioma spa:

- Instalación de paquetes y pip check sin dependencias rotas.
- PDF digital con 179 caracteres extraídos directamente; tres PDF escaneados con cero caracteres y una imagen de página cada uno.
- Renderizado de páginas completas a 300 dpi y OCR en español desde los tres PDF; también OCR directo de sus tres PNG.
- Texto OCR equivalente a la transcripción de referencia tras NFC y normalización de espacios en los tres casos. No se observaron errores de reconocimiento en esta ejecución; no se generaliza a otros documentos.
- Extracción por reglas: C01 5/5 coincidencias; C02 1/5; C03 5/5 contando correctamente Tipo=null. C03 no cumple el campo requerido y no puede capturarse.
- E04 simulado y comparación ejecutados. La simulación reutiliza reglas, está identificada y no aporta métricas de un LLM real.
- CSV UTF-8 con BOM y cinco encabezados exactos, sin filas al no existir aprobación humana. Exportación positiva y bloqueo de duplicados comprobados con fixtures sintéticos de prueba, no como aprobación humana real.
- 26 pruebas locales correctas: reglas, validación, contratos, duplicados, aprobaciones, cambios de fuente/resultado y respuestas del modelo. Incluyen el SDK oficial con transporte HTTP simulado, sin red.
- Reejecutar E02 rechaza sobrescribir OCR. El modo API real sin --autorizar-costo se rechaza antes de cargar configuración o llamar.
- Guía PDF de 12 páginas y cuatro PDF de entrada renderizados e inspeccionados visualmente; ZIP comprobado por lista de archivos permitidos y extracción de prueba.

No probado: Windows, diseñador PAD, llamadas reales a OpenAI, rendimiento de un modelo ni costo/latencia reales. La portabilidad del código no sustituye la aceptación en Windows. No se leyó ninguna clave preexistente ni se realizaron llamadas pagadas.

Fuentes de mantenimiento: laboratorios/laboratorio_extraccion. La versión docente conserva evidencia sintética del ensayo en docente/validacion_macos; esa carpeta no está en el ZIP estudiantil. La guía docente incluye la lista de aceptación de Windows.
