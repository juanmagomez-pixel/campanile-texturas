# Validación de materiales en Blender

Se incluyen 294 PNG, sin que ninguno se considere aún aprobado artísticamente.
La escena de prueba utiliza tres volúmenes de diagnóstico: vivienda humilde, casa de mercader y casa rica. **No pretende representar modelos históricos acabados.**

## Windows

1. Descomprimir el ZIP maestro conservando las carpetas.
2. Abrir la carpeta `texturas_renacimiento_italiano/00_control`.
3. Ejecutar `EJECUTAR_VALIDACION_BLENDER.bat` con Blender 4.x o 5.x instalado.
4. Abrir `00_control/revision_v2/blender_validacion_1600.png` y `blender_validacion_800.png`.

Si Blender no aparece en PATH y no está instalado en la ruta habitual, ejecutar manualmente desde una terminal:

```
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" -b -P "texturas_renacimiento_italiano\00_control\preview_isometrico_blender_v2.py"
```

Sustituir `Blender 4.x` por el nombre real de la carpeta.

## Checklist visual

- Comprobar el realismo a **800 px de anchura**; la textura no debe volverse ruido de píxeles ni perder su patrón material.
- Comprobar a 1600 px que el albedo no tiene sombras simuladas de una luz fija.
- En los planos de tejas, comprobar escala y orientación; las líneas de cubierta no deben mostrar mosaicos repetidos demasiado pronto.
- Comprobar juntas de ladrillo, sillares y escalado de piedra y parquet según las fichas en metros.
- Evaluar la coherencia de color con la misma luz para vivienda humilde, casa de mercader y palacio.
- No aprobar los materiales botánicos solo con el test de edificios: necesitan plano de follaje aparte.

## Estados

Conservar `generada` hasta completar la revisión. Marcar `revisada` en el CSV solo cuando exista captura visual aprobada y motivo; `entregada` solo tras su incorporación al proyecto.
