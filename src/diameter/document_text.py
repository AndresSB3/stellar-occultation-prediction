import re

import spacy
from extraction import extract_keywords

spacy_model = spacy.load('en_core_web_sm')

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
      self.best_unit = next((unit for unit in self.units if unit in self.best_value), None)
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