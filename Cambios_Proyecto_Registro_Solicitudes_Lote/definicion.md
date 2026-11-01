Rutas: RutaCsv ahora apunta a solicitudes_para_pad.csv (CSV aprobado) y RutaResultados a bitacora_carga.csv.
El bloque inicial se detiene con mensaje de error si la bitácora ya existe.
Se agregó el subflujo LocalizarVentana: máximo 3 intentos con 2 s entre cada uno; si se agotan, se registra FALLO_TECNICO y se detiene el lote.
Se agregó el subflujo EsperarDialogo: consulta durante un máximo de 10 s si aparece “Datos inválidos”, “Solicitud duplicada”, “Confirmar registro” o “Registro completado”.
Después de Registrar solicitud, el flujo clasifica la respuesta: RECHAZADA_DATOS, YA_EXISTENTE, PENDIENTE_VERIFICACION (confirma una sola vez y vuelve a esperar) o REGISTRADA_VERIFICADA (solo si el folio leído de la interfaz no está vacío y empieza por FOL-).
La bitácora registra id_solicitud,folio,estado por cada fila, con el estado real.
Si una fila queda en PENDIENTE_VERIFICACION o REVISAR_RESPUESTA, el lote se detiene, para no actuar sobre una pantalla incierta ni reenviar una solicitud que pudo haberse guardado.
Se eliminó la comparación del folio contra el texto de la ventana.
