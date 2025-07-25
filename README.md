# endava-python-project

# MATH MICROSERVICE – PROIECT DE TEMA

## RESPECTAREA CERINTEI

Acest microserviciu a fost dezvoltat in conformitate cu cerinta temei, respectand toate punctele esentiale:

- Microserviciu REST (fara SOAP)
- Operatii matematice implementate: fibonacci, factorial, putere
- Persistenta cererilor in baza de date (SQLite)
- Validare input cu Pydantic
- Structura modulara conform principiilor MVC
- Implementare functionala, fara dependente complexe
- Cod organizat si verificat cu `flake8`, insotit de teste
- Executabil local prin comanda `docker compose up`

Pe langa aceste cerinte de baza, proiectul atinge si mai multe dintre elementele optionale recomandate.

---

## DESCRIEREA APLICATIEI

Aplicatia este un microserviciu REST care permite calculul urmatoarelor operatii:

- **Fibonacci** – calculeaza al `n`-lea numar din sirul Fibonacci (limitat pentru a evita overflow)
- **Factorial** – calculeaza factorialul unui numar intreg nenegativ (cu validare stricta)
- **Putere (`a^b`)** – calculeaza ridicarea la putere, cu suport pentru numere reale si complexe

Rezultatul fiecarei cereri este inregistrat in baza de date, impreuna cu parametrii folositi, tipul operatiei si IP-ul clientului.

---

## TEHNOLOGII FOLOSITE

- **FastAPI** – framework web asincron, rapid si usor de folosit
- **SQLite** – baza de date usoara si portabila, ideala pentru prototipuri si testare
- **SQLAlchemy (async)** – ORM pentru interactiune eficienta cu baza de date
- **Pydantic** – validare declarativa si clara a datelor
- **Uvicorn** – server ASGI de productie
- **Pytest / pytest-asyncio** – testare unitara si integrata
- **Docker & Docker Compose** – rulare containerizata, fara dependente locale
- **Logging** – sistem de loguri pentru cereri si erori
- **Autorizare** – filtrare acces la API prin chei de autentificare

---

## STRUCTURA PROIECTULUI

Proiectul este structurat pe module separate, cu responsabilitati clare:

- `main.py` – initializeaza aplicatia si rutele
- `math.py` – defineste endpoint-urile matematice
- `schemas.py` – contine clasele Pydantic pentru validare
- `models.py` – defineste modelul bazei de date pentru logarea cererilor
- `repository.py` – operatii de salvare asincrona
- `config.py` – incarca configuratii din fisier `.env`
- `utils.py` – serializator JSON pentru numere complexe
- `database.py` – configureaza conexiunea asincrona la SQLite
- `test_*.py` – teste functionale si unitare
- `Dockerfile` si `docker-compose.yml` – permit rularea aplicatiei in containere

---

## CUM SE FOLOSESTE

1. Asigurare Docker instalat
2. Rulare:
   ```bash
   docker compose up --build
3.Acceseaza aplicatia in browser:
  http://localhost:8000/docs
4.Pentru testare (in afara containerului):
  pytest

