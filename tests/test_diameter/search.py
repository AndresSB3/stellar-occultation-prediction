import os
import time

import ads
import requests
from extract import extract_pdf_content
from url import get_pdf_url


# Main search function
def search(token, prompt, fields, headers, amount=500, verbose=False):
  
  # Search with ADS package
  ads.config.token = token
  query = ads.SearchQuery(q=prompt, fl=fields, rows=amount)
  papers = list(query)
  
  # Only use open access or eprint papers
  accessible_papers = [
    paper for paper in papers 
    if paper.property and (
      "OPENACCESS" in paper.property or
      "EPRINT" in paper.property
    )
  ]
  
  # Print available papers
  if verbose:
    print(f"Total de papers: {len(papers)}")
    print(f"Total de papers accesibles: {len(accessible_papers)}\n")
  
  # Create folder if it does not exist already
  os.makedirs(r"data/papers", exist_ok=True)
  
  # Text extraction
  for i, paper in enumerate(accessible_papers):
    
    # Get pdf url
    pdf_url = get_pdf_url(paper)
    
    # Try to make request
    try:
      pdf_request = requests.get(pdf_url, headers=headers, timeout=60)
      
      # Check content and status code
      content_type = pdf_request.headers.get("Content-Type", "")
      all_good = pdf_request.status_code == 200 and "pdf" in content_type
      
    # If an error arises, assume there is an error with the paper
    except:  # noqa: E722
      all_good = False
    
    # Print out paper information in case there is an error
    if verbose and not all_good:
      print(f"No disponible: {i+1}")
      print(f"  URL: {pdf_url}")
      try:
        print(f"  estado: {pdf_request.status_code}")
        print(f"  tipo: {content_type}\n")
        
      # If an error arises with content and status code, it probably does not exist
      except:  # noqa: E722, S110
        pass
      
      # Pause and continue to the next paper
      time.sleep(1)
      continue
    
    # Extract paper text
    try:
      extract_pdf_content(paper, pdf_request)
      if verbose:
        print(f"Procesado: {i+1}\n")

    # Error case, print the error
    except Exception as error:  # noqa: BLE001
      if verbose:
        print(f"Error en {i+1}: {error}\n")
    
    time.sleep(1)