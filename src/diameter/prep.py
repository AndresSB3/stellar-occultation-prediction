import re
import unicodedata


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