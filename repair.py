# -*- coding: utf-8 -*-
"""
repair.py
Repair failed lines in generated contrafactum lyrics.
"""
import os
import json

from prompts import SYSTEM_PROMPT, REPAIR_PROMPT


MAX_REPAIR_ATTEMPTS = 3


def repair_lyrics(generated_text, template, validation_report):
    """Repair lines that failed validation by calling the LLM.

    Parameters
    ----------
    generated_text : str
        The generated lyrics text with sections separated by blank lines.
    template : dict
        The prosodic template from extract_template.
    validation_report : dict
        The validation report from validate_lyrics.

    Returns
    -------
    str
        The repaired full lyrics text with failed lines replaced.
    """
    # Identify failed lines
    failed_lines = [
        line_info
        for line_info in validation_report["lines"]
        if not (line_info["syllable_pass"] and line_info["rhyme_pass"])
    ]

    if not failed_lines:
        return generated_text

    # Build description of failed lines
    failed_descriptions = []
    for fl in failed_lines:
        desc = (
            f"Seccion {fl['section']}, verso {fl['line_num']}: "
            f"\"{fl['text']}\" "
            f"(silabas esperadas: {fl['expected_syllables']}, "
            f"obtenidas: {fl['actual_syllables']}, "
            f"grupo rima: {fl['expected_rhyme_group'] or 'libre'})"
        )
        if not fl["syllable_pass"]:
            desc += " [FALLO: silabas]"
        if not fl["rhyme_pass"]:
            desc += " [FALLO: rima]"
        failed_descriptions.append(desc)

    failed_lines_description = "\n".join(failed_descriptions)

    # Build context lines (adjacent lines for coherence)
    raw_sections = _split_sections(generated_text)
    context_parts = []
    for fl in failed_lines:
        sec_idx = fl["section"] - 1
        line_idx = fl["line_num"] - 1
        if sec_idx < len(raw_sections):
            section = raw_sections[sec_idx]
            start = max(0, line_idx - 1)
            end = min(len(section), line_idx + 2)
            context_parts.append(
                f"Seccion {fl['section']}, contexto: "
                + " | ".join(section[start:end])
            )

    context_lines = "\n".join(context_parts)

    prompt = REPAIR_PROMPT.format(
        failed_lines_description=failed_lines_description,
        context_lines=context_lines,
    )

    # Call LLM for repairs
    repaired_lines = _call_llm_for_repair(prompt)

    # Substitute repaired lines into the generated text
    repaired_text = _substitute_lines(generated_text, failed_lines, repaired_lines)

    return repaired_text


def _split_sections(text):
    """Split text into sections by blank lines."""
    raw_sections = []
    current_section = []
    for line in text.split("\n"):
        if line.strip() == "":
            if current_section:
                raw_sections.append(current_section)
                current_section = []
        else:
            current_section.append(line.strip())
    if current_section:
        raw_sections.append(current_section)
    return raw_sections


def _substitute_lines(generated_text, failed_lines, repaired_lines):
    """Replace failed lines in the generated text with repaired ones."""
    raw_sections = _split_sections(generated_text)

    repair_idx = 0
    for fl in failed_lines:
        sec_idx = fl["section"] - 1
        line_idx = fl["line_num"] - 1

        if repair_idx < len(repaired_lines) and sec_idx < len(raw_sections):
            section = raw_sections[sec_idx]
            if line_idx < len(section):
                section[line_idx] = repaired_lines[repair_idx]
        repair_idx += 1

    # Rebuild text
    result_parts = []
    for section in raw_sections:
        result_parts.append("\n".join(section))

    return "\n\n".join(result_parts)


def _call_llm_for_repair(prompt):
    """Call the LLM API to get repaired lines."""
    provider = os.environ.get("CONTRAFACTUM_PROVIDER", "openai").lower()

    if provider == "anthropic":
        return _call_anthropic_repair(prompt)
    else:
        return _call_openai_repair(prompt)


def _call_openai_repair(prompt):
    """Call OpenAI API for repair."""
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
    result = response.choices[0].message.content.strip()
    return [line.strip() for line in result.split("\n") if line.strip()]


def _call_anthropic_repair(prompt):
    """Call Anthropic API for repair."""
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
    result = response.content[0].text.strip()
    return [line.strip() for line in result.split("\n") if line.strip()]
