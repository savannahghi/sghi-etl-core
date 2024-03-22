<h1 align="center" style="border-bottom: none; text-align: center;">SGHI ETL Core</h1>
<h3 align="center" style="text-align: center;">API specification for components of a simple ETL workflow.</h3>
<p align="center" style="text-align: center;">
    <img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fgithub.com%2Fsavannahghi%2Fsghi-etl-core%2Fraw%2Fdevelop%2Fpyproject.toml&logo=python&labelColor=white">
    <a href="https://microsoft.github.io/pyright/">
        <img alt="Checked with pyright" src="https://microsoft.github.io/pyright/img/pyright_badge.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json">
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white">
    </a>
    <a href="https://github.com/semantic-release/semantic-release">
        <img alt="Semantic Release: conventionalcommits" src="https://img.shields.io/badge/semantic--release-conventionalcommits-e10079?logo=semantic-release"/>
    </a>
    <a href="https://github.com/savannahghi/sghi-etl-core/blob/develop/LICENSE">
        <img alt="GitHub License" src="https://img.shields.io/badge/License-MIT-blue.svg">
    </a>
</p>
<p align="center" style="text-align: center;">
    <a href="https://github.com/savannahghi/sghi-etl-core/actions/workflows/ci.yml">
        <img alt="CI" src="https://github.com/savannahghi/sghi-etl-core/actions/workflows/ci.yml/badge.svg">
    </a>
    <a href="https://coveralls.io/github/savannahghi/sghi-etl-core?branch=develop">
        <img alt="Coverage Status" src="https://img.shields.io/coverallsCoverage/github/savannahghi/sghi-etl-core?branch=develop&logo=coveralls">
    </a>
</p>

---

`sghi-etl-core` specifies the API of simple ETL workflows. That is, this
project defines and specifies the interfaces of the main components needed to
implement an ETL workflow.

## Contribute

Clone the project and run the following command to install dependencies:

```bash
pip install -e .[dev,test,docs]
```

Set up pre-commit hooks:
```bash
pre-commit install
```

## License

[MIT License](https://github.com/savannahghi/sghi-etl-core/blob/develop/LICENSE)

Copyright (c) 2024, Savannah Informatics Global Health Institute
