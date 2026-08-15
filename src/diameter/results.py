import re

import pandas as pd


# Función para visualización en detalle de resultados
def show_results(dataset, file_names):

  # Se recorre cada paper
  for i, file_name in enumerate(file_names):
    print(f'{i+1}) {file_name}:')

    # Caso en que no se encuentren frases
    if not dataset[file_name]:
      print('No se encontraron frases.\n')
      continue

    # Caso en que sí se encuentren frases
    for j, phrase in enumerate(dataset[file_name]):
      print(f'\n{i+1}.{j+1})')
      print(f'a) Frase: {phrase!r}')
      print(f'b) IDs: {dataset[file_name][phrase].object_ids}')
      print(f'c) Parámetros: {dataset[file_name][phrase].params}')
      print(f'd) Unidades: {dataset[file_name][phrase].units}')
      print(f'e) Valores (Y puntajes): {dataset[file_name][phrase].values}')
      print(f'f) Mejor: {dataset[file_name][phrase].best_value}')

      # Si se encuentran palabras sospechosas, se presentan
      if dataset[file_name][phrase].suspicious:
        print(f'g) Palabras Sospechosas: {dataset[file_name][phrase].suspicious}')

# -----------------------------------------------------------------------------
# Resultados generales
# -----------------------------------------------------------------------------

# Función para presentar resultados generales por paper
def show_general_results(dataset, dataset_best_values, file_names):

  # Listas contenedoras
  ids = []
  object_ids = []
  params = []
  best_values = []
  best_uncs = []
  best_scores = []
  source_phrases = []

  # Se construye un dataframe para resumir los resultados generales
  for file_name in file_names:

    # Si el dataset no tiene datos (no se encontraron frases) se salta
    if not dataset[file_name]:
      continue

    # Se extraen los datos de cada archivo
    id = dataset_best_values[file_name].id
    object_id = dataset_best_values[file_name].object_id
    param = dataset_best_values[file_name].param
    best_score = dataset_best_values[file_name].best_score
    source_phrase = dataset_best_values[file_name].phrase
    best_unit = dataset_best_values[file_name].best_unit

    # Se extrae el mejor valor
    best_value = dataset_best_values[file_name].best_value

    # Caso rangos (se separan los dos extremos y se promedian)
    if re.match(r'\d+[\.\,]?\d+\s?(?:' + best_unit + r')?\s?(?:to|and|[\-\−])\s?\d+[\.\,]?\d+\s?(?:' + best_unit + ')', best_value):
      best_value_split = re.findall(r'\d+[\,\.]?\d{0,3}', best_value)
      best_mag = sum(list(map(float, best_value_split))) / len(list(map(float, best_value_split)))
      best_unc = ''

    # Caso incertidumbres (se separa el valor de la unidad y las incertidumbres)
    else:
      best_value_split = re.findall(r'\d+[\,\.]?\d{0,3}', best_value)
      best_mag = float(best_value_split[0].replace(',', '.'))
      best_unc = " ".join(best_value_split[1:]).strip()

    # Se agrega cada dato a las listas contenedoras correspondientes
    ids.append(id)
    object_ids.append(object_id)
    params.append(param)
    source_phrases.append(source_phrase)

    # Si el valor corresponde a un radio, se duplica (se busca el diámetro)
    try:
      if param == 'Radius':
        best_values.append(best_mag * 2)
      else:
        best_values.append(best_mag)
      best_uncs.append(best_unc)
      best_scores.append(best_score)

    # En caso de encontrarse un error, se asignan a nulos
    except:  # noqa: E722
      best_values.append(None)
      best_unc.append(None)
      best_scores.append(None)

  try:
    # Se crea un diccionario que resuma todos los resultados
    best_values_dict = {
        'ID': ids,
        'Object ID': object_ids,
        'Parameter': params,
        'Extracted Value (standardized to diameters) (' + best_unit + ')': best_values,
        'Uncertainty (single ± or double +, -) (' + best_unit + ')': best_uncs,
        'Score': best_scores,
        'Source Phrase': source_phrases,
    }

    # Se convierte el diccionario a un dataframe
    df_best_values = pd.DataFrame(best_values_dict).sort_values(by='Score').reset_index(drop=True)

    # Se presentan los resultados generales
    print(df_best_values)

    return df_best_values
  except:  # noqa: E722
    print('No se encontraron valores.')
    return None