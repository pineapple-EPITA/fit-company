from setuptools import setup, find_packages

setup(
    name="coach_microservice",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "Flask-JWT-Extended",
        "SQLAlchemy",
        "psycopg2-binary",
        "pydantic",
        "requests"
    ],
    python_requires=">=3.10",
) 