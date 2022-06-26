## Testing

Run `pytest` from the project root to run all tests.

## Release

```bash
python -m build --wheel
rm -rf dist
twine upload dist/*
```
