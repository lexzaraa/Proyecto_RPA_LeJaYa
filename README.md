# Proyecto integral de RPA: cierre del segundo parcial

**Materia:** Automatización Robótica de Procesos
**Docente:** Fernando Gómez García
**Fecha de entrega:** 01/11/2026

Flujo completo: documento → extracción → validación y revisión → CSV aprobado → formulario → folio verificado y bitácora.

El proyecto extrae cinco campos (`id_solicitud`, `solicitante`, `area`, `tipo`, `descripcion`) de documentos PDF o imagen de tres casos ficticios (C01, C02 y C03), los valida con revisión humana y registra únicamente las solicitudes aprobadas en la aplicación **Solicitudes RPA** mediante Power Automate Desktop (PAD). Todos los datos son ficticios.

## Integrantes

- Ortiz Herrera Yahir Eduardo
- Zaragoza Bahena Sharon Alexia
- Itzá Hernández Jael Asaf

## Herramientas y versiones

| Herramienta | Versión | Uso |
|---|---|---|
| Windows | 26H2 (compilación SO 26300.9711) | Sistema donde se ejecutó PAD |
| Power Automate Desktop | 11.2610.155.0 | Flujo de carga |
| Python | 3.14.7 | Scripts de extracción |
| Tesseract OCR | 5.5.3.20260724 (idioma `spa`) | Texto de los documentos escaneados |
| pytesseract | 0.3.13 | Envoltorio de Python para Tesseract |
| PyMuPDF (`pymupdf`) | 1.28.2 | Inspección de PDF y conversión de páginas |
| Pillow | 12.3.0 | Manejo de imágenes |
| Pydantic | 2.14.1 | Validación del esquema de extracción |
| python-dotenv | 1.2.4 | Lo importa `E04` (no se usa en modo simulado) |
| openai | 3.29.0 | Lo importa `E04` (no se usa en modo simulado) |
| Aplicación Solicitudes RPA | Laboratorio de escritorio | Formulario de destino |

