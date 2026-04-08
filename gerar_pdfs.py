"""
============================================================
 gerar_pdfs.py
 Gera os PDFs de teoria a partir de DOCS_TEORIA (blocos inline).

 Uso:
   python gerar_pdfs.py

 Requisito:
   pip install fpdf2
============================================================
"""

import os
import sys
import unicodedata

try:
    from fpdf import FPDF
except ImportError:
    print("Erro: fpdf2 nao encontrado. Execute:")
    print("  pip install fpdf2")
    sys.exit(1)

# Garante que conseguimos importar o projeto
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from exemplos.docs_teoria import DOCS_TEORIA

# Mapa: chave -> (subpasta, arquivo.pdf)
PDF_MAP = {
    "translacao":       ("Aula_04", "translacao.pdf"),
    "escala":           ("Aula_04", "escala.pdf"),
    "rotacao":          ("Aula_04", "rotacao.pdf"),
    "cisalhamento":     ("Aula_04", "cisalhamento.pdf"),
    "window_viewport":  ("Aula_05", "window_viewport.pdf"),
    "proj_ortogonal":   ("Aula_05", "proj_ortogonal.pdf"),
    "proj_perspectiva": ("Aula_05", "proj_perspectiva.pdf"),
    "clipping":         ("Aula_05", "clipping.pdf"),
    "seno_cosseno":     ("Fundamentos", "seno_cosseno.pdf"),
    "circulo":          ("Fundamentos", "circulo.pdf"),
    "bezier":           ("Aula_06",    "bezier.pdf"),
    "pipeline_3d":      ("Aula_08",    "pipeline_3d.pdf"),
    "cores_iluminacao": ("Aula_08",    "cores_iluminacao.pdf"),
    "obj_formato":      ("Aula_08",    "obj_formato.pdf"),
}

# Constantes de layout
MARGIN = 18.0  # mm
PW = 210.0  # A4 largura mm
CONTENT_W = PW - 2 * MARGIN
LINE_H = 6.0  # altura de linha padrao mm
CODE_H = 5.5  # altura linha de codigo

# Normalizacao para fonte core (Latin-1)
_CHAR_MAP = {
    "—": "-",
    "–": "-",
    "−": "-",
    "•": "-",
    "→": "->",
    "←": "<-",
    "↔": "<->",
    "×": "x",
    "÷": "/",
    "≤": "<=",
    "≥": ">=",
    "≠": "!=",
    "≈": "~=",
    "π": "pi",
    "θ": "theta",
    "Δ": "Delta",
    "δ": "delta",
    "²": "^2",
    "³": "^3",
    "⁴": "^4",
    "₀": "0",
    "₁": "1",
    "₂": "2",
    "₃": "3",
}


def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    out = text
    for src, dst in _CHAR_MAP.items():
        out = out.replace(src, dst)

    out = unicodedata.normalize("NFKD", out)
    out = "".join(ch for ch in out if not unicodedata.combining(ch))
    out = out.encode("latin-1", "ignore").decode("latin-1")
    return out


