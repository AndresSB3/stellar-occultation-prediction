import re
import json
import fitz
import os
import ads
import time
import pandas as pd
import requests

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
        except Exception:
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

# Función proceso de búsqueda
def search_process(token, headers, prompt, fields, amount, folder_name, vrb=False):

  # Búsqueda en ADS
  ads.config.token = token
  query = ads.SearchQuery(q=prompt, fl=fields, rows=amount)
  papers = list(query)
  accessible_papers = []

  # Filtrado de papers (solo se incluyen papers gratis y que no estén en contra
  # de la minería de datos)
  for paper in papers:
    if paper.property and (
        "OPENACCESS" in paper.property or
        "EPRINT" in paper.property
    ):
      accessible_papers.append(paper)

  # Presentamos total de papers encontrados y el total de papers accesibles
  # encontrados
  if vrb:
    print(f"Total de papers: {len(papers)}")
    print(f"Total de papers accesibles: {len(accessible_papers)}\n")

  # Creamos carpeta para textos crudos
  os.makedirs(folder_name, exist_ok=True)

  # Contenedor de datos de papers
  data = []

  # Extraemos el texto de cada paper accesible y recopilamos sus datos
  for i, paper in enumerate(accessible_papers):
    pdf_url = get_pdf_url(paper)

    try:
      pdf_request = requests.get(pdf_url, headers=headers, timeout=60)
      content_type = pdf_request.headers.get("Content-Type", "")

      # Condición para extracción
      all_good = pdf_request.status_code == 200 and "pdf" in content_type

    except: # noqa: E722
      all_good = False

    # En caso de no cumplirse la condición, imprimimos estado del PDF
    if vrb:
      if not all_good:
        print(f"No disponible: {i+1}")
        print(f"  URL: {pdf_url}")
        try:
          print(f"  estado: {pdf_request.status_code}")
          print(f"  tipo: {content_type}\n")
        except:  # noqa: E722
          pass
        time.sleep(1)
        continue

    # En caso de si cumplirse la condición, probamos extraer su contenido
    try:
      extract_pdf_content(paper, pdf_request, folder_name)
      if vrb:
        print(f"Procesado: {i+1}\n")

    # En caso de error imprimimos un mensaje
    except Exception as error:
      if vrb:
        print(f"Error en {i+1}: {error}\n")

    # Pausa para evitar sobre cargar servidores
    time.sleep(1)

    # Guardamos campos del paper
    if paper.property and (
      "OPENACCESS" in paper.property or
      "EPRINT" in paper.property
    ):
      data.append({
        "title": paper.title[0] if paper.title else None,
        "year": paper.year if paper.year else None,
        "authors": ", ".join(paper.author) if paper.author else None,
        "bibcode": paper.bibcode if paper.bibcode else None,
        "property": paper.property if paper.property else None,
      })

  # Presentamos dataframe con los datos de los papers
  df = pd.DataFrame(data)
  if vrb:
    print('')
    print(df)
  
def create_prompt(ids, params):
    IDs = " OR ".join(ids)
    Params = " OR ".join(params)
    return f"({IDs}) AND ({Params}) AND database:astronomy"
  
def initialize_search(prompt_IDs=['"(10199) Chariklo"', "Chariklo"], amount=500, token="dD15JbSYQrvUB5CZXhvnQxqeDfnT0gczHNRycyGu"):
  
  headers = {"User-Agent": "ADS-literature-mining-script"}
  
  prompt_params = [
    "diameter",
    "size",
    "radius",
    '"effective diameter"',
    '"equivalent diameter"',
    "radiometric",
    '"thermal model"',
    "occultation",
    "NEATM",
    "thermal",
    "albedo"
  ]

  prompt = create_prompt(prompt_IDs, prompt_params)

  fields = [
    "title",
    "year",
    "author",
    "bibcode",
    "property",
    "links_data"
  ]

  folder_name = r"data/papers"
  
  search_process(token, headers, prompt, fields, amount, folder_name, vrb=True)