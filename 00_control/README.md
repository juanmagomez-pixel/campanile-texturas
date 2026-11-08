# Texturas del Renacimiento italiano — 294 PNG de preproducción

**Versión:** 2026-11-07 / 01 · **Estado:** catálogo completo en número de archivos; **no aprobado artísticamente**.

## Uso previsto
Generar y renderizar edificios italianos de los siglos XIV–XVI en Blender para juego de estrategia de ciudades isométricas, con materiales de aspecto natural y envejecimiento moderado. Referencia visual: Age of Empires / Manor Lords, evitando dibujos animados.

## Contenido
- **98 materiales × 3 variantes a/b/c = 294 PNG** (a=cuidada; b=usada; c=vieja).
- L01–L16 incluidos; seis ciudades: Florencia, Venecia, Milán, Génova, Roma y Palermo.
- 256×256, 512×512 y 1024×1024, según resolución de cada material; una capa de humedad es 512×256.
- RGBA en hojas, corte de tronco, reja de hierro, musgo y red de pesca; otros PNG normalmente RGB.
- Materiales `repeticion=ambos` tienen bordes verticales y horizontales iguales; `horizontal` solo en los laterales; `no` no son mosaicos.
- Cada PNG tiene SHA-256 verificado en `progreso_produccion.csv` y `verificacion_total.json`.

## Advertencia sobre calidad
**Estos archivos son prototipos, no un paquete visual final**. Su tamaño y su continuidad de bordes se han comprobado, pero no se ha hecho una prueba real en Blender ni una inspección histórica material por material. La mayoría de texturas L02–L16 se han elaborado por procedimiento y pueden parecer demasiado sintéticas. En particular, los ramilletes de encina/ciprés parecen ilustrados y necesitan reemplazo si el objetivo es acabado fotográfico; el olivo procede de una generación de imagen y se ha limpiado el halo, pero conviene comprobar el alfa. Las muestras L01 de pizarra, paja y plomo provienen de recortes de una lámina y tienen menor definición efectiva que su resolución nominal.

**Tampoco se han medido todos los elementos con la precisión histórica deseada.** Revisar el paso de las hiladas de teja, ladrillo, sillares y los patrones arquitectónicos locales.

## Archivos de control
- `00_control/progreso_produccion.csv`: fuente de verdad; estado `generada` NO significa `revisada` ni `entregada`.
- `00_control/catalogo_texturas_v2.json`: descripción, tamaño físico y ruta de cada textura.
- `00_control/REANUDAR_AQUI.md`: instrucciones para continuar la validación en otra conversación.
- `00_control/verificacion_total.json`: hashes, resoluciones, alfa y error máximo de bordes.
- `00_control/REVISION_ARTISTICA.md`: prioridades para convertir los prototipos en arte definitivo.
- `00_control/generadores/`: los scripts de construcción usados por cada lote.
- `00_control/fuentes_lote01/` y `00_control/fuentes_lote06/`: fuentes generadas que deben conservarse si se quieren reexportar texturas.
- `00_control/preview_*`: láminas de inspección y mosaicos 3x3.

## Blender
Los PNG son mapas de Base Color, no contienen normal, height, roughness ni geometría. Cargar en Image Texture con color sRGB, extension Repeat cuando proceda y UV proporcionales a los metros de la ficha original. No hornear luces dentro del albedo. Renderizar una calle completa desde cámara isométrica antes de aprobar los materiales, incluyendo 15-20 edificios del mismo tipo para detectar patrones que se repiten.

## Nota para Godot
Si Blender exporta imágenes 2D de edificios/sprites, los 294 PNG normalmente NO necesitan importarse a Godot como texturas individuales; se usan como fuentes de render en Blender. Debe optimizarse el atlas de sprites renderizados final según resolución y zoom del juego.

## Retomar sin depender del historial
Conservar este ZIP y adjuntarlo al nuevo chat. Pedir: «Lee 00_control/REANUDAR_AQUI.md y realiza la validación artística y en Blender, comenzando por los materiales más sintéticos». No rehacer lo que esté validado ni dar por aprobado un archivo por el simple hecho de existir.


## Revisión de calidad v2 (7/11/2026)
- Corrección del color RGB bajo alfa en los 21 PNG con transparencia, conservando el canal alfa.
- Restablecida la coincidencia exacta de bordes en los mosaicos repetibles.
- Recalculados los 294 SHA256 de los PNG y el estado de avance correcto.
- Comparativas visuales y script actualizado `preview_isometrico_blender_v2.py`.
- **No son texturas finales fotográficas aprobadas**; quedan 0/294 validadas en Blender.
- Leer `00_control/revision_v2/AUDITORIA_CALIDAD_V2.md`.
