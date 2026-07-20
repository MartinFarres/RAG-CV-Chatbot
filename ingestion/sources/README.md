# Sources

Contenido fuente para la ingesta (`python run.py`). Cada subcarpeta
corresponde a un `tipo` de chunk distinto. Importante: los loaders
escanean cada carpeta con un glob (`*.md`, `*.csv`), así que **no pongas
archivos de documentación sueltos que calcen con esos globs acá
adentro** — se ingestarían como si fueran contenido real.

Todos los `.md` de `cv/`, `about_me/`, `certificados/` y `plan_estudio/`
pueden tener un frontmatter opcional (`---\nclave: valor\n---` al
inicio) para `nombre` y, en certificados, `fuente_url`. Un valor `null`
o vacío se trata como ausente.

## cv/

Uno o más `.md` con tu CV (lo normal es uno solo). El body (después del
frontmatter) se parte por heading (cualquier nivel `#`..`######`), así
que estructuralo con secciones reales:

```md
## Perfil
...

## Experiencia
### Proyecto A
...
### Proyecto B
...

## Certificaciones
...
```

Cada heading (Perfil, Experiencia, cada proyecto, Certificaciones) termina
siendo un chunk propio con `tipo="cv"`. `nombre` sale del frontmatter
(`nombre: "..."`) o, si no hay, es `"CV"`. Un heading sin texto debajo se
funde con el siguiente bloque en vez de generar un chunk vacío.

## readmes/

- `repos_links.md`: una URL de GitHub por línea (bullet `- https://github.com/owner/repo`).
  Son los proyectos públicos con buen README: se traen en vivo vía la
  API de GitHub en el momento de la ingesta. `nombre` = nombre del repo,
  `fuente_url` = esa misma URL.
- Cualquier otro `.md` en esta carpeta: un README ya escrito acá a mano,
  para repos privados (o sin buen README propio). `nombre` se toma del
  primer `# Heading` del archivo (o el nombre de archivo si no hay), y
  `fuente_url` de una línea `**Repositorio:** <url>` si está presente.

En ambos casos, si el doc es corto queda como un único chunk; si es
largo se parte por heading igual que el CV.

## certificados/

Un `.md` por certificado, contenido completo (no se parte: son cortos y
partirlos no aporta nada). `nombre` y `fuente_url` opcionales por
frontmatter; sin `nombre`, se toma del nombre del archivo.

## plan_estudio/

Dos formatos, se pueden combinar:

- `.csv` con una fila por materia, columnas:
  `anio_carrera,materia,seccion,estado,tipo_aprobacion,fecha,calificacion`.
  Cada fila es un chunk propio (`tipo="plan_estudio"`, `nombre` = la
  materia), para poder responder preguntas puntuales como "¿qué
  materias de IA aprobó?". `tipo_aprobacion`, `fecha` y `calificacion`
  son opcionales (ej. materias en curso, sin nota todavía).
- `.md` con un resumen narrativo (estado del alumno, promedio, etc.).
  Se parte por heading igual que el CV/README; `nombre` sale del
  frontmatter o del primer heading.

## about_me/

Un `.md` con preguntas como headings (`##`/`###`). Se parte por heading
igual que el CV: cada pregunta (o sub-área temática) es un chunk propio
(`tipo="about_me"`). `nombre` sale del frontmatter, si no del primer
`# Heading`, si no `"About Me"`.
