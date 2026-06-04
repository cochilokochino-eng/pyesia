# -*- coding: utf-8 -*-
"""
analyzer.py
Analiza estructura, metrica y rima de una letra base usando pyesia.
"""
from generator import extract_template, _count_metric_syllables


def analyze_lyrics(lyrics_text):
    """Analiza la letra base y devuelve la plantilla prosodica.

    Parameters
    ----------
    lyrics_text : str
        Texto completo de la letra con secciones separadas por lineas en blanco.

    Returns
    -------
    dict
        Plantilla prosodica con estructura:
        {
            "sections": [...],
            "resumen": {
                "total_secciones": int,
                "total_versos": int,
                "rango_silabas": (min, max)
            }
        }
    """
    template = extract_template(lyrics_text)

    # Agregar resumen
    total_versos = 0
    all_syllables = []
    for section in template["sections"]:
        for line in section["lines"]:
            total_versos += 1
            all_syllables.append(line["metric_syllables"])

    template["resumen"] = {
        "total_secciones": len(template["sections"]),
        "total_versos": total_versos,
        "rango_silabas": (min(all_syllables), max(all_syllables)) if all_syllables else (0, 0),
    }

    return template


def format_template_report(template):
    """Genera un reporte legible de la plantilla prosodica.

    Parameters
    ----------
    template : dict
        Plantilla devuelta por analyze_lyrics.

    Returns
    -------
    str
        Reporte formateado en texto.
    """
    lines = []
    lines.append("# Plantilla Prosodica Detectada\n")
    resumen = template.get("resumen", {})
    lines.append(f"- Secciones: {resumen.get('total_secciones', '?')}")
    lines.append(f"- Versos totales: {resumen.get('total_versos', '?')}")
    rango = resumen.get("rango_silabas", (0, 0))
    lines.append(f"- Rango de silabas metricas: {rango[0]}-{rango[1]}")
    lines.append("")

    for section in template["sections"]:
        lines.append(f"## {section['name']}")
        lines.append("")
        for i, line in enumerate(section["lines"], 1):
            rima = line["rhyme_group"] or "-"
            lines.append(
                f"  {i}. [{line['metric_syllables']} silabas] "
                f"[rima: {rima}] {line['text']}"
            )
        if section.get("rhyme_endings"):
            lines.append(f"  Terminaciones de rima: {section['rhyme_endings']}")
        lines.append("")

    return "\n".join(lines)
