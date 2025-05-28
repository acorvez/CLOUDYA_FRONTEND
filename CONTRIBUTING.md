# Cloudya - Guide de contribution

Merci de votre intérêt à contribuer à Cloudya ! Ce document vous guidera à travers le processus de contribution.

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment puis-je contribuer?](#comment-puis-je-contribuer)
   - [Rapporter des bugs](#rapporter-des-bugs)
   - [Suggérer des améliorations](#suggérer-des-améliorations)
   - [Contribuer au code](#contribuer-au-code)
   - [Ajouter des templates](#ajouter-des-templates)
3. [Style de code](#style-de-code)
4. [Tests](#tests)
5. [Documentation](#documentation)

## Code de conduite

Ce projet et tous ses participants sont régis par notre [Code de conduite](CODE_OF_CONDUCT.md). En participant, vous êtes censé respecter ce code.

## Comment puis-je contribuer?

### Rapporter des bugs

Les bugs sont suivis en tant qu'issues GitHub. Lorsque vous créez une issue pour un bug, incluez:

- Un titre clair et descriptif
- Des étapes précises pour reproduire le problème
- Ce à quoi vous vous attendiez et ce qui s'est réellement passé
- Des notes, logs ou captures d'écran qui aideraient à comprendre le problème

### Suggérer des améliorations

Les suggestions d'améliorations sont également suivies en tant qu'issues GitHub. Incluez:

- Un titre clair et descriptif
- Une description détaillée de l'amélioration suggérée
- Les avantages que cette amélioration apporterait
- Des exemples d'utilisation ou des maquettes si applicable

### Contribuer au code

1. Forker le dépôt
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Commiter vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

#### Process de Pull Request

- Assurez-vous que vos changements respectent les standards de style de code
- Mettez à jour la documentation si nécessaire
- Ajoutez des tests pour couvrir vos changements
- Assurez-vous que tous les tests passent
- Référencez l'issue que votre PR résout, si applicable

### Ajouter des templates

Les templates sont une partie essentielle de Cloudya. Pour contribuer un nouveau template:

1. Créez un nouveau répertoire dans `templates/{terraform,ansible,apps}/{provider}/{template_name}`
2. Incluez un fichier `manifest.yaml` qui décrit le template
3. Ajoutez tous les fichiers nécessaires (Terraform, Ansible, Docker Compose, etc.)
4. Incluez un README qui explique comment utiliser le template
5. Créez une PR avec votre nouveau template

## Style de code

Nous suivons les conventions PEP 8 pour le code Python. De plus:

- Utilisez 4 espaces pour l'indentation (pas de tabulations)
- Limitez la longueur des lignes à 88 caractères
- Utilisez des noms de variables et de fonctions descriptifs
- Commentez votre code, en particulier pour les sections complexes

Nous utilisons [Black](https://github.com/psf/black) pour le formatage du code et [isort](https://pycqa.github.io/isort/) pour trier les imports.

## Tests

Tous les changements majeurs doivent être accompagnés de tests. Nous utilisons pytest pour nos tests.

Pour exécuter les tests:

```bash
pytest
```

## Documentation

La documentation est essentielle pour garder Cloudya accessible à tous les utilisateurs. Lorsque vous ajoutez ou modifiez des fonctionnalités:

- Mettez à jour le README.md si nécessaire
- Ajoutez ou mettez à jour la documentation des fonctions, classes et modules
- Si vous ajoutez une nouvelle commande, assurez-vous qu'elle a une aide claire et concise
- Mettez à jour la documentation dans docs/ si elle existe

---

Merci pour votre contribution à Cloudya!
