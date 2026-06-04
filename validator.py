# -*- coding: utf-8 -*-
"""
validator.py
Validates generated contrafactum lyrics against the prosodic template.
"""
from pyesia.spanish_poetry_functions import (
    syllables,
    tonic_syllable,
    rhyme,
    clean_punctuation,
)
from generator import _count_metric_syllables


def validate_lyrics(generated_text, template):
    """Validate generated lyrics against a prosodic template.

    Parameters
    ----------
    generated_text : str
        The generated lyrics text with sections separated by blank lines.
    template : dict
        The prosodic template from extract_template.

    Returns
    -------
    dict
        A validation report with structure:
        {
            "valid": bool,
            "section_count": {"expected": int, "got": int, "pass": bool},
            "lines": [
                {
                    "section": int,
                    "line_num": int,
                    "text": str,
                    "expected_syllables": int,
                    "actual_syllables": int,
                    "syllable_pass": bool,
                    "expected_rhyme_group": str or None,
                    "rhyme_pass": bool
                },
                ...
            ],
            "summary": {
                "total_lines": int,
                "passed_lines": int,
                "failed_lines": int
            }
        }
    """
    # Split generated text into sections
    raw_sections = []
    current_section = []
    for line in generated_text.split("\n"):
        if line.strip() == "":
            if current_section:
                raw_sections.append(current_section)
                current_section = []
        else:
            current_section.append(line.strip())
    if current_section:
        raw_sections.append(current_section)

    expected_sections = len(template["sections"])
    got_sections = len(raw_sections)
    section_pass = expected_sections == got_sections

    report = {
        "valid": True,
        "section_count": {
            "expected": expected_sections,
            "got": got_sections,
            "pass": section_pass,
        },
        "lines": [],
        "summary": {"total_lines": 0, "passed_lines": 0, "failed_lines": 0},
    }

    if not section_pass:
        report["valid"] = False

    # Validate each line
    total_lines = 0
    passed_lines = 0
    failed_lines = 0

    for sec_idx, template_section in enumerate(template["sections"]):
        if sec_idx >= len(raw_sections):
            # Missing section - all lines fail
            for line_idx, tpl_line in enumerate(template_section["lines"]):
                total_lines += 1
                failed_lines += 1
                report["lines"].append(
                    {
                        "section": sec_idx + 1,
                        "line_num": line_idx + 1,
                        "text": "",
                        "expected_syllables": tpl_line["metric_syllables"],
                        "actual_syllables": 0,
                        "syllable_pass": False,
                        "expected_rhyme_group": tpl_line["rhyme_group"],
                        "rhyme_pass": False,
                    }
                )
            continue

        gen_lines = raw_sections[sec_idx]

        for line_idx, tpl_line in enumerate(template_section["lines"]):
            total_lines += 1

            if line_idx >= len(gen_lines):
                # Missing line
                failed_lines += 1
                report["lines"].append(
                    {
                        "section": sec_idx + 1,
                        "line_num": line_idx + 1,
                        "text": "",
                        "expected_syllables": tpl_line["metric_syllables"],
                        "actual_syllables": 0,
                        "syllable_pass": False,
                        "expected_rhyme_group": tpl_line["rhyme_group"],
                        "rhyme_pass": False,
                    }
                )
                continue

            gen_text = gen_lines[line_idx]
            actual_syllables = _count_metric_syllables(gen_text)
            expected_syllables = tpl_line["metric_syllables"]

            # Syllable check: pass if within +/-1
            syllable_pass = abs(actual_syllables - expected_syllables) <= 1

            # Rhyme check
            rhyme_group = tpl_line["rhyme_group"]
            rhyme_pass = True  # default pass if no rhyme required

            if rhyme_group is not None:
                # Find other lines in the same section with the same rhyme group
                rhyme_pass = _check_rhyme(
                    gen_text, gen_lines, template_section, line_idx, rhyme_group
                )

            line_pass = syllable_pass and rhyme_pass
            if line_pass:
                passed_lines += 1
            else:
                failed_lines += 1

            report["lines"].append(
                {
                    "section": sec_idx + 1,
                    "line_num": line_idx + 1,
                    "text": gen_text,
                    "expected_syllables": expected_syllables,
                    "actual_syllables": actual_syllables,
                    "syllable_pass": syllable_pass,
                    "expected_rhyme_group": rhyme_group,
                    "rhyme_pass": rhyme_pass,
                }
            )

    report["summary"]["total_lines"] = total_lines
    report["summary"]["passed_lines"] = passed_lines
    report["summary"]["failed_lines"] = failed_lines

    if failed_lines > 0:
        report["valid"] = False

    return report


def _check_rhyme(gen_text, gen_lines, template_section, line_idx, rhyme_group):
    """Check if a line rhymes with other lines in the same rhyme group.

    Returns True if the line rhymes (consonant or assonant) with at least one
    other line in the same group that has already been generated.
    """
    # Get the last word of the current line
    current_words = clean_punctuation(gen_text).split()
    if not current_words:
        return False
    current_last_word = current_words[-1]

    # Find other lines in the same rhyme group
    has_partner = False
    for other_idx, other_tpl_line in enumerate(template_section["lines"]):
        if other_idx == line_idx:
            continue
        if other_tpl_line["rhyme_group"] != rhyme_group:
            continue
        if other_idx >= len(gen_lines):
            continue

        has_partner = True
        other_words = clean_punctuation(gen_lines[other_idx]).split()
        if not other_words:
            continue
        other_last_word = other_words[-1]

        strong, soft = rhyme(current_last_word, other_last_word)
        if strong or soft:
            return True

    # If no partner lines exist yet, pass by default
    if not has_partner:
        return True

    return False
