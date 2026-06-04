# -*- coding: utf-8 -*-
"""
prompts.py
Prompt templates for contrafactum-ai generation and repair.
"""

SYSTEM_PROMPT = """Eres un letrista experto en musica mexicana y latinoamericana. \
Tu especialidad es escribir contrafactums: nuevas letras que mantienen exactamente \
la estructura metrica, el esquema de rima y la organizacion en secciones de una \
cancion original, pero con un tema completamente diferente.

Reglas estrictas:
- Escribe en espanol mexicano natural y coloquial.
- NUNCA copies frases literales del texto original.
- Cada verso debe cumplir con el conteo de silabas metricas indicado (tolerancia +/-1).
- Respeta el patron de rima indicado en la plantilla.
- Mantien la misma cantidad de secciones y versos por seccion.
- El resultado debe sonar natural y cantable.
"""

GENERATION_PROMPT = """Genera un contrafactum completo basado en la siguiente plantilla metrica.

PLANTILLA:
{template_json}

TEMA NUEVO: {theme}
ESTILO: {style}

INSTRUCCIONES:
1. Escribe exactamente {total_sections} secciones separadas por una linea en blanco.
2. Cada seccion debe tener exactamente el numero de versos indicado en la plantilla.
3. Para cada verso, respeta el numero de silabas metricas indicado (tolerancia +/-1 silaba).
4. Respeta el esquema de rima: los versos marcados con el mismo grupo de rima deben rimar entre si.
5. NO copies ninguna frase del texto original. Crea contenido completamente nuevo sobre el tema indicado.
6. Escribe en espanol mexicano natural, que suene bien al cantarse.

Responde SOLO con las letras generadas, sin explicaciones ni marcadores de seccion.
"""

REPAIR_PROMPT = """Necesito que reescribas SOLO los versos que fallaron la validacion metrica.

VERSOS QUE FALLARON:
{failed_lines_description}

CONTEXTO (versos adyacentes para mantener coherencia):
{context_lines}

INSTRUCCIONES:
1. Reescribe SOLO los versos indicados como fallidos.
2. Cada verso reescrito debe cumplir con su conteo de silabas metricas objetivo (tolerancia +/-1).
3. Mantien el esquema de rima: si el verso debe rimar con otro, asegurate de que rime.
4. Mantien la coherencia tematica con los versos de contexto.
5. Escribe en espanol mexicano natural.

Responde con SOLO los versos reescritos, uno por linea, en el mismo orden que se presentaron.
No incluyas explicaciones ni numeracion.
"""
