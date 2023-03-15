import encodings

_es = []
for encoding in set(encodings.aliases.aliases.values()):
    _es.append(encodings.search_function(encoding).name.upper())
_es.sort()

ENCODINGS = frozenset(_es)
