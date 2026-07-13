"""Lista de proyectos a ingestar como chunks de tipo "proyecto".

Cada entrada necesita "nombre" y exactamente una fuente:
- "github": "owner/repo" -> se trae el README.md vía la API de GitHub.
- "local_file": ruta relativa a ingestion/sources/readmes/ -> se usa tal
  cual, sin pegarle a GitHub (para repos privados que no se pueden traer).

"fuente_url" es opcional; si no se especifica, para las entradas "github"
se arma como https://github.com/<owner>/<repo>.
"""

PROJECTS: list[dict[str, str]] = [
    # {"nombre": "LoadBalancerAutoScaler-DRL", "github": "MartinFarres/LoadBalancerAutoScaler-DRL"},
    # {"nombre": "Proyecto Privado", "local_file": "readmes/proyecto_privado.md", "fuente_url": "https://..."},
]
