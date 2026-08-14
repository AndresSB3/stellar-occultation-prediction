import os
import re
import unicodedata

import pandas as pd
import spacy

spacy_model = spacy.load('en_core_web_sm')

# Lectura de corpus
def read_corpus(corpus_path, file_name):
  with open(corpus_path + file_name, "r", encoding='utf-8') as f:
    return f.read()

# Normalización unicode
def unicode_normalization(corpus):
  corpus_uni = unicodedata.normalize("NFKD", corpus)
  corpus_uni = "".join(c for c in corpus_uni if not unicodedata.combining(c))
  return corpus_uni

# Tratado de citas de paréntesis
def cite_deletion(corpus):

  # (Autor, Año) (Autor & Autor, Año) (Autor et al., Año)
  # (Autor, Año; Autor, Año) (Autor, Añoa, Añob) (Colaboración, Año)
  casos_sin_detalles = r"(?:\s?\((?:e.g.,\s)?[^\(\)]+[\d]{4}[a-z]?\))"

  # (Autor, Año, detalle adicional)
  casos_con_detalles = r"(?:\s?\((?:e.g.,\s)?[A-Z][^\(\)]+[\d]{4}[^\(\)]+\))"

  cite_pattern = casos_sin_detalles + r"|" + casos_con_detalles
  corpus_nocites = re.sub(cite_pattern, "", corpus)
  return corpus_nocites

# Aplicación de pre procesamiento
def preprocess(corpus):
  corpus = unicode_normalization(corpus)             # Norm Unicode
  corpus = corpus.replace('\u00A0', ' ')             # Espacios no separables
  corpus = re.sub(r"-\n", "", corpus)                # Cortes de línea
  corpus = re.sub(r"([^.])\n([^A-Z\d])", r"\1 \2", corpus) # \n por formato
  corpus = cite_deletion(corpus)                     # Citas paréntesis
  corpus = re.sub(r'http\S+|www\S+', '', corpus)     # URLs
  corpus = re.sub(r" ’", r"’", corpus)               # Espacios en conjunciones
  corpus = re.sub(r"[ ]+", " ", corpus)              # Espacios múltiples
  return corpus

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

# -----------------------------------------------------------------------------
# Clases
# -----------------------------------------------------------------------------

