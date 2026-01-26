Contexte du projet
EduSmart est une startup innovante spécialisée dans les solutions éducatives intelligentes. Elle propose une plateforme permettant d’optimiser l’apprentissage autonome à partir de contenus fiables et accessibles, notamment les articles Wikipedia.

Face à la surcharge informationnelle et aux barrières linguistiques, EduSmart vise à réduire le temps nécessaire à la compréhension d’un sujet tout en renforçant la rétention des connaissances. L’utilisateur fournit simplement l’URL d’un article Wikipedia, et la plateforme lui offre instantanément :

Un résumé synthétique,
Une traduction fidèle vers une langue cible de son choix (ex. : anglais, arabe, espagnol),
Un QCM interactif généré dynamiquement à partir du contenu de l’article, permettant une auto-évaluation immédiate,
Un suivi personnalisé de sa progression : historique des articles traités, scores aux quiz, points forts/faibles par thématique.
En tant que développeur IA, vous êtes chargé(e) de concevoir et d’implémenter le cœur intelligent de cette solution, en exploitant un modèle de langage (LLM) pour automatiser ces quatre capacités clés, tout en garantissant performance, précision et expérience utilisateur fluide.

Fonctionnalités principales
Ingestion de contenu

L’utilisateur peut soumettre du contenu de deux manières :

Via URL Wikipedia : extraction du texte à l’aide de la bibliothèque wikipedia (utilise un User-Agent).
session = requests.Session()
session.headers.update({
    "User-Agent": "MyWikiProject/1.0 (contact: youremail@example.com)"
    
})
​
wikipedia.requests = session
Via téléchargement de fichier PDF : extraction du texte à l’aide de LangChain.
Prétraitement du texte:

Analyser l’URL et récupérer l’identifiant de l’article (le “tag” ou titre recherché) en utilisant urllib.parse.urlparse et en accédant à l’attribut path.
Si l’identifiant de Wikipédia contient plusieurs mots séparés par des underscores (_), remplacer les underscores par des espaces pour obtenir le titre correct de l’article.
Dans les articles Wikipédia, la structure est organisée en sections identifiées par des titres délimités par === Nom de la section ===.
Le prétraitement consiste à segmenter l’article en sections distinctes et à les représenter sous forme de dictionnaire
Traitement intelligent (via LLM)

À partir du contenu extrait, l’utilisateur choisit l’une des actions suivantes :

Résumé : format personnalisable (court / moyen).
Traduction : vers une langue cible parmi une liste prédéfinie (FR, EN, AR, ES, etc.).
Génération de quiz : retour au format JSON incluant : Questions à choix multiples (4 options, 1 bonne réponse), Questions ouvertes courtes, Réponses correctes incluses.
Export des résultats

L’utilisateur peut télécharger les résultats sous forme de : Fichier PDF, Fichier texte brut (.txt).
Rôles et permissions

Utilisateur: Résumer, traduire, générer des QCM, Choisir le format de téléchargement, Consulter son historique, ses actions et ses scores
Administrateur:
Gérer les comptes utilisateurs et leurs rôles
Accéder aux statistiques globales : Nombre d’inscriptions, Nombre d’articles résumés, Nombre de QCM générés, Nombre de téléchargements
tables principales:

users: id, username, email, hashed_password,
articles: id, url, title, action, createdat
quizattempts: id, userid, articleid, score, submittedat
Intégration des LLMs

Résumé : via Groq (modèle optimisé pour la vitesse et la concision).
Traduction & génération de QCM : via Google Gemini.
Pour chaque LLM, configurer la température (temperature) et le nombre maximal de tokens (max_tokens).
Prompt Engineering : chaque fonctionnalité utilise un prompt personnalisé comprenant :
Le contexte,
Le contenu source (article ou texte extrait),
Des instructions précises,
Une spécification stricte du format de sortie (notamment JSON pour les quiz).
Backend

Framework : FastAPI (API REST asynchrone)
Validation : Pydantic(Valider également l’URL de Wikipédia)
ORM : SQLAlchemy
Authentification : OAuth 2.0 + JWT
Base de données : PostgreSQL
Configuration : pydantic-settings + fichiers .env
Logging : journalisation structurée des événements applicatifs
wikipedia: Accéder au contenu des articles Wikipédia
urllib.parse: Manipuler et encoder des URLs
Conteneurisation : Docker + Docker Compose
Gestion centralisée des exceptions
Frontend (au choix)

React.js
Streamlit
Qualité & tests

Tests unitaires : pytest
Mocks complets des API externes : Mock de Groq, Mock de Gemini
Modalités pédagogiques
Travail : individuel

Durée : 10 jours

Période : Du 12/01/2026 au 23/01/2026 avant minuit.

Modalités d'évaluation
Mise en situation
Code review
Culture du projet
Livrables
Dépôt GitHub contenant :
Code source complet
README.md (description, installation, technologies)
Diagramme de classes UML
Critères de performance
- Précision IA : Résumés fidèles, traductions exactes, QCM pertinents et valides.
-Qualité de prompt engineer.
- Sécurité & fiabilité : Authentification OAuth 2.0, gestion robuste des erreurs, pas de fuites de données.
- Qualité du code : Couverture de tests ≥ 80 %, architecture modulaire, documentation complète, conteneurisation opérationnelle.