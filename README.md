# Pyesia: A toolbox for prosodic analysis of poetry in Spanish

Pyesia allows to perform automatic analysis of the prosody in of poetry written in Spanish. Currently, the main features are:

> Count syllables

> Localize tonic syllables

> Localize synalephas and synalephas-hyatus

> Detect rhyme

> Basic analysis of a poem verse by verse: Number of phological/metric syllables, position of the tonic syllables, final rhyme

> Basic plots showing the analysis

To do: Quantification of the number of syllables per tonic syllable.

Do you need another feature, you have new ideas? Please contact me at g.serranonajera@gmail.com


# Pyesia: Herramientas para el análisis prosódico de poesía en español

Pyesia permite el análisis automático de la prosodia de poesia en español. Actualmente, las principales características son:

> Contar de sílabas

> Localizar sílabas tónicas

> Localizar sinalefas y sinalefas-hiato

> Detectar rimas

> Analisis básico del poema verso a verso: Número de sílabas fonológicas/métricas, posición de las sílabas tónicas, rima final

> Gráficos básicos para mostrar los resultados del análisis

Por hacer: Cuantificación de número de sílabas por sílaba tónica.

¿Necesitas alguna otra herramient o tienes nuevas ideas? Por favor contáctame en g.serranonajera@gmail.com

---

# Contrafactum AI

Contrafactum AI is a local Streamlit application that generates contrafactum lyrics -- new lyrics that maintain the exact metric structure, rhyme scheme, and section layout of a base Spanish song, but with a completely different theme.

## How it works

1. **Template extraction**: Analyzes the base lyrics using pyesia's prosodic engine to detect syllable counts, rhyme patterns, and section structure.
2. **Generation**: Sends the metric template, your chosen theme, and style to an LLM (OpenAI or Anthropic) to produce new lyrics.
3. **Validation**: Checks that the generated lyrics match the original metric structure (syllable count within +/-1) and rhyme scheme.
4. **Repair**: If lines fail validation, automatically asks the LLM to rewrite only the failing lines (up to 3 attempts).

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

Set your LLM provider API key as an environment variable:

```bash
# For OpenAI (default)
export OPENAI_API_KEY="your-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-key-here"
export CONTRAFACTUM_PROVIDER="anthropic"
```

## Usage

```bash
streamlit run app.py
```

Then in the browser:

1. Paste a base lyric in Spanish
2. Write a new theme
3. Choose a style (corrido mexicano, norteno clasico, banda, espiritual, etc.)
4. Click "Generar Contrafactum"
5. View the generated lyrics, metric report, rhyme report, and any failed lines
