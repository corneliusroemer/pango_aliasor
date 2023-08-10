[![Python package](https://github.com/corneliusroemer/pango_aliasor/actions/workflows/pytest.yaml/badge.svg)](https://github.com/corneliusroemer/pango_aliasor/actions/workflows/pytest.yaml)
[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/pango_aliasor/README.html)

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

# Find parent lineage
aliasor.parent("BQ.1") # 'BE.1.1.1'

aliasor.partial_compress("B.1.1.529.3.1",up_to=1) # 'BA.3.1'
aliasor.partial_compress("B.1.1.529.3.1.1.2",up_to=1) # 'BA.3.1.1.2'

aliasor.partial_compress("B.1.1.529.3.1",accepted_aliases=["AY"]) # 'B.1.1.529.3.1'
aliasor.partial_compress("B.1.617.2",accepted_aliases=["AY"]) # 'AY.2'

aliasor.partial_compress('B.1.1.529.2.75.1.2',up_to=4, accepted_aliases={"BA"}) == 'BL.2'
```

See [tests](tests/test_aliasor.py) for more examples.

## Installation

Choose any of the following:

```bash
pip install pango_aliasor
conda install -c bioconda pango_aliasor
mamba install -c bioconda pango_aliasor
```

## Convenience script

If you have a `metadata.tsv` with a `pango_lineage` column and you simply want to add a `pango_lineage_unaliased` column, you can use the convenience script below:

```py
import pandas as pd
from pango_aliasor.aliasor import Aliasor
import argparse


def add_unaliased_column(tsv_file_path, pango_column='pango_lineage', unaliased_column='pango_lineage_unaliased'):
    aliasor = Aliasor()
    def uncompress_lineage(lineage):
        if not lineage or pd.isna(lineage):
            return "?"
        return aliasor.uncompress(lineage)

    df = pd.read_csv(tsv_file_path, sep='\t')
    df[unaliased_column] = df[pango_column].apply(uncompress_lineage)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add unaliased Pango lineage column to a TSV file.')
    parser.add_argument('--input-tsv', required=True, help='Path to the input TSV file.')
    parser.add_argument('--pango-column', default='pango_lineage', help='Name of the Pango lineage column in the input file.')
    parser.add_argument('--unaliased-column', default='pango_lineage_unaliased', help='Name of the column to use for the unaliased Pango lineage column in output.')
    args = parser.parse_args()
    df = add_unaliased_column(args.input_tsv, args.pango_column, args.unaliased_column)
    print(df.to_csv(sep='\t', index=False))
```

## Testing

Run `pytest` from the project root to run all tests.

## Release

1. Bump version in `setup.cfg`
2. Release using `gh release create`
3. Build using `python3 -m build`
4. Publish to Pypi using `twine upload dist/pango_aliasor*`
