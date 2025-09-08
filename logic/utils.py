import json

def is_json(jsonString):
  try:
    json.loads(jsonString)
  except ValueError as e:
    return False
  return True