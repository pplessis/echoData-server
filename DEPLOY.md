# Déploiement sur Vercel — echoData-server

Ce document décrit les étapes minimales pour déployer l'application Flask sur Vercel.

Pré-requis
- Avoir le CLI Vercel installé (`npm i -g vercel`) ou utiliser le dashboard.
- Avoir Python 3.11 installé localement pour les tests (recommandé).

Variables d'environnement à définir dans Vercel (Dashboard -> Settings -> Environment Variables)
- `SECRET_KEY` : clé secrète Flask.
- `DATABASE_JSON_PATH` : (optionnel) chemin si vous stockez des JSON externes.
- `MAIL_SERVER` : (optionnel) configuration mail.
- `FLASK_DEBUG` : `True` ou `False`.

Notes importantes
- Ne stockez pas de secrets dans `.env` committé. Utilisez les env vars de Vercel.
- Le runtime serverless est éphémère : toute écriture locale (logs, fichiers JSON modifiés) n'est pas persistante.
  Si l'application doit écrire des données, utilisez un stockage externe (S3, Google Cloud Storage, une base de données).
- Les logs doivent aller sur stdout/stderr (déjà configuré dans `app/config.py`).

Fichiers clés
- `api/app.py` : point d'entrée WSGI exposant `app`.
- `vercel.json` : configuration Vercel (builds, routes, runtime).

Tester localement
1. Installer les dépendances:
```bash
python -m pip install -r requirements.txt
```
2. Lancer Vercel en local pour tester le comportement serverless:
```bash
vercel dev
```

Déployer
```bash
vercel --prod
```

Vérifications post-déploiement
- Vérifier les logs via le dashboard Vercel pour s'assurer qu'il n'y a pas d'erreurs d'import ou d'accès au FS.
- Tester les routes statiques (`/static/...`) et les pages principales.

Recommandations à moyen terme
- Remplacer toute persistance de fichiers locaux par un stockage externe si nécessaire.
- Ajouter un `requirements-lock.txt` généré via `pip freeze` et l'implémenter dans CI.
- Ajouter des tests unitaires et des tests d'intégration pour les endpoints critiques.
