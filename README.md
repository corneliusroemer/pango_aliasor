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
```

See [tests](tests/test_aliasor.py) for more examples.

## Installation

```bash
pip install pango_aliasor
```

## Testing

Run `pytest` from the project root to run all tests.

## Release

