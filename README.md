````markdown
# 📘 DOCUMENTATION TECHNIQUE  
# Application de Gestion Universitaire

---

## 📄 Page de garde

**Nom du projet :** Application de Gestion Universitaire  
**Auteur :** [Votre Nom]  
**Formation :** [Nom de la formation]  
**Établissement :** [Nom de l’établissement]  
**Année académique :** 2024 – 2025  
**Encadrant :** [Nom de l’enseignant]  

---

# 📑 Table des matières

1. [Résumé exécutif](#résumé-exécutif)  
2. [Introduction](#introduction)  
3. [Analyse du besoin](#analyse-du-besoin)  
4. [Description technique détaillée](#description-technique-détaillée)  
5. [Architecture de l’application](#architecture-de-lapplication)  
6. [Choix techniques](#choix-techniques)  
7. [Guide d’installation et d’utilisation](#guide-dinstallation-et-dutilisation)  
8. [Tests et validation](#tests-et-validation)  
9. [Perspectives d’amélioration](#perspectives-damélioration)  
10. [Conclusion](#conclusion)  

---

# Résumé exécutif

L’Application de Gestion Universitaire est un logiciel développé en Python permettant la gestion des ressources d’un établissement universitaire (livres, équipements, salles) ainsi que la gestion des utilisateurs (administrateurs, professeurs, étudiants).

Le système permet :

- L’authentification sécurisée des utilisateurs  
- L’emprunt et le retour de ressources  
- L’administration complète des ressources  
- La gestion des comptes utilisateurs  
- La persistance des données via fichiers JSON  

L’objectif principal est d’automatiser et sécuriser la gestion des ressources universitaires à travers une interface graphique intuitive développée avec Tkinter.

---

# Introduction

Dans les établissements universitaires, la gestion des ressources (bibliothèque, matériel, salles) peut rapidement devenir complexe.

Les problématiques principales sont :

- Mauvaise gestion des stocks
- Absence de traçabilité des emprunts
- Gestion manuelle inefficace
- Manque de sécurité dans la gestion des utilisateurs

Cette application a été développée afin de proposer une solution centralisée, sécurisée et simple d’utilisation.

---

# Analyse du besoin

## 🎯 Objectifs principaux

- Centraliser la gestion des ressources universitaires
- Permettre un système d’authentification sécurisé
- Gérer différents rôles utilisateurs
- Assurer la traçabilité des emprunts
- Garantir l’intégrité des données

## 👥 Public cible

- Administrateurs universitaires  
- Professeurs  
- Étudiants  

## 📌 Contraintes techniques

- Utilisation exclusive de Python
- Persistance des données en fichiers JSON
- Interface graphique simple (Tkinter)
- Sécurisation des mots de passe (bcrypt)
- Limitation d’emprunt selon le rôle

---

# Description technique détaillée

Le code principal est contenu dans le fichier :

📄 `universite.py` :contentReference[oaicite:0]{index=0}  

## 📂 Structure des classes

### 1️⃣ Classe `jsonObject`

Rôle : Gestion générique des fichiers JSON.

Fonctions principales :

```python
def charger_json(self, filename)
def save_json(self, filename, data)
def next_id(self, tab, key_id)
def find_by_criteria(self, tab, **criteria)
````

Fonctionnalités :

* Chargement sécurisé des fichiers JSON
* Sauvegarde formatée
* Génération automatique d’ID
* Recherche multicritère

---

### 2️⃣ Classe `Users`

Responsable de :

* Création d’utilisateurs
* Authentification
* Suppression
* Modification
* Gestion des rôles

#### 🔐 Sécurité implémentée

* Hashage des mots de passe avec `bcrypt`
* Interdiction de supprimer l’utilisateur `root`
* Seul `root` peut créer un administrateur
* Contrôle des permissions backend

Exemple de hashage :

```python
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
```

---

### 3️⃣ Classe `universite`

Gestion des ressources :

* `livre`
* `equipement`
* `salle`

#### Fonctions principales :

```python
emprunter_ressource()
retourner_ressource()
ajouter_ressource()
delete_ressource_by_name()
get_emprunts_user()
```

#### 🎓 Règles métier

| Rôle       | Limite d’emprunt |
| ---------- | ---------------- |
| Étudiant   | 3 ressources     |
| Professeur | 10 ressources    |
| Admin      | Illimité         |

---

### 4️⃣ Classe `App`

Interface graphique réalisée avec Tkinter :

* Menu principal
* Connexion / Inscription
* Gestion des ressources
* Administration
* Gestion des emprunts

---

# Architecture de l’application

## 🏗 Type d’architecture

Architecture modulaire orientée objet.

### 📌 Organisation logique :

```
┌─────────────────────────────┐
│ Interface graphique (App)   │
└───────────────┬─────────────┘
                │
┌───────────────┴─────────────┐
│ Logique métier              │
│ - Users                     │
│ - universite                │
└───────────────┬─────────────┘
                │
┌───────────────┴─────────────┐
│ Couche persistance (JSON)   │
└─────────────────────────────┘
```

---

# Choix techniques

## 🐍 Python

Choisi pour :

* Simplicité
* Rapidité de développement
* Richesse des bibliothèques

## 🖥 Tkinter

* Bibliothèque native Python
* Interface légère
* Compatible multi-plateforme

## 🔐 bcrypt

* Sécurisation des mots de passe
* Protection contre attaques par force brute

## 📁 JSON

* Stockage simple
* Lisible
* Facilement modifiable

---

# Guide d’installation et d’utilisation

## 🔧 Prérequis

* Python 3.10+
* Bibliothèque bcrypt
* Bibliothèque Json
* Bibliothèque tkinter

Installation :

```bash
pip install bcrypt
pip install json
pip install tk
```
ou 

```bash

apt install python3-bcrypt python3-json python3-tk

```


## ▶️ Lancement

```bash
python universite.py
```

## 🔑 Comptes par défaut

* **root / (mot de passe par défaut configuré)**
* etudiant1 / 1234
* prof1 / 1234

---

# Tests et validation

## ✔ Tests fonctionnels réalisés

* Création utilisateur
* Connexion sécurisée
* Emprunt avec limite
* Retour de ressource
* Suppression sécurisée
* Protection compte root

## ✔ Tests de sécurité

* Vérification hash mot de passe
* Contrôle d’accès administrateur
* Protection backend

## ✔ Tests de robustesse

* Fichier JSON vide
* Ressource inexistante
* Tentative d’emprunt sans stock

---

# Perspectives d’amélioration

* Migration vers base de données SQL
* Interface plus moderne (PyQt / Web)
* Système de journalisation (logs)
* Gestion des dates d’emprunt
* Notifications de retard
* API REST
* Authentification à double facteur
* Tests unitaires automatisés (pytest)

---

# Conclusion

L’Application de Gestion Universitaire répond efficacement aux besoins identifiés :

* Gestion centralisée des ressources
* Sécurisation des accès
* Interface intuitive
* Architecture modulaire évolutive

Le projet démontre :

* Maîtrise de la programmation orientée objet
* Gestion des fichiers JSON
* Implémentation de règles métier
* Sécurisation des données sensibles
* Conception d’interface graphique

Ce projet constitue une base solide pouvant évoluer vers une application professionnelle complète.

---

# 🎓 Fin de la documentation


