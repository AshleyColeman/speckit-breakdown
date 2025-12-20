from setuptools import setup, find_packages

setup(
    name="speckit-breakdown",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "PyYAML>=6.0",
        "psycopg2-binary>=2.9.9",
        "pydantic>=2.0.0",
        "rich>=10.0.0",
        "shellingham>=1.3.0"
    ],
    entry_points={
        "console_scripts": [
            "speckit=src.cli.main:app",
        ],
    },
)