# Clase texto de documento
class document_text:

  # Método de inicialización
  def __init__(self, id, phrase, object_id, param_related, units, suspicious):

    # Atributos dados
    self.id = id
    self.phrase = phrase

    # Se extraen los IDs de objeto, los parámetros, las unidades, las palabras
    # sospechosas en la frase y los valores encontrados
    self.compute_keywords(object_id, param_related, units, suspicious)

    # Se calculan los puntajes para cada valor a partir de análisis de
    # distancias semánticas apoyado por análisis de dependencias
    self.get_score()

    # Se extrae el mejor valor (el del menor puntaje)
    self.compute_best_value()


  # Método apoyo para extraer los valores con las unidades correctas con
  # expresiones regulares
  def _compute_values(self):

    # Diccionario de valores
    self.values = {}

    # Caso rangos de valores
    pattern_1_1 = r'\d+[\.\,]?\d+\s?(?:'
    pattern_1_2 = r')?\s?(?:to|and|[\-\−])\s?\d+[\.\,]?\d+\s?(?:'

    # Caso valores con incertidumbres con ±
    pattern_2 = (
    r'(?<![\-\−\.\,])\d+[\s\.\,\±]?(?:\d+)?[\s\.\,\±]?(?:\d+)?[\s\.\,\±]?(?:'
    r'\d+)?[\s\.\,\±]?(?:\d+)?[\s\.\,\±]?(?:\d+)?[\s]?'
    )

    # Caso valores con incertidumbres con + -
    pattern_3_1 = r'\d+[\t\r\f \+\.\,\(]{0,3}['
    pattern_3_2 = (
    r']{0,2}[\+\d\(]{0,3}[\d\-\t\r\f \−\.\,\/][\t\r\f \d\-\−\+\.\,\(]{0,3}['
    r'\-\−\t\r\f \d\.\,\(\/]{0,3}[\-\t\r\f \d\−\.\,\(\/\)]{0,7}'
    )

    # Se busca el caso de cada unidad
    for unit in self.units:

      # Patrón final (combinación de todos los anteriores con la unidad
      # específica)
      pattern = (
        pattern_1_1 + unit + pattern_1_2 + unit + r')|' +
        pattern_2 + unit + r'(?![\−\-\^\/])|' +
        pattern_3_1 + unit + pattern_3_2 + unit + r'(?![\−\-\^\/])'

      )

      # Extracción de valores
      nums = re.findall(pattern, self.phrase)

      # Puntajes iniciales
      for num in nums:
        self.values[num] = 10000

  # Método para la extracción de palabras clave en la frase (identificadores
  # del objeto, parámetros, unidades, palabras sospechosas y valores)
  def compute_keywords(self, ids, params, units, sus):
    keywords = extract_keywords(self.phrase, ids, params, units, sus)
    self.object_ids = keywords['IDs']
    self.params = keywords['Parameters']
    self.units = keywords['Units']
    self.suspicious = keywords['Suspicious']
    self._compute_values()

  # Método apoyo para el cálculo del puntaje a partir de análisis de distancias
  # semánticas
  def _get_score(self, phrase, w1, w2):

    # Removemos espacios dentro de las palabras que se van a analizar
    phrase = phrase.replace(w1, w1.replace(" ", ""))
    w1 = w1.replace(" ", "")
    phrase = phrase.replace(w2, w2.replace(" ", ""))
    w2 = w2.replace(" ", "")

    # Tokenizamos de forma simple la frase
    phrase = phrase.split()

    # Calculamos la posición absoluta de cada palabra en la frase
    d1 = next((i for i, element in enumerate(phrase) if w1 in element), None)
    d2 = next((i for i, element in enumerate(phrase) if w2 in element), None)

    # Retornamos la distancia entre ambas palabras (distancia semántica)
    return abs(d1 - d2)

  # Método para el cálculo del puntaje de cada valor encontrado por medio de
  # análisis de distancias semánticas apoyado por análisis de dependencias
  def get_score(self):

    # Atributos para el parámetro y el identificador más cercanos al valor
    self.value_params = {}
    self.value_obj_id = {}
    closest_param = ''
    closest_object_id = ''

    # Puntaje inicial por defecto (alto para permitir que cualquier puntaje lo
    # reemplace) (aquí mientras menor es el puntaje mejor)
    initial_score = 10000

    # Penalización por presencia de palabra sospechosa en la misma frase del
    # valor
    punishment = 20

    # Leve penalización por identificador ambiguo
    punishment_id = 10

    # Se aplica análisis de distancias semánticas a cada valor
    for value in self.values:

      # Puntaje asociado al identificador y al parámetro
      score_ids = initial_score
      score_params = initial_score

      # Análisis de distancia semántica entre cada identificador y el valor
      for object_id in self.object_ids:
        distance = self._get_score(
          self.phrase.lower(),
          value.lower(),
          object_id.lower()
        )
        if distance < score_ids:
          score_ids = distance
          closest_object_id = object_id

      # Análisis de distancia semántica entre cada parámetro y el valor
      for param in self.params:
        distance = self._get_score(
          self.phrase.lower(),
          value.lower(),
          param.lower()
        )
        if distance < score_params:
          score_params = distance
          closest_param = param

      # Tomamos como puntaje el menor entre los dos calculados
      score = min(score_ids, score_params)

      # Por CADA palabra sospechosa en la frase, aplicamos penalización
      for _ in self.suspicious:
        score = score + punishment

      # Si el identificador es ambiguo ("object" o "body") se penaliza
      # levemente
      if closest_object_id.lower() in ['object', 'body']:
        score = score + punishment_id

      # Actualizamos el puntaje del valor
      self.values[value] = score

      # Actualizamos el identificador y el parámetro más cercanos al valor
      self.value_obj_id[value] = closest_object_id
      self.value_params[value] = closest_param

      # Reinicamos los contenedores
      closest_object_id = ''
      closest_param = ''

    # Se complementa el análisis de distancias semántica con análisis de
    # dependencias
    self.compute_dependency_bonuses_and_penalties()

  # Método para calcular el valor con el mejor puntaje (el del menor puntaje)
  def compute_best_value(self):
    try:
      self.best_value = min(self.values, key=self.values.get)
      self.best_score = self.values[self.best_value]
      self.best_unit = [unit for unit in self.units if unit in self.best_value][0]
    except:  # noqa: E722
      self.best_value = None
      self.best_score = None
      self.best_unit = None

  # Método para aplicar análisis de dependencias
  def compute_dependency_bonuses_and_penalties(self):

    # Se pasa la frase por Spacy
    phrase = spacy_model(self.phrase)

    # Contenedores para los ancestros y hermanos
    ancestors = []
    children = []

    # Análisis de dependencias por valor en la frase
    for value in self.values:

      # Se extrae el valor numérico del valor (se excluyen unidades, signos e
      # incertidumbres)
      focus = re.search(r'\d+[\.\,]?\d{0,3}', value).group(0)

      # Se busca el bloque de palabras al cual pertenece el valor
      for chunk in phrase.noun_chunks:

        # Filtra los bloques a los cuales no pertenece el valor
        if focus not in chunk.text:
          continue

        # Se extraen los ancestros de la raíz del bloque (como es la raíz del
        # bloque, todos sus ancestros son ancestros del valor)
        ancestors = [
          ancestor.text.lower()
          for ancestor in chunk.root.ancestors
        ]

        # Se extraen los hijos de la raíz del bloque (esto correspondería a los
        # hermanos del valor, dado que los hijos de la raíz son todas las
        # palabras en el bloque)
        children = [
          child.text.lower()
          for child in chunk.root.subtree
          if child != chunk.root
        ]

      # Se crea una lista con los ancestros y hermanos del valor
      dependencies = ancestors + children

      # Si el valor depende de un identificador del objeto, se aplica un bonus
      # (máximo un bonus por valor)
      for object_id in self.object_ids:
        if object_id.lower() not in dependencies:
          continue
        self.values[value] -= 10
        break

      # Si el valor depende de un parámetro, se aplica un bonus (máximo uno por
      # valor)
      for param in self.params:
        if param.lower() not in dependencies:
          continue
        self.values[value] -= 10
        break

      # Si el valor depende de una palabra sospechosa, se aplica una fuerte
      # penalización (sin límite máximo de penalizaciones)
      for sus in self.suspicious:
        if sus.lower() not in dependencies:
          continue
        self.values[value] += 35