La lista completa de paquetes está en `laboratorio_extraccion/requirements.txt`. Tesseract está instalado en `C:\Program Files\Tesseract-OCR\`; en el equipo de prueba el comando `tesseract` no estaba disponible en el `PATH` de la terminal.

## Estructura del repositorio

| Carpeta o archivo | Contenido |
|---|---|
| `README.md` | Este documento (incluye la reflexión) |
| `matriz_pruebas.xlsx` | Matriz de las 7 pruebas obligatorias |
| `laboratorio_extraccion/` | Scripts (`scripts/E01` a `E05`, `comun.py`, `comun_v1_original.py`), `configuracion/`, `entradas/` (documentos originales), `requirements.txt` y el material del laboratorio |
| `Extraccion_rama_LLM/` | Resultados de la rama LLM (simulada) |
| `Extraccion_comparacion_ramas/` | Comparación de las ramas de reglas y LLM |
| `Patron_Libre_redaccion/` | Evidencia de la modificación de `extraer_reglas` para C02 (salida original y modificada) |
| `Exportacion_CSV_Aprobado/` | CSV aprobado, revisión humana y casos pendientes |
| `Evidencias - 2Script/` | Evidencias de la inspección y del OCR |
| `Evidencias_RPA/` | Capturas del flujo de PAD |
| `Cambios_Proyecto_Registro_Solicitudes_Lote/` | Capturas del flujo antes y después de los cambios |
| `Evidencia_Prueba1/` a `Evidencia_Prueba7/` | Evidencia de cada una de las 7 pruebas |
| `inspeccion.json` | Muestra de la inspección de los PDF |

`salidas/` (resultados generados), `.venv/`, `.env` y `__pycache__/` **no** se suben al repositorio; se excluyen con `.gitignore`. Las muestras revisadas de lo generado están en las carpetas de evidencia. El resto de las evidencias y el video se entregan en Google Classroom.

## Rutas configurables

**Scripts de Python.** `comun.py` calcula la raíz del proyecto (`RAIZ`) a partir de su propia ubicación, de modo que no hay rutas absolutas que cambiar. Se leen `entradas/`, `salidas/` y `configuracion/` dentro de `laboratorio_extraccion/`.

**Flujo de PAD** (`Proyecto_RegistroSolicitudes_Lote`, pestaña `Main`):

| Variable | Acción | Valor de referencia |
|---|---|---|
| `RutaCsv` | `C01 - Establecer variable` | `<RAIZ>\salidas\solicitudes_para_pad.csv` |
| `RutaResultados` | `C02 - Establecer variable` | `<RAIZ>\salidas\bitacora_carga.csv` |

`<RAIZ>` es la carpeta `laboratorio_extraccion` en el equipo donde se ejecute. `LimiteSondeos` (10) controla cuántos segundos espera el flujo cada respuesta de la aplicación.

## Preparación

1. Desde `laboratorio_extraccion/`, crear y activar el entorno virtual e instalar las dependencias:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Instalar Tesseract OCR con el idioma español (`spa`).
3. Colocar los documentos originales (C01, C02 y C03, en PDF y PNG) en `entradas/`.
4. No hace falta `.env` ni clave de API: la rama LLM se ejecuta en **modo simulado**.
5. Reconstruir el flujo de PAD según la sección "Flujo de PAD".
6. Abrir **Solicitudes RPA | Laboratorio de escritorio**, con el escenario de prueba en **Base** y el formulario vacío.

## Ejecución

### 1. Extracción y revisión (fuera de PAD)

Desde `laboratorio_extraccion/`:

```powershell
.\.venv\Scripts\python.exe .\scripts\E01_inspeccionar_documento.py
.\.venv\Scripts\python.exe .\scripts\E02_extraer_texto_ocr.py
.\.venv\Scripts\python.exe .\scripts\E03_extraer_con_reglas.py
.\.venv\Scripts\python.exe .\scripts\E04_extraer_con_llm.py --modo simulado
.\.venv\Scripts\python.exe .\scripts\E05_validar_comparar_exportar.py --metodo reglas --llm-modo simulado
```

`E05` genera `salidas/revision_humana.json` con una plantilla. Para cada caso, una persona compara los cinco campos con el **documento original** y edita **solo** `revision_humana.json`: `aprobado: true`, su nombre en `revisor` y los cinco `campos_verificados` en `true`. La `firma` debe coincidir con la de `revision_plantilla_actual.json` (se regenera en cada ejecución; si cambia el resultado de extracción, hay que actualizarla). Luego se vuelve a ejecutar `E05`, que exporta `salidas/solicitudes_para_pad.csv` solo con los casos aprobados (C01 y C02). C03 queda en `pendientes_revision.json`.

### 2. Carga en la aplicación (PAD)

1. Comprobar que `salidas\bitacora_carga.csv` **no exista**. Si existe, el flujo se detiene con un mensaje de error, para no mezclar bitácoras.
2. Anotar el contador "Solicitudes guardadas" de la aplicación.
3. Ejecutar `Proyecto_RegistroSolicitudes_Lote` desde PAD y no intervenir durante el recorrido.
4. Revisar `salidas\bitacora_carga.csv` y comparar el contador antes y después.
5. Renombrar la bitácora antes de otra ejecución (por ejemplo `bitacora_prueba1.csv`).

## Flujo de PAD

El flujo no se entrega como archivo ejecutable: se reconstruye con las capturas de `Evidencias_RPA/` y `Cambios_Proyecto_Registro_Solicitudes_Lote/` y con esta descripción. Por cada fila del CSV hace lo siguiente:

1. Localiza la ventana con reintentos acotados (subflujo `LocalizarVentana`: 3 intentos, 2 s entre ellos).
2. Pulsa **Nueva solicitud**, captura los cinco campos con elementos de interfaz y pulsa **Registrar solicitud**.
3. Reconoce la respuesta de la aplicación (subflujo `EsperarDialogo`: hasta 10 s, una consulta por segundo).
4. Según la respuesta, decide el estado y lo escribe en la bitácora (`id_solicitud,folio,estado`):

| Estado | Significado |
|---|---|
| `REGISTRADA_VERIFICADA` | Se confirmó una sola vez, se leyó el folio real de la interfaz (empieza por `FOL-`) y quedó registrada. |
| `RECHAZADA_DATOS` | La aplicación mostró "Datos inválidos". |
| `YA_EXISTENTE` | La aplicación mostró "Solicitud duplicada". |
| `PENDIENTE_VERIFICACION` | Se confirmó, pero la espera se agotó. No se reenvía y el lote se detiene. |
| `REVISAR_RESPUESTA` | Respuesta no reconocida. El lote se detiene. |
| `FALLO_TECNICO` | No se pudo localizar la ventana tras los reintentos. El lote se detiene. |

### Elementos de interfaz para reconstruir el flujo

Ventanas localizadas por **título** (con la clase vacía): `Solicitudes RPA | Laboratorio de escritorio`, `Datos inválidos`, `Solicitud duplicada`, `Confirmar registro` y `Registro completado`.

Elementos de la aplicación:
- Botones `Nueva solicitud` y `Registrar solicitud`
- Cuadros de texto `Identificador de solicitud`, `Solicitante` y `Descripción`
- Combos `Área` y `Tipo de solicitud`
- Botón `Aceptar` (datos inválidos) y `Aceptar_SolicitudDuplicada`
- Botón `Boton_ConfirmarRegistro`
- Campo `Campo_FolioGenerado` (atributo `Own Text`) y botón `BotonAceptar_RegistroCompletado`

## Cambios realizados

- **`comun.py`, función `extraer_reglas`:** en la primera ejecución, las reglas solo reconocían campos con etiqueta al inicio de línea, y C02 (redactado en párrafo libre) solo devolvió `id_solicitud`. Se añadió un respaldo general (`PATRONES_LIBRES`) para las frases "presentada por", "área de", "tipo" y "Se solicita:". No contiene datos de ningún caso y marca cada campo rescatado como "requiere revisión humana". Se conservó la salida original (`reglas_v1_original`, `llm_simulado_v1_original` y `comun_v1_original.py`).
- **Flujo de PAD:** se partió de `Proyecto_RegistroSolicitudes_Lote_v1_original`. Se cambiaron `RutaCsv` y `RutaResultados` por las rutas del proyecto, se añadieron los subflujos `LocalizarVentana` y `EsperarDialogo`, la clasificación de respuestas, los seis estados de la bitácora y la detención del lote en estados inciertos. Se eliminó la comparación del folio contra el texto de la ventana.

## Pruebas

La matriz completa está en [`matriz_pruebas.xlsx`](matriz_pruebas.xlsx). Resumen (el contador inicial, 6, venía de registros de pruebas anteriores):

| # | Prueba | Resultado | Contador |
|---|---|---|---|
| 1 | Documento completo y aprobado | SOL-801 → FOL-0007 y SOL-802 → FOL-0008, `REGISTRADA_VERIFICADA` | 6 → 8 |
| 2 | Información ausente en C03 | C03 no está en el CSV ni en la bitácora; no se envió | sin cambio por C03 |
| 3 | Datos inválidos | SOL-901 `RECHAZADA_DATOS` | 8 → 8 |
| 4 | Identificador ya registrado | SOL-801 `YA_EXISTENTE` | 8 → 8 |
| 5 | Respuesta lenta, espera suficiente | SOL-902 → FOL-0009, `REGISTRADA_VERIFICADA` | 8 → 9 |
| 6 | Espera agotada tras confirmar | SOL-903 `PENDIENTE_VERIFICACION`; la comprobación posterior mostró FOL-0010 guardado, sin reenvío | 9 → 10 |
| 7 | Aplicación cerrada | SOL-904 `FALLO_TECNICO` tras 3 intentos | 10 → 10 |

Las pruebas de fallo se hicieron con CSV aparte (`solicitudes_prueba_*.csv`), sin modificar los documentos originales ni el CSV aprobado. La evidencia de cada una está en `Evidencia_Prueba1/` a `Evidencia_Prueba7/`.

## Limitaciones conocidas

- **La rama LLM es simulada.** Reutiliza las reglas y **no** mide el rendimiento de un modelo. No se usó ninguna API real ni clave.
- **Las reglas son estrictas.** Reconocen campos con etiqueta o las frases del respaldo; otras redacciones pueden fallar.
- **C03 permanece pendiente** porque su documento no contiene `Tipo`. No se completa ni se envía.
- **El flujo no hace por sí mismo la comprobación posterior** de un registro pendiente: se hizo observando la aplicación, sin reenviar.
- **Si una fila queda pendiente o incierta, el lote se detiene** y las filas siguientes no se procesan.
- **La bitácora no puede existir antes de ejecutar:** hay que moverla o renombrarla entre ejecuciones.
- **Dependencia de títulos de ventana y de la codificación:** si cambia el título de la aplicación, o el CSV no está en UTF-8, el flujo puede fallar.
- **Rutas absolutas en PAD:** deben ajustarse en cada equipo.
- **El flujo de PAD no se entrega como archivo ejecutable.** La ejecución en Windows se acredita con la bitácora, la matriz, las capturas y el video.
- En las pruebas 3 a 7, parámetros como `RutaCsv`, la espera de la rama `CONFIRMAR` (prueba 6) y el escenario de la aplicación se cambiaron temporalmente y se restauraron.

## Reflexión

Para evitar registrar datos incorrectos, separamos la extracción de la carga. Los textos OCR se procesaron con reglas, y cada uno de los cinco campos se comparó contra el documento original. Solo los casos completos, válidos y aprobados por una persona llegaron al CSV. C03 se quedó pendiente porque el documento no contiene Tipo, y no inventamos ese dato. Además, el formulario rechazó datos inválidos y el flujo lo registró como rechazo, no como éxito.

Para comprobar el guardado no confiamos en haber pulsado el botón. El flujo reconoce la ventana de respuesta, confirma una sola vez, lee el folio real de la interfaz, verifica que tenga el formato esperado y solo entonces registra la solicitud en la bitácora. También comparamos el contador antes y después de cada ensayo.

No todas las acciones pueden reintentarse porque algunas cambian el estado de la aplicación. Localizar una ventana se puede repetir sin riesgo, y por eso tiene un límite de tres intentos. Confirmar un registro no: en la prueba de espera agotada, el flujo se rindió, pero la solicitud sí se había guardado. Reenviarla habría creado un duplicado. Por eso conservamos el estado pendiente y comprobamos antes de actuar.

## Datos y protección de archivos

Todos los datos son ficticios. No se incluyen claves, archivos `.env`, entornos virtuales, cachés ni datos personales. `salidas/` está fuera de Git.
