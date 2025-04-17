# AIofus API

API d'authentification pour AIofus (FastAPI).

## Endpoints
- POST /register : inscription (username, password)
- POST /login : connexion (username, password)

## Lancer en local
```
pip install -r requirements.txt
uvicorn main:app --reload
```

## Déploiement
- Déployer ce dossier sur Render.com en tant que service web Python (FastAPI)
- Renseigner la variable d'environnement DATABASE_URL dans Render
