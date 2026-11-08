# Auditoría visual y técnica — versión 2

Fecha: 7 de noviembre de 2026.

## Estado contrastado

- **294 archivos PNG válidos** (98 familias × 3 estados), sin duplicados exactos.
- Resoluciones: **512×512: 219**; **1024×1024: 51**; **256×256: 21**; **512×256: 3**.
- Archivos RGBA: **21** corregidos con dilatación del color RGB hacia los bordes transparentes para evitar halos del filtrado.
- Verificación de continuidad exigida por la ficha: **0 errores** de bordes exactos (cero no garantiza repetición visual natural).
- **294 generados, 0 revisados en Blender, 0 aprobados artísticamente**. No equiparar generación con calidad final.
- Archivo `ESTADO_VERIFICADO.json` del ZIP antiguo desfasado (123 de 294). Corregido en `ESTADO_VERIFICADO_v2.json`.

## Prioridades

- **Crítica (6 PNG):** ramilletes de encina y ciprés. Morfología ilustrada, poco fotográfica. Rehacer con recortes fotográficos/licencia compatible y alfa limpio.
- **Alta (48 PNG):** olivo (bordes), corte de tronco (anillos esquemáticos), pizarra, paja y plomo (detalle limitado de fuente atlas), algunas fábricas de ladrillo y decoraciones de aspecto demasiado geométrico.
- **Media:** restantes. Deben pasar comprobación a escala de sprite y en edificios reales.

## Archivos de inspección

- `diagnostico_repeticion_9_materiales.jpg`: mosaicos de 3 × 2 y miniaturas de 128 px.
- `diagnostico_alfa_botanica.jpg`: recortes transparentes sobre fondos claro y oscuro.
- `preview_isometrico_blender_v2.py`: escena de evaluación ejecutable localmente. **No se ha ejecutado aquí (Blender no instalado)**.
- `progreso_produccion_v2.csv`: hashes actualizados, estados QA y prioridades por PNG.

## Condición para cerrar un material

1. Escala física y lenguaje de material consistentes.
2. Losas, sillares y tejas sin artefactos evidentes tras mosaico 3 × 3.
3. Recorte correcto sin halos, si procede.
4. Aspecto convincente en Blender a la resolución final del sprite y en la misma iluminación para las tres variantes.
5. Solo después cambiar `estado_qa=pendiente_blender` por `aprobada` y conservar captura de la prueba.

## Licencias

Los PNG de esta entrega fueron generados para el proyecto; no se ha incorporado ninguna fotografía descargada de terceros en esta revisión. Si se sustituyen recursos por fotos externos, utilizar preferiblemente CC0 y documentar fuente y licencia por fichero.
