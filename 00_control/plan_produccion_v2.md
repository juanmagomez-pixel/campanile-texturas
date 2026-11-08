# Plan de producción de texturas realistas (v2)

**Objetivo:** materiales físicamente plausibles para edificios italianos (siglos XIV-XVI), renderizados en Blender y usados en videojuego isométrico al estilo de referencias realistas como Manor Lords. Sin cel shading, pintura ni apariencia de dibujos animados.

**Progreso actual:** 294/294 PNG generados como prototipos. Catálogo completo en cantidad. Pendiente validación artística, histórica y Blender: las fuentes L02-L16 en su mayoría procedimentales.

**Resoluciones:** 512px principal, 1024px ornamentos complejos, 256px auxiliares, 512×256 en la capa de humedad. Las dimensiones se pueden ajustar tras inspeccionar un render a la escala real de juego.

**Variantes:** `a` cuidada, `b` usada, `c` vieja. Cada material conserva sus características geográficas e históricas.

## Lotes y orden de trabajo

| Lote | Tema | Materiales | PNG | Archivo de entrega |
|---|---|---:|---:|---|
| L01 | comunes tejados | 5 | 15 | `lote_01_comunes_tejados.zip` |
| L02 | comunes muros | 6 | 18 | `lote_02_comunes_muros.zip` |
| L03 | comunes piedra noble | 7 | 21 | `lote_03_comunes_piedra_noble.zip` |
| L04 | comunes marmoles columnas | 6 | 18 | `lote_04_comunes_marmoles_columnas.zip` |
| L05 | comunes vidrio decoracion | 5 | 15 | `lote_05_comunes_vidrio_decoracion.zip` |
| L06 | comunes madera arboles | 8 | 24 | `lote_06_comunes_madera_arboles.zip` |
| L07 | comunes suelos campos | 8 | 24 | `lote_07_comunes_suelos_campos.zip` |
| L08 | florencia | 4 | 12 | `lote_08_florencia.zip` |
| L09 | venecia | 5 | 15 | `lote_09_venecia.zip` |
| L10 | milan | 4 | 12 | `lote_10_milan.zip` |
| L11 | genova | 4 | 12 | `lote_11_genova.zip` |
| L12 | roma | 5 | 15 | `lote_12_roma.zip` |
| L13 | palermo | 5 | 15 | `lote_13_palermo.zip` |
| L14 | detalles puertas envejecimiento | 9 | 27 | `lote_14_detalles_puertas_envejecimiento.zip` |
| L15 | detalles oficios | 11 | 33 | `lote_15_detalles_oficios.zip` |
| L16 | detalles obras murallas | 6 | 18 | `lote_16_detalles_obras_murallas.zip` |

## Catálogo completo por material

