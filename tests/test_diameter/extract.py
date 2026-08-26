import re

import fitz


# Identificación de texto en bordes
def is_border(y0, y1, page_height, margin_ratio=0.06):
  margin = page_height * margin_ratio
  return (y0 < margin or y1 > page_height - margin)

# Identificación de bloques de texto muy pequeños
def is_small(text):
  words = text.split()
  return len(words) < 3

# Identificación de bloques de texto compuestos principalmente por números
# y símbolos
def is_sym(text, tolerance = 0.5):
  return sum(char.isalpha() for char in text) / max(len(text), 1) < tolerance

# Identificación de títulos de figuras y tablas
def is_figuretitle(block_text):
  text = block_text.strip().lower()
  return bool(re.match(r'^(fig(\.|"?|ure)?|table)\s*\d+', text))

def extract_pdf_content(paper, pdf_request, folder_name):

  # Abrimos el pdf
  doc_pages = fitz.open(stream=pdf_request.content, filetype="pdf")
  text = ""
  for page in doc_pages:

    # Extraemos altura y bloques del PDF
    page_height = page.rect.height
    blocks = page.get_text("blocks")

    for block in blocks:
      _, y0, _, y1, block_text, *_ = block
      block_text = block_text.strip()

      # Filtramos texto en bordes
      if is_border(y0, y1, page_height):
        continue

      # Filtramos textos muy pequeños
      if is_small(block_text):
        continue

      # Filtramos textos principalmente simbólicos o numéricos
      if is_sym(block_text):
        continue

      # Filtramos títulos de figuras y tablas
      if is_figuretitle(block_text):
        continue

      # Guardamos texto del bloque
      text += block_text + "\n"

    # Separador para cada página
    text += "\n===PAGE===\n\n"

  # Guardamos el texto crudo usando su bibcode
  filename = f"{paper.year}_{paper.bibcode}.txt"
  with open(f"{folder_name}/{filename}", "w", encoding="utf-8") as text_file:
    text_file.write(text)

  doc_pages.close()
  del doc_pages