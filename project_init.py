from pathlib import Path

# Structura de directoare, unde cheia este directorul si valoarea este o lista de fisiere
project_structure = {
    "app": [
        "__init__.py",
        "main.py",
    ],
    "app/api": ["__init__.py"],
    "app/api/v1": [
        "__init__.py",
        "schemas.py",
    ],
    "app/api/v1/endpoints": [
        "__init__.py",
        "math.py",
    ],
    "app/core": [
        "__init__.py",
        "config.py",
        "security.py",  # il cream de acum
    ],
    "app/db": [
        "__init__.py",
        "database.py",
        "models.py",
        "repository.py",
    ],
    "app/services": [
        "__init__.py",
        "math_service.py",
    ],
}

# Fisiere la nivelul radacinii
root_files = [
    ".env",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "README.md",
]


def main():
    print("Creare structura de directoare si fisiere...")

    # Creare directoare si fisierele din interior
    for directory, files in project_structure.items():
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        for file in files:
            (dir_path / file).touch()

    # Creare fisiere la nivelul radacinii
    for file in root_files:
        Path(file).touch()

    print("Structura proiectului a fost creata cu succes!")


if __name__ == "__main__":
    main()