| ID | Lote | Ciudad / grupo | Material | Resolución | Escala física | Repetición | Alfa |
|---|---|---|---|---|---|---|---|
| T001 | L01 | Comunes | Teja árabe roja | 512×512 | 2×2metros | ambos | no |
| T002 | L01 | Comunes | Teja oscura y vieja | 512×512 | — | ambos | no |
| T003 | L01 | Comunes | Pizarra | 512×512 | 2×2metros | ambos | no |
| T004 | L01 | Comunes | Paja de techumbre | 512×512 | 2×2metros | ambos | no |
| T005 | L01 | Comunes | Plomo de cúpula | 512×512 | 2×2metros | ambos | no |
| T006 | L02 | Comunes | Enlucido claro gastado | 512×512 | 2×2metros | ambos | no |
| T007 | L02 | Comunes | Enlucido viejo con desconchones | 512×512 | 2×2metros | ambos | no |
| T008 | L02 | Comunes | Adobe | 512×512 | 2×2metros | ambos | no |
| T009 | L02 | Comunes | Ladrillo toscano | 512×512 | 1,5×1,5metros | ambos | no |
| T010 | L02 | Comunes | Ladrillo lombardo | 512×512 | 1,5×1,5metros | ambos | no |
| T011 | L02 | Comunes | Mampostería de zócalo | 512×512 | 2×2metros | ambos | no |
| T012 | L03 | Comunes | Piedra serena en sillares | 512×512 | 3×3metros | ambos | no |
| T013 | L03 | Comunes | Almohadillado rústico | 1024×1024 | 3×3metros | ambos | no |
| T014 | L03 | Comunes | Travertino | 512×512 | 3×3metros | ambos | no |
| T015 | L03 | Comunes | Mármol blanco y verde | 1024×1024 | 3×3metros | ambos | no |
| T016 | L03 | Comunes | Piedra a franjas blancas y negras | 512×512 | 3×3metros | ambos | no |
| T017 | L03 | Comunes | Toba dorada | 512×512 | 3×3metros | ambos | no |
| T018 | L03 | Comunes | Piedra de Istria | 512×512 | 3×3metros | ambos | no |
| T019 | L04 | Comunes | Mármol blanco de Carrara | 512×512 | 1×1metro | ambos | no |
| T020 | L04 | Comunes | Mármol verde de Prato | 512×512 | 1×1metro | ambos | no |
| T021 | L04 | Comunes | Mármol rosa de Maremma | 512×512 | 1×1metro | ambos | no |
| T022 | L04 | Comunes | Mármol rojo de Verona | 512×512 | 1×1metro | ambos | no |
| T023 | L04 | Comunes | Piedra serena lisa | 256×256 | 1×1metro | ambos | no |
| T024 | L04 | Comunes | Piedra clara labrada | 256×256 | 1×1metro | ambos | no |
| T025 | L05 | Comunes | Vidrio emplomado de rulli | 1024×1024 | 1×1metro | ambos | no |
| T026 | L05 | Comunes | Vidrio de cuarterones | 1024×1024 | 1×1metro | ambos | no |
| T027 | L05 | Comunes | Vidriera de iglesia | 1024×1024 | 1×1metro | ambos | no |
| T028 | L05 | Comunes | Esgrafiado florentino | 1024×1024 | 2×2metros | ambos | no |
| T029 | L05 | Comunes | Terracota decorativa | 1024×1024 | 1×1metro | ambos | no |
| T030 | L06 | Comunes | Vigas viejas | 512×512 | 1×1metro | ambos | no |
| T031 | L06 | Comunes | Tablas de puertas y contraventanas | 512×512 | 1×1metro | ambos | no |
| T032 | L06 | Comunes | Corteza de olivo y encina | 512×512 | 1×1metro | ambos | no |
| T033 | L06 | Comunes | Corteza de ciprés y pino | 512×512 | 1×1metro | ambos | no |
| T034 | L06 | Comunes | Ramillete de hojas de olivo | 512×512 | — | no | sí |
| T035 | L06 | Comunes | Ramillete de hojas de encina | 512×512 | — | no | sí |
| T036 | L06 | Comunes | Ramillete de ciprés | 512×512 | — | no | sí |
| T037 | L06 | Comunes | Corte de tronco | 512×512 | — | no | sí |
| T038 | L07 | Comunes | Losas de piedra | 512×512 | 2×2metros | ambos | no |
| T039 | L07 | Comunes | Tierra apisonada | 512×512 | 2×2metros | ambos | no |
| T040 | L07 | Comunes | Grava | 512×512 | 2×2metros | ambos | no |
| T041 | L07 | Comunes | Toldo de lino | 512×512 | 1×1metro | ambos | no |
| T042 | L07 | Comunes | Tierra arada | 512×512 | 2×2metros | ambos | no |
| T043 | L07 | Comunes | Hierba corta | 512×512 | 2×2metros | ambos | no |
| T044 | L07 | Comunes | Arcilla húmeda | 512×512 | 2×2metros | ambos | no |
| T045 | L07 | Comunes | Vertedero | 512×512 | 2×2metros | ambos | no |
| T046 | L08 | Florencia | Pietraforte ocre | 512×512 | 3×3metros | ambos | no |
| T047 | L08 | Florencia | Revoque florentino ocre y crema | 512×512 | 2×2metros | ambos | no |
| T048 | L08 | Florencia | Teja florentina con tejas de caballete | 1024×1024 | 2×2metros | ambos | no |
| T049 | L08 | Florencia | Empedrado de lastrone | 512×512 | 3×3metros | ambos | no |
| T050 | L09 | Venecia | Ladrillo veneciano y revoque rojo | 512×512 | 2×2metros | ambos | no |
| T051 | L09 | Venecia | Teja veneciana clara | 1024×1024 | 2×2metros | ambos | no |
| T052 | L09 | Venecia | Masegni de traquita | 512×512 | 2×2metros | ambos | no |
| T053 | L09 | Venecia | Mármol rojo veneciano y piedra de Istria juntos | 1024×1024 | 1×1metro | ambos | no |
| T054 | L09 | Venecia | Madera de pilotes y barcos | 512×512 | 1×1metro | ambos | no |
| T055 | L10 | Milán | Ceppo lombardo | 512×512 | 3×3metros | ambos | no |
| T056 | L10 | Milán | Revoque lombardo | 512×512 | 2×2metros | ambos | no |
| T057 | L10 | Milán | Teja lombarda oscura | 1024×1024 | 2×2metros | ambos | no |
| T058 | L10 | Milán | Rizada de cantos rodados | 512×512 | 2×2metros | ambos | no |
| T059 | L11 | Génova | Fachada pintada genovesa | 1024×1024 | 3×3metros | ambos | no |
| T060 | L11 | Génova | Fachada rosa genovesa | 1024×1024 | 3×3metros | ambos | no |
| T061 | L11 | Génova | Persianas genovesas verdes | 1024×1024 | 1×1metro | ambos | no |
| T062 | L11 | Génova | Pavimento de ladrillo y pizarra | 512×512 | 2×2metros | ambos | no |
| T063 | L12 | Roma | Ladrillo romano antiguo | 512×512 | 1,5×1,5metros | ambos | no |
| T064 | L12 | Roma | Peperino gris | 512×512 | 3×3metros | ambos | no |
| T065 | L12 | Roma | Revoque amarillo romano | 512×512 | 2×2metros | ambos | no |
| T066 | L12 | Roma | Sampietrini | 512×512 | 2×2metros | ambos | no |
| T067 | L12 | Roma | Mosaico cosmatesco | 1024×1024 | 2×2metros | ambos | no |
| T068 | L13 | Palermo | Revoque claro siciliano | 512×512 | 2×2metros | ambos | no |
| T069 | L13 | Palermo | Cúpula roja árabe-normanda | 512×512 | 2×2metros | ambos | no |
| T070 | L13 | Palermo | Arcos ciegos entrelazados | 1024×1024 | 3×3metros | horizontal | no |
| T071 | L13 | Palermo | Mayólica siciliana | 1024×1024 | 1×1metro | ambos | no |
| T072 | L13 | Palermo | Basalto del Etna | 512×512 | 2×2metros | ambos | no |
| T073 | L14 | Detalles | Portón claveteado | 512×512 | 2×2metros | no | no |
| T074 | L14 | Detalles | Puerta de casa humilde | 512×512 | 1×1metro | no | no |
| T075 | L14 | Detalles | Contraventanas de tablas | 512×512 | 1×1metro | no | no |
| T076 | L14 | Detalles | Contraventanas pintadas de verde | 512×512 | 1×1metro | no | no |
| T077 | L14 | Detalles | Reja de hierro forjado | 512×512 | — | no | sí |
| T078 | L14 | Detalles | Hierro oxidado | 256×256 | 0,5×0,5metros | ambos | no |
| T079 | L14 | Detalles | Musgo y liquen sobre teja | 256×256 | 2×2metros | ambos | sí |
| T080 | L14 | Detalles | Suciedad de lluvia | 256×256 | 2×2metros | horizontal | no |
| T081 | L14 | Detalles | Humedad en la base | 512×256 | 2×1metros | horizontal | no |
| T082 | L15 | Detalles | Sacos de arpillera | 256×256 | 1×1metro | ambos | no |
| T083 | L15 | Detalles | Leña apilada | 512×512 | 1×1metro | ambos | no |
| T084 | L15 | Detalles | Heno y paja suelta | 512×512 | 2×2metros | ambos | no |
| T085 | L15 | Detalles | Mineral de hierro | 512×512 | 2×2metros | ambos | no |
| T086 | L15 | Detalles | Escoria y carbón | 512×512 | 2×2metros | ambos | no |
| T087 | L15 | Detalles | Frente de cantera de mármol | 512×512 | 3×3metros | ambos | no |
| T088 | L15 | Detalles | Duelas de tonel | 512×512 | 1×1metro | no | no |
| T089 | L15 | Detalles | Cerámica cocida apilada | 512×512 | 1×1metro | no | no |
| T090 | L15 | Detalles | Redes de pesca | 512×512 | — | ambos | sí |
| T091 | L15 | Detalles | Telas de seda | 512×512 | 1×1metro | no | no |
| T092 | L15 | Detalles | Cuero curtido | 256×256 | 0,5×0,5metros | ambos | no |
| T093 | L16 | Detalles | Madera de andamio | 512×512 | 1×1metro | ambos | no |
| T094 | L16 | Detalles | Piedra en bruto | 512×512 | 2×2metros | ambos | no |
| T095 | L16 | Detalles | Cal y mortero | 512×512 | 2×2metros | ambos | no |
| T096 | L16 | Detalles | Sillares de muralla | 512×512 | 4×4metros | ambos | no |
| T097 | L16 | Detalles | Muralla de ladrillo con piedra | 512×512 | 4×4metros | ambos | no |
| T098 | L16 | Detalles | Tierra pisada de cuartel | 512×512 | 2×2metros | ambos | no |

## Validación por archivo

1. Control visual: materia realista, sin aspecto plástico ni dibujo, contraste adecuado al render final.
2. Verificar dimensiones, formato PNG y transparencia cuando proceda.
3. Para texturas repetibles, montar un mosaico 3×3 y corregir discontinuidades visibles entre bordes.
4. Mantener la escala física, las direcciones de junta y la ausencia de sombras proyectadas.
5. Marcar `generada`, `revisada`, `entregada` sucesivamente solo después de completar realmente cada fase.
6. Crear un ZIP por lote que contenga los PNG finales del lote y copia del manifiesto actualizado.

## Instrucción para continuar

Si se corta la conversación: subir el ZIP de control o el último ZIP de lote y pedir: «Continúa el proyecto de texturas del Renacimiento desde el primer estado pendiente del manifiesto. Respeta las resoluciones, la escala física y la estética fotográfica realista. No rehagas las variantes entregadas».

La copia del manifiesto es imprescindible: el historial del chat no sustituye a los ficheros guardados.
