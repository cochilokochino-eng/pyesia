# -*- coding: utf-8 -*-
"""
contrafactum.py
CLI para generar contrafactums a partir de una letra base.

Uso:
    python contrafactum.py --tema "Corrido para el Dia del Padre" --estilo "corrido norteno clasico mexicano"
"""
import argparse
import os
import sys
import json
from datetime import datetime

from analyzer import analyze_lyrics, format_template_report
from generator import generate_contrafactum
from validator import validate_lyrics
from repair import repair_lyrics, MAX_REPAIR_ATTEMPTS


INPUT_FILE = os.path.join("inputs", "letra_base.txt")
OUTPUT_LYRICS = os.path.join("outputs", "contrafactum.md")
OUTPUT_REPORT = os.path.join("outputs", "reporte.md")


def read_input(path):
    """Lee la letra base del archivo de entrada."""
    if not os.path.exists(path):
        print(f"Error: No se encontro el archivo '{path}'")
        print("Pega tu letra base en inputs/letra_base.txt antes de ejecutar.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print(f"Error: El archivo '{path}' esta vacio.")
        print("Pega tu letra base en inputs/letra_base.txt antes de ejecutar.")
        sys.exit(1)

    return text


def save_output(path, content):
    """Guarda contenido en un archivo de salida."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_report(template, validation_report, tema, estilo, attempts_used):
    """Construye el reporte tecnico en formato markdown."""
    lines = []
    lines.append("# Reporte Tecnico - Contrafactum\n")
    lines.append(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Tema:** {tema}")
    lines.append(f"**Estilo:** {estilo}")
    lines.append(f"**Intentos de reparacion:** {attempts_used}")
    lines.append("")

    # Resumen de validacion
    summary = validation_report["summary"]
    lines.append("## Resumen de Validacion\n")
    lines.append(f"- Total de versos: {summary['total_lines']}")
    lines.append(f"- Versos correctos: {summary['passed_lines']}")
    lines.append(f"- Versos con problemas: {summary['failed_lines']}")
    sec_check = validation_report["section_count"]
    lines.append(
        f"- Secciones: {sec_check['got']}/{sec_check['expected']} "
        f"({'OK' if sec_check['pass'] else 'FALLO'})"
    )
    lines.append("")

    # Detalle por verso
    lines.append("## Detalle por Verso\n")
    lines.append("| Seccion | Verso | Silabas esperadas | Silabas obtenidas | Silabas OK | Rima OK | Texto |")
    lines.append("|---------|-------|-------------------|-------------------|------------|---------|-------|")
    for entry in validation_report["lines"]:
        syl_ok = "SI" if entry["syllable_pass"] else "NO"
        rhy_ok = "SI" if entry["rhyme_pass"] else "NO"
        text_short = entry["text"][:40] + "..." if len(entry["text"]) > 40 else entry["text"]
        lines.append(
            f"| {entry['section']} | {entry['line_num']} | "
            f"{entry['expected_syllables']} | {entry['actual_syllables']} | "
            f"{syl_ok} | {rhy_ok} | {text_short} |"
        )
    lines.append("")

    # Plantilla detectada
    lines.append("## Plantilla Prosodica Detectada\n")
    lines.append(format_template_report(template))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Genera un contrafactum a partir de una letra base.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplo:\n"
            '  python contrafactum.py --tema "Corrido para el Dia del Padre" '
            '--estilo "corrido norteno clasico mexicano"\n\n'
            "Antes de ejecutar, pega tu letra base en inputs/letra_base.txt"
        ),
    )
    parser.add_argument(
        "--tema",
        required=True,
        help="Tema nuevo para el contrafactum.",
    )
    parser.add_argument(
        "--estilo",
        required=True,
        help="Estilo musical (ej: corrido norteno clasico mexicano).",
    )
    parser.add_argument(
        "--input",
        default=INPUT_FILE,
        help=f"Archivo de letra base (default: {INPUT_FILE}).",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_LYRICS,
        help=f"Archivo de salida para la letra (default: {OUTPUT_LYRICS}).",
    )
    parser.add_argument(
        "--reporte",
        default=OUTPUT_REPORT,
        help=f"Archivo de salida para el reporte (default: {OUTPUT_REPORT}).",
    )

    args = parser.parse_args()

    # Paso 1: Leer letra base
    print("=" * 50)
    print("  CONTRAFACTUM - Generador de letras")
    print("=" * 50)
    print()
    print(f"[1/6] Leyendo letra base de: {args.input}")
    lyrics_text = read_input(args.input)
    print(f"      Leidos {len(lyrics_text.split(chr(10)))} lineas.")

    # Paso 2: Analizar estructura
    print("[2/6] Analizando estructura, metrica y rima...")
    template = analyze_lyrics(lyrics_text)
    resumen = template.get("resumen", {})
    print(f"      Detectadas {resumen.get('total_secciones', '?')} secciones, "
          f"{resumen.get('total_versos', '?')} versos.")
    rango = resumen.get("rango_silabas", (0, 0))
    print(f"      Rango de silabas: {rango[0]}-{rango[1]}")

    # Paso 3: Generar contrafactum
    print(f"[3/6] Generando contrafactum...")
    print(f"      Tema: {args.tema}")
    print(f"      Estilo: {args.estilo}")
    try:
        generated = generate_contrafactum(template, args.tema, args.estilo)
    except ValueError as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR al generar: {e}")
        sys.exit(1)
    print("      Letra generada.")

    # Paso 4: Validar
    print("[4/6] Validando estructura, metrica y rima...")
    report = validate_lyrics(generated, template)
    print(f"      Versos OK: {report['summary']['passed_lines']}/{report['summary']['total_lines']}")

    # Paso 5: Reparar si es necesario
    attempts_used = 0
    if not report["valid"]:
        print(f"[5/6] Reparando versos fallidos (max {MAX_REPAIR_ATTEMPTS} intentos)...")
        while not report["valid"] and attempts_used < MAX_REPAIR_ATTEMPTS:
            attempts_used += 1
            print(f"      Intento {attempts_used}...")
            try:
                generated = repair_lyrics(generated, template, report)
                report = validate_lyrics(generated, template)
                print(f"      Versos OK: {report['summary']['passed_lines']}/{report['summary']['total_lines']}")
            except (ValueError, Exception) as e:
                print(f"      Error en reparacion: {e}")
                break
    else:
        print("[5/6] No se requiere reparacion.")

    # Paso 6: Guardar resultados
    print("[6/6] Guardando resultados...")

    # Guardar letra
    lyrics_content = f"# Contrafactum\n\n"
    lyrics_content += f"**Tema:** {args.tema}\n"
    lyrics_content += f"**Estilo:** {args.estilo}\n\n"
    lyrics_content += "---\n\n"
    lyrics_content += generated
    lyrics_content += "\n"
    save_output(args.output, lyrics_content)
    print(f"      Letra guardada en: {args.output}")

    # Guardar reporte
    report_content = build_report(template, report, args.tema, args.estilo, attempts_used)
    save_output(args.reporte, report_content)
    print(f"      Reporte guardado en: {args.reporte}")

    # Resumen final
    print()
    print("=" * 50)
    print("  RESULTADO")
    print("=" * 50)
    if report["valid"]:
        print("  Estado: EXITO - Todos los versos pasan validacion.")
    else:
        failed = report["summary"]["failed_lines"]
        total = report["summary"]["total_lines"]
        print(f"  Estado: PARCIAL - {failed}/{total} versos con problemas.")
    print(f"  Letra: {args.output}")
    print(f"  Reporte: {args.reporte}")
    print("=" * 50)


if __name__ == "__main__":
    main()
