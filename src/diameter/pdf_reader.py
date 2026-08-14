import json

import fitz
from text_id import is_border, is_figuretitle, is_small, is_sym


# Función para extracción de texto de archivos PDF
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
    print('saving...')
    text_file.write(text)

  doc_pages.close()
  del doc_pages

# Función para conseguir url de PDF
def get_pdf_url(paper):

  # Valor inicial
  pdf_url = None

  # Recorremos cada link
  if hasattr(paper, "links_data") and paper.links_data:
    links = paper.links_data
    parsed_links = []

    # Extraemos los links parseados
    for link in links:

      # Caso str
      if isinstance(link, str):
        try:
          parsed_links.append(json.loads(link))
        except json.JSONDecodeError:
          continue

      # Caso diccionario
      elif isinstance(link, dict):
        parsed_links.append(link)

    # Buscamos el link que corresponde al PDF
    for link in parsed_links:
      if link.get("type", "").lower() == "pdf":
        pdf_url = link.get("url")
        break

  # En caso de no encontrarse link, se asigna uno por defecto
  if not pdf_url:
    pdf_url = f"https://ui.adsabs.harvard.edu/link_gateway/{paper.bibcode}/PUB_PDF"

  return pdf_url