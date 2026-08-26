from test_diameter.search import search


def test_main():
  search(token, prompt, fields, headers, amount, verbose=True)

# Mini función para organizar el prompt
def create_prompt(ids, params):
  IDs = " OR ".join(ids)
  Params = " OR ".join(params)
  return f"({IDs}) AND ({Params}) AND database:astronomy"

# Token de ADS (de cuenta personal)
token = "dD15JbSYQrvUB5CZXhvnQxqeDfnT0gczHNRycyGu"

# Encabezado para declarar que el pipeline hace pedidos para minería de
# literatura
headers = {"User-Agent": "ADS-literature-mining-script"}

# IDs del objeto
prompt_IDs = ["Chariklo"]

# Parámetros que se buscan
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

# Prompt de búsqueda - Parámetros del objeto e Identificadores del objeto
prompt = create_prompt(prompt_IDs, prompt_params)

# Campos de extracción
fields = [
  "title",
  "year",
  "author",
  "bibcode",
  "property",
  "links_data"
]

# Cantidad máxima de PDFs a buscar (muchos no están disponibles así que se
# recomienda un valor alto)
amount = 500

test_main()