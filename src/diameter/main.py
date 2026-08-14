from extraction import initialize_extraction
from search import initialize_search


def main():
  
  # Hiperparámetros
  prompt_IDs = ['"(10199) Chariklo"', "Chariklo"]         # Identificadores de objeto
  amount = 500                                            # Cantidad de artículos máximo
  token = "dD15JbSYQrvUB5CZXhvnQxqeDfnT0gczHNRycyGu"      # Token de ADS
  
  # Proceso de búsqueda de artículos científicos
  initialize_search(prompt_IDs=prompt_IDs, amount=amount, token=token)
  
  # Proceso de extracción de diámetros
  initialize_extraction(prompt_IDs=prompt_IDs, vrb=True)

if __name__ == "__main__":
  main()