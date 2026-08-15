from document_text import document, document_text
from extraction import preprocess_filter


# Función para proceso de análisis
def analysis_process(file_names, corpus_path, ids, params, units, sus):

  # Diccionarios contenedores
  dataset = {}
  dataset_best_values = {}

  # Se trabaja con cada paper
  for file_name in file_names:
    dataset[file_name] = {}

    # Preprocesamiento + filtro heurístico
    filtered_phrases = preprocess_filter(
      corpus_path,
      file_name,
      ids,
      params,
      units,
      sus
    )

    # Se aplica el análisis a cada frase encontrada en el paper
    for filtered_phrase in filtered_phrases:
      dataset[file_name][filtered_phrase] = document_text(
        file_name,
        filtered_phrase,
        ids,
        params,
        units,
        sus
      )

    # Se extrae el mejor valor del paper (el valor con el menor puntaje)
    texts = [dataset[file_name][text] for text in dataset[file_name]]
    dataset_best_values[file_name] = document(texts)

  return dataset, dataset_best_values