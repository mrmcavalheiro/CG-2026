"""
exemplos/teoria_content.py
Módulo de compatibilidade — re-exporta o conteúdo de docs_teoria.py.
"""
from exemplos.docs_teoria import DOCS_TEORIA

TEORIA_TRANSLACAO   = DOCS_TEORIA["translacao"]
TEORIA_ESCALA       = DOCS_TEORIA["escala"]
TEORIA_ROTACAO      = DOCS_TEORIA["rotacao"]
TEORIA_CISALHAMENTO = DOCS_TEORIA["cisalhamento"]

TEORIAS_MAP = {
    "translacao":   TEORIA_TRANSLACAO,
    "escala":       TEORIA_ESCALA,
    "rotacao":      TEORIA_ROTACAO,
    "cisalhamento": TEORIA_CISALHAMENTO,
}
