import os
import re

import spacy
from analysis import analysis_process
from prep import preprocess
from results import show_general_results, show_results

spacy_model = spacy.load('en_core_web_sm')

# Lectura de corpus
def read_corpus(corpus_path, file_name):
  with open(corpus_path + file_name, "r", encoding='utf-8') as f:
    return f.read()

# Función de extracción de palabras clave
def extract_keywords(phrase, object_id, param_related, units, suspicious):
  keywords = {
    'IDs': [
      id for id in object_id
      if re.search(r"\b" + id.lower() + r"\b", phrase.lower())
    ],
    'Parameters': [
      param for param in param_related
      if re.search(r"\b" + param.lower() + r"\b", phrase.lower())
    ],
    'Units': [
      unit for unit in units
      if re.search(r"\b" + unit.lower() + r"\b", phrase.lower())
    ],
    'Suspicious': [
      sus for sus in suspicious
      if re.search(r"\b" + sus.lower() + r"\b", phrase.lower())
    ]
  }
  return keywords

# Función de filtrado
def filter_heuristic(phrases, object_id, param_related, units, suspicious):
  filtered_phrases = []
  for phrase in phrases:

    # Filtrar frases sin id de objeto
    if not any(
      re.search(r"\b" + id.lower() + r"\b", phrase.lower())
      for id in object_id
    ):
      continue

    # Filtrar frases sin parámetro
    if not any(
      re.search(r"\b" + related.lower() + r"\b", phrase.lower())
      for related in param_related
    ):
      continue

    # Filtrar frases sin número + unidades correctas
    if not any(
      re.search(r"\d\s" + unit.lower(), phrase.lower())
      for unit in units
    ):
      continue

    # Si la frase es útil, se guarda
    filtered_phrases.append(phrase)

  return filtered_phrases

# Función para incorporar preprocesamiento y filtrado
def preprocess_filter(corpus_path, file_name, ids, params, units, sus):
  corpus = read_corpus(corpus_path, file_name)

  # Preprocesamiento
  corpus_pp = preprocess(corpus)

  # Tokenización por oraciones
  doc = spacy_model(corpus_pp)
  phrases = [phrase.text for phrase in doc.sents]

  # 1er filtro heurístico
  filtered_phrases = filter_heuristic(phrases, ids, params, units, sus)

  return filtered_phrases

def initialize_extraction(prompt_IDs, vrb=False):

  # Directorio de datos
  corpus_path = "data/papers/"

  # Datos
  file_names = os.listdir(corpus_path)
  if vrb:
    print(f'\nFiles: {file_names}')

  # Identificadores del objeto (se sacan de los del principio) (se agregan
  # términos más generales)
  object_id = prompt_IDs + ['Asteroid', 'Object', 'Body']
  if vrb:
    print(f'\nObject IDs: {object_id}')

  # Parámetros
  param_related = [
      r"Diameter",
      r"Radius"
  ]
  if vrb:
    print(f'\nParameters: {param_related}')

  # Unidades
  units = [
      r"km"
  ]
  if vrb:
    print(f'\nUnits: {units}')

  # Palabras sospechosas
  suspicious = [
      r"Standard Deviation",
      r"Residual",
      r"Ring",
      r"Rings",
      r"Orbital",
      r"Impact",
      r"Satellite",
      r"Crater",
      r"Surface Area",
      r"Moonlet",
      r"Moon",
      r"Companion",
      r"Particle",
      r"Impact",
      r"Impacted",
      r"Impacting",
      r"Cluster",
      r"Family",
      r"Star",
      r"Stellar",
      r"Angular Diameter"
  ]
  if vrb:
    print(f'\nSuspicious Words: {suspicious}')
    
  # Ejecutamos el proceso anterior
  dataset, dataset_best_values = analysis_process(
    file_names,
    corpus_path,
    object_id,
    param_related,
    units,
    suspicious
  )
  
  if vrb:
    show_results(dataset, file_names)
    show_general_results(dataset, dataset_best_values, file_names)