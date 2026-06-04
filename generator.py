# -*- coding: utf-8 -*-
"""
generator.py
Template extraction and contrafactum generation using LLM APIs.
"""
import os
import json
import string

from pyesia.spanish_poetry_functions import (
    syllables,
    tonic_syllable,
    detect_synalephas,
    rhyme_scheme,
    clean_punctuation,
)
from prompts import SYSTEM_PROMPT, GENERATION_PROMPT


def _count_metric_syllables(verse_text):
    """Count metric syllables for a single verse string.

    Reimplements the per-verse logic from perform_analysis to work
    directly on a text string rather than requiring a file path.
    """
    verse = clean_punctuation(verse_text)
    words_verse = verse.split()

    if not words_verse:
        return 0

    syllable_number = 0
    verse_type = 0
    total_words = len(words_verse)

    prev_syllables = []
    prev_tonic = []
    synalepha_count = 0

    for word_idx, word in enumerate(words_verse):
        current_syllables = syllables(word)
        current_tonic = tonic_syllable(current_syllables)
        length = len(current_syllables)
        syllable_number += length

        synalepha, _ = detect_synalephas(
            prev_syllables, current_syllables, prev_tonic, current_tonic
        )

        if synalepha:
            synalepha_count += 1

        prev_syllables = current_syllables
        prev_tonic = current_tonic

        if word_idx == total_words - 1:
            if current_tonic == -1:  # aguda
                verse_type = 1
            elif current_tonic < -2:  # esdrujula o sobreesdrujula
                verse_type = -1
            else:  # llana
                verse_type = 0

    metric_syllables = syllable_number - synalepha_count + verse_type
    return metric_syllables


def extract_template(lyrics_text):
    """Extract the prosodic template from a Spanish lyrics text.

    Parameters
    ----------
    lyrics_text : str
        The full lyrics text with sections separated by blank lines.

    Returns
    -------
    dict
        A JSON-serializable template dictionary with structure:
        {
            "sections": [
                {
                    "name": "Seccion 1",
                    "lines": [
                        {
                            "text": "original line",
                            "metric_syllables": int,
                            "rhyme_group": str or None
                        },
                        ...
                    ],
                    "rhyme_endings": {"group": "ending_sound"}
                },
                ...
            ]
        }
    """
    # Split into sections by blank lines
    raw_sections = []
    current_section = []
    for line in lyrics_text.split("\n"):
        if line.strip() == "":
            if current_section:
                raw_sections.append(current_section)
                current_section = []
        else:
            current_section.append(line.strip())
    if current_section:
        raw_sections.append(current_section)

    template = {"sections": []}

    for sec_idx, section_lines in enumerate(raw_sections):
        section = {
            "name": f"Seccion {sec_idx + 1}",
            "lines": [],
            "rhyme_endings": {},
        }

        # Count metric syllables for each line
        for line_text in section_lines:
            metric = _count_metric_syllables(line_text)
            section["lines"].append(
                {
                    "text": line_text,
                    "metric_syllables": metric,
                    "rhyme_group": None,
                }
            )

        # Detect rhyme scheme for this section
        con_list, aso_list, rhyme_dict = rhyme_scheme(section_lines)

        # Assign rhyme groups to lines
        keys = string.ascii_uppercase
        key_idx = 0
        assigned = {}

        for group_indices in con_list:
            group_key = keys[key_idx] if key_idx < len(keys) else f"C{key_idx}"
            for line_idx in group_indices:
                if line_idx < len(section["lines"]):
                    section["lines"][line_idx]["rhyme_group"] = group_key
                    assigned[line_idx] = group_key
            # Get the rhyme ending from the first word in the group
            if group_indices:
                first_idx = group_indices[0]
                if first_idx < len(section_lines):
                    last_word = clean_punctuation(section_lines[first_idx]).split()[-1]
                    s = syllables(last_word)
                    t = tonic_syllable(s)
                    ending = "".join(s[t:])
                    section["rhyme_endings"][group_key] = ending
            key_idx += 1

        keys_lower = string.ascii_lowercase
        key_idx_lower = 0
        for group_indices in aso_list:
            group_key = keys_lower[key_idx_lower] if key_idx_lower < len(keys_lower) else f"a{key_idx_lower}"
            for line_idx in group_indices:
                if line_idx < len(section["lines"]) and line_idx not in assigned:
                    section["lines"][line_idx]["rhyme_group"] = group_key
                    assigned[line_idx] = group_key
            if group_indices:
                first_idx = group_indices[0]
                if first_idx < len(section_lines):
                    last_word = clean_punctuation(section_lines[first_idx]).split()[-1]
                    s = syllables(last_word)
                    t = tonic_syllable(s)
                    ending = "".join(s[t:])
                    section["rhyme_endings"][group_key] = ending
            key_idx_lower += 1

        template["sections"].append(section)

    return template


def generate_contrafactum(template, theme, style):
    """Generate a contrafactum using an LLM API.

    Parameters
    ----------
    template : dict
        The prosodic template extracted by extract_template.
    theme : str
        The new theme for the contrafactum.
    style : str
        The musical style.

    Returns
    -------
    str
        The generated lyrics text.
    """
    provider = os.environ.get("CONTRAFACTUM_PROVIDER", "openai").lower()

    total_sections = len(template["sections"])
    template_json = json.dumps(template, ensure_ascii=False, indent=2)

    prompt = GENERATION_PROMPT.format(
        template_json=template_json,
        theme=theme,
        style=style,
        total_sections=total_sections,
    )

    if provider == "anthropic":
        return _call_anthropic(prompt)
    else:
        return _call_openai(prompt)


def _call_openai(prompt):
    """Call OpenAI API to generate text."""
    import openai

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it to use the OpenAI provider."
        )

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
    )
    return response.choices[0].message.content.strip()


def _call_anthropic(prompt):
    """Call Anthropic API to generate text."""
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Please set it to use the Anthropic provider."
        )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.content[0].text.strip()
