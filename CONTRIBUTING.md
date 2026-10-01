# Contributing

Thanks for helping improve OpenFront Auto-Placer. Keep changes focused and explain what they change.

## Development setup

The application and Windows executable require Windows and Python 3.11 or later. From the repository folder:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

To build the standalone executable, run `make.bat`. It installs the build extra and creates `dist\OpenFrontAutoPlacer.exe`.

## Tests

Run the existing unit tests before submitting changes:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests
```

The tests mock system input, so actual interaction with OpenFront and executable builds still need to be checked on Windows.

On a headless Linux test host, use the dummy input backend:

```sh
PYNPUT_BACKEND=dummy python -m unittest discover -s tests
```

## Pull requests

- Describe the problem and the behavior changed.
- Include or update tests when changing behavior.
- Keep unrelated changes out of the pull request.
