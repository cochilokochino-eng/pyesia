# -*- coding: utf-8 -*-
"""
app.py
Streamlit interface for Contrafactum AI.
"""
import streamlit as st
import pandas as pd

from generator import extract_template, generate_contrafactum
from validator import validate_lyrics
from repair import repair_lyrics, MAX_REPAIR_ATTEMPTS


st.set_page_config(page_title="Contrafactum AI", layout="wide")

st.title("Contrafactum AI")
st.markdown(
    "Genera nuevas letras que mantienen la estructura metrica, "
    "el esquema de rima y la organizacion en secciones de una cancion original."
)

# --- Sidebar inputs ---
with st.sidebar:
    st.header("Configuracion")

    base_lyrics = st.text_area(
        "Letra base (en espanol)",
        height=250,
        placeholder=(
            "Yo soy como el verde pino\n"
            "que en la sierra se ha criado\n\n"
            "Me gusta cantar bonito\n"
            "al pie de un encino parado"
        ),
    )

    theme = st.text_input(
        "Tema nuevo",
        placeholder="Ej: la nostalgia de un migrante en Estados Unidos",
    )

    style_options = [
        "Corrido mexicano",
        "Norteno clasico",
        "Banda",
        "Espiritual",
        "Bolero",
        "Cumbia",
        "Ranchera",
        "Personalizado",
    ]
    style = st.selectbox("Estilo musical", style_options)

    if style == "Personalizado":
        style = st.text_input(
            "Describe el estilo personalizado",
            placeholder="Ej: trova yucateca con influencia caribeña",
        )

    generate_btn = st.button("Generar Contrafactum", type="primary")

# --- Main area ---
if generate_btn:
    if not base_lyrics.strip():
        st.error("Por favor, pega una letra base.")
    elif not theme.strip():
        st.error("Por favor, escribe un tema nuevo.")
    else:
        # Step 1: Extract template
        with st.spinner("Analizando estructura metrica de la letra base..."):
            template = extract_template(base_lyrics)

        with st.expander("Plantilla metrica detectada", expanded=False):
            st.json(template)

        # Step 2: Generate contrafactum
        with st.spinner("Generando contrafactum con IA..."):
            try:
                generated = generate_contrafactum(template, theme, style)
            except ValueError as e:
                st.error(str(e))
                st.stop()
            except Exception as e:
                st.error(f"Error al generar: {e}")
                st.stop()

        # Step 3: Validate and repair loop
        with st.spinner("Validando y reparando..."):
            report = validate_lyrics(generated, template)
            attempts = 0
            while not report["valid"] and attempts < MAX_REPAIR_ATTEMPTS:
                try:
                    generated = repair_lyrics(generated, template, report)
                    report = validate_lyrics(generated, template)
                    attempts += 1
                except (ValueError, Exception):
                    break

        # --- Display results ---
        st.subheader("Letra generada")
        st.text(generated)

        # Metric report
        st.subheader("Reporte metrico")
        if report["lines"]:
            df = pd.DataFrame(report["lines"])
            df = df.rename(
                columns={
                    "section": "Seccion",
                    "line_num": "Verso",
                    "text": "Texto",
                    "expected_syllables": "Silabas esperadas",
                    "actual_syllables": "Silabas obtenidas",
                    "syllable_pass": "Silabas OK",
                    "expected_rhyme_group": "Grupo rima",
                    "rhyme_pass": "Rima OK",
                }
            )
            st.dataframe(df, use_container_width=True)

        # Rhyme report
        st.subheader("Reporte de rima")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total versos", report["summary"]["total_lines"])
        col2.metric("Versos correctos", report["summary"]["passed_lines"])
        col3.metric("Versos fallidos", report["summary"]["failed_lines"])

        # Failed lines
        failed = [
            line for line in report["lines"]
            if not (line["syllable_pass"] and line["rhyme_pass"])
        ]
        if failed:
            st.subheader("Versos con problemas")
            for fl in failed:
                reason = []
                if not fl["syllable_pass"]:
                    reason.append(
                        f"silabas: esperadas {fl['expected_syllables']}, "
                        f"obtenidas {fl['actual_syllables']}"
                    )
                if not fl["rhyme_pass"]:
                    reason.append(f"rima grupo {fl['expected_rhyme_group']}")
                st.warning(
                    f"Seccion {fl['section']}, verso {fl['line_num']}: "
                    f"\"{fl['text']}\" - {'; '.join(reason)}"
                )
        else:
            st.success("Todos los versos pasan la validacion metrica y de rima.")

        # Template at bottom
        with st.expander("Plantilla completa (JSON)", expanded=False):
            st.json(template)
