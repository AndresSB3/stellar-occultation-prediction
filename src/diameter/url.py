import json


# Get PDF url from an ADS paper
def get_pdf_url(paper):
  pdf_url = None
  
  # Verifiy links exist and extract links
  if hasattr(paper, "links_data") and paper.links_data:
    links = paper.links_data
    parsed_links = []

    # Parse links
    for link in links:
      
      # Case STR
      if isinstance(link, str):
        parsed_links.append(json.loads(link))

      # Case dictionary
      elif isinstance(link, dict):
        parsed_links.append(link)

    # Extract PDF link
    for link in parsed_links:
      if link.get("type", "").lower() == "pdf":
        pdf_url = link.get("url")
        break

  # Default link
  if not pdf_url:
    pdf_url = f"https://ui.adsabs.harvard.edu/link_gateway/{paper.bibcode}/PUB_PDF"

  return pdf_url