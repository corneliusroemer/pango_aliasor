[![Python package](https://github.com/corneliusroemer/pango_aliasor/actions/workflows/pytest.yaml/badge.svg)](https://github.com/corneliusroemer/pango_aliasor/actions/workflows/pytest.yaml)

Python convenience library to translate between aliased and unaliased Pango lineages

Useful for:
- constructing a tree of Pango lineages
- semantic sorting of Pango lineages
- ...

## Usage

```python
from pango_aliasor.aliasor import Aliasor

# Initalize aliasor (only needs to be done once)
# If no alias_key.json is passed, downloads the latest version from github
aliasor = Aliasor()

# To use custom alias_key.json, pass the relative path to the file
# aliasor = Aliasor('alias_key.json')

# Go from aliased lineage to unaliased lineage
aliasor.uncompress("BA.5") # 'B.1.1.529.5'
aliasor.uncompress("BE.5") # 'B.1.1.529.5.3.1.5'
aliasor.uncompress("XA") # 'XA'

# Go from unaliased lineage to aliased lineage
aliasor.compress("B.1.1.529.3.1") # 'BA.3.1'

aliasor.partial_compress("B.1.1.529.3.1",up_to=1) # 'BA.3.1'
aliasor.partial_compress("B.1.1.529.3.1.1.2",up_to=1) # 'BA.3.1.1.2'

aliasor.partial_compress("B.1.1.529.3.1",accepted_aliases=["AY"]) # 'B.1.1.529.3.1'
aliasor.partial_compress("B.1.617.2",accepted_aliases=["AY"]) # 'AY.2'

aliasor.partial_compress('B.1.1.529.2.75.1.2',up_to=4, accepted_aliases={"BA"}) == 'BL.2'
```

See [tests](tests/test_aliasor.py) for more examples.

## Installation

```bash
pip install pango_aliasor
```

## Testing

Run `pytest` from the project root to run all tests.

## Release

1. Bump version in `setup.cfg`
2. Release using `gh release create`
3. Build using `python3 -m build`
4. Publish to Pypi using `twine upload dist/pango_aliasor*
