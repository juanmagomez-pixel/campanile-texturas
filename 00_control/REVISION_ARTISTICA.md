# Lista de control para revisión artística e histórica

## Prioridad crítica
1. Sustituir `ramillete_encina_*` y `ramillete_cipres_*` si en el juego se ven como dibujos (los prototipos actuales son procedimentales, no fotográficos).
2. Revisar `corte_tronco_*` por el patrón concéntrico y el borde de corteza, que podrían parecer demasiado uniformes.
3. Revisar halos y contorno de `ramillete_olivo_*` sobre fondos claros, oscuros y en cámara isométrica.
4. Rehacer en foto/escaneo L01 `pizarra_liguria`, `paja_techumbre`, `plomo_cupula` si sus recortes muestran pérdida de detalle.

## Prioridad alta
5. Revisar fachadas geométricas y ornamentos: `mosaico_cosmatesco`, `mayolica_siciliana`, `arcos_entrelazados`, `esgrafiado_florentino`, `terracota_decorativa`: comprobar iconografía y evitar aspecto vectorial.
6. Revisar grupos de ladrillo, mampostería, tejas y lajas: bordes alineados no bastan para asegurar un mosaico natural. Ver todos los preview 3×3 y repetir sobre superficies de 3×3 metros.
7. Comprobar diferencias históricas y cronológicas: siglo XIV, XV y XVI; no atribuir una técnica posterior a 1494–1530 sin justificarlo.
8. Ajustar escala de tejas, sillares, ladrillos, plantas, puertas y juntas según el modelo en metros.

## Validaciones en Blender
9. Crear escena de prueba con una vivienda humilde, casa mercantil, palacio, iglesia y tramo de muralla usando materiales regionales.
10. Renderizar a resolución real de sprite: revisar que detalles importantes se lean a 100%, sin ruido subpíxel.
11. Revisar color/albedo bajo iluminación diurna neutra y perspectiva isométrica, sin sombras dibujadas.
12. Colocar 15–20 construcciones iguales y verificar repetición/variante a/b/c; si se reconocen patrones, diversificar por offsets UV o más materiales.

## Puerta de calidad
Solo pasar `estado=generada` a `estado=revisada` cuando se confirme material, nitidez, seamless visual y fidelidad histórica. Pasar a `entregada` únicamente si la textura final se ha integrado con éxito en la librería de materiales del juego.


## Actualización 2026-11-07 (v2)
Se han corregido los colores transparentes de 21 PNG y revisado el manifiesto.
Los 294 PNG están generados, pero ninguno se considera aprobado en Blender.
La revisión detallada está en `revision_v2/AUDITORIA_CALIDAD_V2.md`.
