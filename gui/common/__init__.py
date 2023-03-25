import encodings

__es = []
for encoding in set(encodings.aliases.aliases.values()):
    __es.append(encodings.search_function(encoding).name.upper())
__es.sort()

ENCODINGS: frozenset[str] = frozenset(__es)
