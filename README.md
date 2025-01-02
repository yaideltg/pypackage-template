# Python Package Template

This repository is a fully functional Python package template.

It is based on the use of the `pyproject.toml` configuration file, and takes into account no code compilation is needed.

In case Cython code is included, then a few modifications should be made, mainly in the `build_source_dist` section of the GitHub workflow configuration file (`.github/workflows/packaging.yml`), to include the build of the wheels too.

In case C or FORTRAN code needs to be compiled, then further investigation is needed. A good starting point is to look at other packages configurations, like Numpy, for example.

For this example I'm using a package named `puarmm`.

## Packages used in the development environment

- [asdf](https://github.com/asdf-vm/asdf): is a tool for installing multiple versions of languages, frameworks, and tools and switching between them.
- [python-launcher](https://github.com/brettcannon/python-launcher): a convenience tool for launching the right Python at the right time. With python-launcher, you can use a single command, py, to invoke the installation of Python you intend based on your current working directory or the presence of a virtual environment directory.
- [pipx](https://github.com/pypa/pipx/): a management tool for running other Python tools in isolated environments inspired by the JavaScript world's `npx`.
- [build](https://github.com/pypa/build): a tool provided by the Python Packaging Authority (PyPA) for building Python packages.
- [tox](https://tox.wiki/en/latest/): a testing and task management tool for Python projects.
- [pre-commit](https://pre-commit.com): a tool for managing and executing pre-commit hooks for Git repositories.

The package should be developed under a [virtual environment](https://docs.python.org/3/library/venv.html).

For testing and compatibility we are using the last three versions of Python 3: `3.11`, `3.12`, and `3.13`. These are recommended to be managed by `asdf`.

## Single-sourcing the Project Version

As of the time of writing, there is no standardization on how to manage the packages version in a single place. See [Single-sourcing the Project Version](https://packaging.python.org/en/latest/discussions/single-source-version/) in the Python Packaging User Guide.

We normally would have to manually update in each new release the version number in the following places: `pyproject.toml` file, package's `__init__.py`, and Git tag in case we are using them in the CI/CD workflows.

Evidently, there are several workarounds to this. The one currently proposed by the Python "authorities" is using [setuptools-scm](https://setuptools-scm.readthedocs.io/en/latest/). With it, we only need to worry about the Git tags (`v0.1.0` for example), and all other places get updated dynamically.

We need to include the following configuration in the `pyproject.toml` file:

``` python
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
...

[project]
# Important: Remove any existing version declaration
# version = "0.0.1"
dynamic = ["version"]
...

[tool.setuptools_scm] # can be empty if no extra settings are needed, presence enables setuptools-scm
```

And then the following snippet in the package's `__init__.py` file:

``` python
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("package-name") # replace package-name with the actual name of the package 
except PackageNotFoundError:
    # package is not installed
    pass
```

With this configuration we only have to worry about updating the Git tags for each release, and it will do the heavy lifting for us.

## Development workflow

The bare bones structure of the package is as follows:

```
pyarmm
├── src
│   └── pyarmm
│       ├── __init__.py
│       └── armmodel
│       │   └── __init__.py
│       └── compute
│       │   └── __init__.py
│       └── deps
│       │   └── __init__.py
│       └── analysis
│           └── __init__.py
├── test
└── pyproject.toml
```

### Structure of the package

It has one package called `pyarmm`, which is located in `src/pyarmm/`, and three sub-packages: `armmodel`, `compute`, and `analysis`.

Note that in this case we have opted for a traditional Python Packages structure, but we could also have chosen a [Python Namespace Package](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/) structure instead.

All the configuration of the package is contained inside the `pyproject.toml` file, as specified by the [PEP 518](https://peps.python.org/pep-0518/).

The `pyarmm` package requires a functional Python version `>=3.11`.

### Creating the virtual environment

``` shell
cd /path/to/pyarmm
py -3.13 -m venv .venv
```

This will isolate our development environment from the default Python installation on your computer, and more importantly, from other projects you may be working on. This is absolutely necessary!

### Building the package source and wheels

``` shell
pyproject-build
```

This uses the specifications inside the `pyproject.toml` file, and builds the source and binary distribution packages.

**Note**: Whereas a source distribution allows almost anyone to build the code on their platform, a binary distribution is prebuilt for a given platform and saves users the work of building it themselves.

Because `pyarmm` is a pure Python code, the `wheel` created is universal.

**Note**: In the cases where the packages include compiled code, then there will be a `wheel` for each platform and Python implementation. Of course, this needs a more complex configuration.

The results can be found on a newly created directory called `dist`.

### Installing the package

``` shell
py -m pip install .
```

Now check the package is correctly installed with:

``` shell
py -m pip list
```

### Using `tox` to manage tasks

In the `pyproject.toml` file, as well as in `.github/workflows/packaging.yml`, `tox` is configured to run several tests and tasks.

The default environment runs the tests on the last three versions of Python (at the moment of writing the latest version of Python is 3.13, so be sure to update the `envlist` in case it gets outdated).

``` shell
tox
```

Next there are environments to run a **typecheck** with `mypy`, another to **format** the code using `black`, and another to **lint** the code using `flake-8`.

To run them you can use the following sequence:

``` shell
tox -e typecheck
tox -e format
tox -e lint
```

In case the formatting showed possible changes, these could be applied with

``` shell
tox -e format -- src test
```

### Using `pre-commit` to perform `tox` tasks automatically on commit

Using `pre-commit` (`.pre-commit-config.yaml`) we have configured these `tox` tasks (type-checking, formatting, and linting) automatically every time we perform a commit.

Note that if any of these tasks made modifications to any file, then the commit will fail (because there were modified files), and you will have to commit again. This second time, of course there will be no more changes, and the commit will pass.

## Taking advantage of the `__init__.py` files

This `__init__.py` loads to the namespace the clases and methods in a convenient way. With it, importing
something from wherever in the code would be as:

from pyarm.deps import Dependency, Gromacs

Whereas without it:

from pyarm.deps.Dependency import Dependency
from pyarm.deps.Gromacs import Gromacs

That is, by loading into the 'deps' namespace (from this file) the clases and methods it offers, we create
an interface which:

1. Allows simplified imports,
2. The user doesn't need to know the exact path to the feature he needs, and
3. More importantly, we have the freedom to remodel the 'deps' package structure
   without breking any previous code.

## Features to implement

- To include compiled code configuration, mainly for C and FORTRAN.
- To include the documentation configuration.
- To publish the package to PyPI on every commit marked with a tag.
- To implement dynamic fields in the `pyproject.toml` file, like for example to get the code's version from the git tag.
