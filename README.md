# Contrafactum CLI

Herramienta de linea de comandos para generar contrafactums a partir de una letra base en espanol.

Un **contrafactum** es una nueva letra que mantiene la estructura metrica, el esquema de rima y la organizacion en secciones de la cancion original, pero con un tema completamente diferente.

## Requisitos

- Python 3.9+
- API key de OpenAI o Anthropic

## Instalacion

```bash
pip install -e .
pip install -r requirements.txt
```

## Configuracion

Configura tu API key como variable de entorno:

```bash
# Para OpenAI (default)
export OPENAI_API_KEY="tu-api-key"

# Para Anthropic
export ANTHROPIC_API_KEY="tu-api-key"
export CONTRAFACTUM_PROVIDER="anthropic"
```

## Uso

1. Pega tu letra base en `inputs/letra_base.txt`.

2. Ejecuta el script:

```bash
python contrafactum.py --tema "Corrido para el Dia del Padre" --estilo "corrido norteno clasico mexicano"
```

3. Resultados:
   - `outputs/contrafactum.md` - La letra generada
   - `outputs/reporte.md` - Reporte tecnico con validacion de metrica y rima

## Argumentos

| Argumento | Requerido | Descripcion |
|-----------|-----------|-------------|
| `--tema` | Si | Tema nuevo para el contrafactum |
| `--estilo` | Si | Estilo musical deseado |
| `--input` | No | Archivo de entrada (default: `inputs/letra_base.txt`) |
| `--output` | No | Archivo de salida para la letra (default: `outputs/contrafactum.md`) |
| `--reporte` | No | Archivo de salida para el reporte (default: `outputs/reporte.md`) |

## Ejemplos

```bash
# Corrido para el Dia del Padre
python contrafactum.py --tema "Corrido para el Dia del Padre" --estilo "corrido norteno clasico mexicano"

# Bolero romantico
python contrafactum.py --tema "Amor a distancia" --estilo "bolero clasico"

# Cumbia festiva
python contrafactum.py --tema "La fiesta del pueblo" --estilo "cumbia nortena"

# Usar un archivo de entrada diferente
python contrafactum.py --tema "Mi pueblo" --estilo "ranchera" --input mi_letra.txt
```

## Como funciona

1. **Lectura** - Lee la letra base de `inputs/letra_base.txt`
2. **Analisis** - Detecta estructura, secciones, lineas, metrica y patron de rima usando pyesia
3. **Plantilla** - Crea una plantilla tecnica con silabas metricas y grupos de rima por verso
4. **Generacion** - Genera una nueva letra via LLM respetando la plantilla
5. **Validacion** - Verifica que la letra generada cumpla con metrica y rima
6. **Reparacion** - Reescribe solo los versos que fallaron (hasta 3 intentos)
7. **Salida** - Guarda letra final y reporte tecnico

## Estructura del proyecto

```
contrafactum.py    - CLI principal
analyzer.py        - Analisis de estructura, metrica y rima
generator.py       - Generacion de contrafactum via LLM
validator.py       - Validacion de metrica y rima
repair.py          - Reparacion de versos fallidos
prompts.py         - Prompts para el LLM
inputs/            - Letras base de entrada
outputs/           - Letras generadas y reportes
pyesia/            - Libreria de analisis prosodico
```

## Pyesia

Este proyecto utiliza [pyesia](https://github.com/cochilokochino-eng/pyesia), una libreria de analisis prosodico para poesia en espanol que proporciona:

- Conteo de silabas metricas
- Deteccion de sinalefas
- Clasificacion de versos (agudos, llanos, esdrujulos)
- Deteccion de esquema de rima (consonante y asonante)