# Clase para documento (resume los mejores valores)
class document:

  # Método inicializador que extrae de todas las frases del documento la que
  # tiene el mejor puntaje
  def __init__(self, texts):

    # Puntaje inicial
    score = 10000

    # Se compara el mejor puntaje de cada frase y se guarda el mejor
    for text in texts:

      # Se salta puntajes mayores al actual
      if not text.best_score or text.best_score > score:
        continue

      # Se actualiza el puntaje al menor visto hasta ahora
      score = text.best_score

      # Se actualizan los atributos del documento si se encuentra un mejor
      # puntaje
      self.id = text.id
      self.phrase = text.phrase
      self.best_value = text.best_value
      self.best_unit = text.best_unit
      self.best_score = text.best_score
      self.param = text.value_params[text.best_value]
      self.object_id = text.value_obj_id[text.best_value]

# -----------------------------------------------------------------------------
# Análisis de papers (función principal)
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# Resultados por paper
# -----------------------------------------------------------------------------

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
      print(f'{i+1}.{j+1})')
      print(f'a) Frase: {repr(phrase)}')
      print(f'b) IDs: {dataset[file_name][phrase].object_ids}')
      print(f'c) Parámetros: {dataset[file_name][phrase].params}')
      print(f'd) Unidades: {dataset[file_name][phrase].units}')
      print(f'e) Valores (Y puntajes): {dataset[file_name][phrase].values}')
      print(f'f) Mejor: {dataset[file_name][phrase].best_value}')

      # Si se encuentran palabras sospechosas, se presentan
      if dataset[file_name][phrase].suspicious:
        print(f'g) Palabras Sospechosas: {dataset[file_name][phrase].suspicious}')
      print('')

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