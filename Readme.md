# Ilm Notes - Guide de déploiement Streamlit Cloud

## 1️⃣ Pré-requis

* Compte GitHub
* Compte Streamlit Cloud ([https://streamlit.io/cloud](https://streamlit.io/cloud))
* Python 3.10+ installé localement pour tests

## 2️⃣ Structure du projet

```
ilm_notes/
│
├─ app.py              # Fichier principal Streamlit
├─ logic.py            # Pages + fonctions utilitaires
├─ db.py               # Gestion de la base de données et utilisateurs
├─ requirements.txt    # Dépendances Python
```

### Exemple `requirements.txt`

```
streamlit
pandas
altair
reportlab
```

> Astuce : Ne pas inclure `ilm_notes.db`, il sera créé automatiquement à la première utilisation.

## 3️⃣ Préparer le projet GitHub

```bash
git init
git add .
git commit -m "Initial commit Ilm Notes"
git branch -M main
git remote add origin <URL_DE_TON_REPO>
git push -u origin main
```

* `<URL_DE_TON_REPO>` = URL de ton dépôt GitHub

## 4️⃣ Déploiement sur Streamlit Cloud

1. Connecte Streamlit Cloud à ton compte GitHub.
2. Sélectionne le repository `ilm_notes`.
3. Indique `app.py` comme fichier principal.
4. Streamlit Cloud installera automatiquement les packages depuis `requirements.txt`.
5. L’application sera en ligne avec une URL type :
   `https://share.streamlit.io/username/ilm_notes/main/app.py`

## 5️⃣ Test du MVP

* Créer un utilisateur (manuel via la saisie du nom d'utilisateur).
* Ajouter des notes (vérifier la limite du plan gratuit à 10 notes).
* Tester le graphique de progression par catégorie.
* Tester l’export PDF et le format WhatsApp.
* Vérifier la compatibilité mobile.

## 6️⃣ Option PRO et paiement

Pour le MVP, simuler l’upgrade :

* Bouton « Passer au PRO » → call `upgrade_plan(username)`.
* Plan PRO → illimité.

Pour production :

* Intégrer Stripe ou Mobile Money pour le paiement réel.
* Après paiement réussi, appeler `upgrade_plan(username)`.

## 7️⃣ Conseils et bonnes pratiques

* Toujours utiliser un curseur (`conn.cursor()`) pour exécuter les requêtes SQL.
* Tous les chemins doivent être relatifs pour Streamlit Cloud.
* Les fichiers PDF sont temporaires en cloud ; pour persistance, utiliser un stockage cloud (S3, Google Drive, etc.).
* Collecter le feedback des étudiants pour améliorer le produit avant intégration du paiement.

---

✅ Avec ce guide, Ilm Notes est prêt à être mis en ligne pour tes étudiants et testé en situation réelle. Après validation, l’intégration du plan PRO et paiement pourra être ajoutée facilement.
