import re


# Identificación de texto en bordes
def is_border(y0, y1, page_height, margin_ratio=0.06):
  margin = page_height * margin_ratio
  return (y0 < margin or y1 > page_height - margin)

# Identificación de bloques de texto muy pequeños
def is_small(text):
  words = text.split()
  return len(words) < 3

# Identificación de bloques de texto compuestos principalmente por números
# y símbolos
def is_sym(text, tolerance = 0.5):
  return sum(char.isalpha() for char in text) / max(len(text), 1) < tolerance

# Identificación de títulos de figuras y tablas
def is_figuretitle(block_text):
  text = block_text.strip().lower()
  return bool(re.match(r'^(fig(\.|"?|ure)?|table)\s*\d+', text))