class TeoriaPDF(FPDF):
    def __init__(self, titulo=""):
        super().__init__()
        self._titulo = titulo
        self.set_margins(MARGIN, MARGIN, MARGIN)
        self.set_auto_page_break(auto=True, margin=MARGIN + 5)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 100, 140)
        self.cell(0, 6, sanitize_text("Computacao Grafica - UNIJUI 2026"), align="R")
        self.ln(4)
        self.set_draw_color(80, 100, 200)
        self.line(MARGIN, self.get_y(), PW - MARGIN, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(140, 140, 140)
        self.set_draw_color(200, 200, 200)
        self.line(MARGIN, self.get_y() - 1, PW - MARGIN, self.get_y() - 1)
        self.cell(0, 6, sanitize_text(f"Pagina {self.page_no()}"), align="C")


def render_block(pdf: TeoriaPDF, btype: str, btext: str):
    w = CONTENT_W
    btext = sanitize_text(btext)

    if btype == "blank":
        pdf.ln(4)

    elif btype == "sep":
        pdf.ln(2)
        pdf.set_draw_color(100, 120, 180)
        pdf.line(MARGIN, pdf.get_y(), PW - MARGIN, pdf.get_y())
        pdf.ln(4)

    elif btype == "title":
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(20, 40, 100)
        pdf.multi_cell(w, 10, btext, align="L")
        pdf.set_draw_color(40, 80, 200)
        pdf.set_line_width(0.8)
        pdf.line(MARGIN, pdf.get_y(), PW - MARGIN, pdf.get_y())
        pdf.set_line_width(0.2)
        pdf.ln(4)

    elif btype == "sub":
        pdf.set_font("Helvetica", "I", 12)
        pdf.set_text_color(0, 100, 140)
        pdf.multi_cell(w, LINE_H, btext, align="L")
        pdf.ln(2)

    elif btype == "head":
        pdf.ln(3)
        x, y = pdf.get_x(), pdf.get_y()
        pdf.set_fill_color(230, 235, 248)
        pdf.set_draw_color(60, 100, 200)
        pdf.set_font("Helvetica", "B", 11)
        pdf.rect(MARGIN, y, w, 7.5, style="F")
        pdf.line(MARGIN, y, MARGIN, y + 7.5)
        pdf.set_text_color(30, 60, 160)
        pdf.set_xy(MARGIN + 3, y + 0.5)
        pdf.cell(w - 3, 6.5, btext)
        pdf.set_xy(MARGIN, y + 8)
        pdf.ln(2)

    elif btype == "body":
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(w, LINE_H, btext, align="J")
        pdf.ln(1)

    elif btype == "list":
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(MARGIN + 4)
        pdf.multi_cell(w - 4, LINE_H, f"-  {btext}", align="L")
        pdf.ln(0.5)

    elif btype == "code":
        x, y = MARGIN, pdf.get_y()
        pdf.set_font("Courier", "", 10)
        tw = pdf.get_string_width(btext) + 8
        tw = min(tw, w)
        bh = CODE_H + 2
        pdf.set_fill_color(240, 245, 240)
        pdf.set_draw_color(160, 200, 160)
        pdf.rect(x, y, w, bh, style="FD")
        pdf.set_fill_color(60, 160, 80)
        pdf.rect(x, y, 2.5, bh, style="F")
        pdf.set_text_color(20, 100, 30)
        pdf.set_xy(x + 4, y + 1.2)
        while btext and pdf.get_string_width(btext) > w - 8:
            btext = btext[:-1]
        pdf.cell(w - 8, CODE_H, btext)
        pdf.set_xy(MARGIN, y + bh + 1)

    elif btype == "eq":
        pdf.ln(2)
        x, y = MARGIN, pdf.get_y()
        bh = LINE_H + 5
        pdf.set_fill_color(245, 240, 255)
        pdf.set_draw_color(120, 60, 180)
        pdf.rect(x, y, w, bh, style="FD")
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(80, 20, 160)
        pdf.set_xy(x, y + 1.5)
        pdf.cell(w, LINE_H, btext, align="C")
        pdf.set_xy(MARGIN, y + bh + 2)
        pdf.ln(1)

    elif btype in ("table_h", "table_r"):
        cols = [sanitize_text(c.strip()) for c in btext.split("|")]
        n = len(cols)
        cw = w / max(n, 1)
        y = pdf.get_y()
        bh = 6.5

        if btype == "table_h":
            pdf.set_fill_color(210, 220, 240)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(20, 40, 120)
        else:
            pdf.set_fill_color(248, 248, 252)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)

        pdf.set_draw_color(180, 190, 220)
        for i, col in enumerate(cols):
            pdf.set_xy(MARGIN + i * cw, y)
            pdf.cell(cw, bh, col, border=1, fill=True, align="L")
        pdf.ln(bh)


def gerar_pdf(key: str, blocks: list, out_path: str):
    titulo = sanitize_text(next((b[1] for b in blocks if b[0] == "title"), key))
    pdf = TeoriaPDF(titulo=titulo)
    pdf.add_page()

    for btype, btext in blocks:
        render_block(pdf, btype, btext)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf.output(out_path)
    print(f"  [OK] {os.path.relpath(out_path, BASE)}")


if __name__ == "__main__":
    print("Gerando PDFs de teoria...")
    ok = 0
    for key, (subfolder, filename) in PDF_MAP.items():
        if key not in DOCS_TEORIA:
            print(f"  [SKIP] '{key}' nao encontrado em DOCS_TEORIA")
            continue
        out = os.path.join(BASE, "teoria", subfolder, filename)
        try:
            gerar_pdf(key, DOCS_TEORIA[key], out)
            ok += 1
        except Exception as e:
            print(f"  [ERRO] {key}: {e}")

    print(f"\n{ok}/{len(PDF_MAP)} PDFs gerados em 'teoria/'.")
