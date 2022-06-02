## Testing

Run `pytest` from the project root to run all tests.

## Release

```bash
pip install build
python -m build --sdist --outdir dist .
pip install twine
rm -rf dist
twine upload dist/*
```
