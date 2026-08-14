import os
import time

import ads
import pandas as pd
import requests
from pdf_reader import extract_pdf_content, get_pdf_url


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
    if vrb and not all_good:
      print(f"No disponible: {i+1}")
      print(f"  URL: {pdf_url}")
      
      if "pdf_request" in locals() and pdf_request is not None:
        print(f"  estado: {pdf_request.status_code}")
        
      if "content_type" in locals():
        print(f"  tipo: {content_type}\n")
        
      time.sleep(1)
      continue

    # En caso de si cumplirse la condición, probamos extraer su contenido
    try:
      extract_pdf_content(paper, pdf_request, folder_name)
      if vrb:
        print(f"Procesado: {i+1}\n")

    # En caso de error imprimimos un mensaje
    except Exception as error:  # noqa: BLE001
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
    print(f'\n{df}')
  
def create_prompt(ids, params):
    IDs = " OR ".join(ids)
    Params = " OR ".join(params)
    return f"({IDs}) AND ({Params}) AND database:astronomy"
  
def initialize_search(prompt_IDs=None, amount=500, token="dD15JbSYQrvUB5CZXhvnQxqeDfnT0gczHNRycyGu"):
  
  if not prompt_IDs:
    prompt_IDs = ['"(10199) Chariklo"', "Chariklo"]
  
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