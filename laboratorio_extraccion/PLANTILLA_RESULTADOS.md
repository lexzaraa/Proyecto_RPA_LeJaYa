# Evidencia del equipo

Integrantes: 
Sistema / Python / Tesseract / spa disponible: 
Ruta del ensayo: 
LLM real o simulado / modelo (si real): 

## Inspección

PDF digital, caracteres extraídos: 
PDF escaneados, caracteres extraídos directamente: 
Diferencia entre OCR, extracción, validación y revisión: 

## Observaciones por campo

Completa una fila por cada campo de cada documento (15 filas).

| Caso | Campo | Visible en original | Texto OCR | Reglas | LLM y modo | Coincide | Formato válido | Diagnóstico confirmado |
|---|---|---|---|---|---|---|---|---|
| C01 | id_solicitud | | | | | | | |

Diagnósticos: OCR, extracción, incumplimiento de reglas, ausente/incierto, fallo técnico. Pueden coexistir. No confundir una hipótesis automática de OCR con una comprobación visual.

## Ejercicio de modificación

Cambio general de etiqueta Area / Área: 
Prueba agregada y resultado: 
Por qué no memoriza documentos: 

## Comparación y revisión

Huellas OCR iguales por caso: 
Aciertos observados de reglas (por documento): 
Aciertos observados del LLM real, o NO MEDIDO si simulado: 
Limitaciones de la comparación literal de descripciones: 
Método elegido para CSV: 
Filas aprobadas, revisor y justificación: 
Casos pendientes y causa: 

## Evidencias

### E06. Inspeccionar los originales [análisis manual]
¿Qué formatos tienen texto seleccionable? ¿Qué campos ves?

El único formato con texto seleccionable son los '.pgn'
Campos = ['Identificadpr', 'Area', 'Tipo', 'Solicitante']

### E08. Explicar el alcance [análisis]

- Una imagen tiene píxeles, estos contienen información visual, pero no necesariamente texto que una computadora pueda copiar directamente.
- El OCR intenta convertirlos en texto, analiza las imágenes e intenta identificar las letras, números y palabras que aparecen en ella.
- Extraer campos organiza ese texto, por ejemplo, separar el nombre, la solicitud, el folio y el tipo.

- La validación verifica que los datos cumplan ciertas condiciones, como tener una fecha válida, un importe numérico o un folio con el formato esperado.

Rutas de OCR, JSON de ambos métodos, reporte, pendientes, revisión y CSV: 
Resultado de unittest: 

### E10. Comparar texto y documento [VS Code y visor]
- Acento: México | Mexico ----- Observación de ejemplo: El texto extraído omitió el acento de la palabra "México"
- Identificador: SOL-308 | SOL-3O8 ----- Observación de ejemplo: el OCR confundió el número cero (0) con la letra O en el identificador.
- Campo ausente: Teléfono: 9981234567 | Teléfono: ----- Observación de ejemplo: el campo de "Teléfono" está presente en la imagen original, pero no aparece en el texto extraído.

### E11. Inspeccionar el renderizado [código y ejercicio]

¿Por qué renderizar la página completa conserva el diseño mientras extraer imágenes incrustadas puede perder textos, giros o capas?

El renderizado de la página completa permite representar conjuntamente los elementos visibles del documento, como texto, imágenes, tablas, líneas y elementos girados. Esto evita algunas de las limitaciones de extraer únicamente las imágenes incrustadas, ya que estas no necesariamente contienen todos los elementos de la página. 

## Reflexión de 150-200 palabras

Escribe aquí.
