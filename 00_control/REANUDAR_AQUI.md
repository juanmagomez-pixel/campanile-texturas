# Reanudar aquí — revisión de calidad v2

Fecha: 2026-11-07.

**Archivo maestro actualizado:** `paquete_texturas_renacimiento_v2.zip`. Este ZIP es autocontenido: **no requiere aplicar el parche anterior**.

## Estado real
- 294 de 294 archivos PNG generados y comprobados como imágenes válidas.
- 21 PNG RGBA con mejora técnica de color bajo transparencia, sin cambiar el alfa.
- 0 fallos de continuidad exacta de borde cuando la repetición es obligatoria.
- **0 materiales aprobados artísticamente**: la prueba en Blender está pendiente.
- Nombres, dimensiones, escalas y estructura originales preservados.

## Continuación recomendada
1. Abrir `00_control/revision_v2/AUDITORIA_CALIDAD_V2.md`.
2. En un equipo con Blender 4.x, ejecutar el script `00_control/preview_isometrico_blender_v2.py`, que produce un render a 1600 px y otro a 800 px; conservar imágenes del resultado.
3. Ver los materiales en cámara isométrica y marcar los prioritarios, empezando por las hojas de encina y ciprés (6 PNG), cortes de tronco y piezas decorativas.
4. Sustituir primero los resultados que parezcan dibujos; no modificar texturas por un criterio puramente numérico.
5. Tras aprobar un archivo, cambiar su estado en el manifiesto y registrar qué render lo valida.

## Guía rápida para Blender
Descomprime el ZIP. Desde la carpeta contenedora ejecuta:

`blender -b -P texturas_renacimiento_italiano/00_control/preview_isometrico_blender_v2.py`

Los renders aparecerán en `texturas_renacimiento_italiano/00_control/revision_v2/`.

## Transparencia y versiones
La mejora del alfa evita algunas franjas del filtrado de textura; no convierte las hojas procedimentales en fotografías. No se han introducido fotos de terceros ni cambios de licencia en este paquete.
