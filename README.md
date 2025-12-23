# TP-IHM
# Database Schema Designer:

Une application de bureau interactive conçue pour modéliser des schémas de bases de données relationnelles, 
générer du code SQL et visualiser les relations entre les tables de manière intuitive.

## Fonctionnalités Principales

- **Conception Visuelle (Canvas) :Ajoutez des tables et déplacez-les librement sur un espace de travail graphique.
- **Gestion des Attributs :Ajouter, modifier ou supprimer des colonnes avec gestion des types (INTEGER, TEXT, etc.) et des contraintes (Primary Key, Not Null).
- **Système de Relations :Créez des relations (1:N, 1:1, N:N). Le système génère automatiquement les tables de jointure pour les relations N:N.
- **Génération SQL automatique :Visualisation en temps réel du script "CREATE TABLE" correspondant à votre schéma.
- **Console SQL intégrée :Testez et exécutez vos commandes SQL directement sur une base de données SQLite intégrée.

---

## Architecture du Projet:

Le projet suit le modèle *MVC* (Modèle-Vue-Contrôleur) :
- *Model (schema.py)* : Gère la logique des données et la génération du SQL.
- *View (main_view.py, table_item.py, etc.)* : Interface utilisateur et éléments graphiques.
- *Controller (main_controller.py)* : Le cerveau qui relie l'interface à la logique.

---

## MainController:

Le fichier "main_controller.py" est le composant central du projet. Voici ses responsabilités principales :

1. **Gestion des Événements (_connect)** : 
   Il lie les clics sur les boutons de l'interface (Ajouter table, relation, etc.) aux fonctions logiques.
   
2. *Cycle de Vie des Éléments Graphiques* :
   - draw_table : Transforme une table du "Model" en un objet visuel (TableItem) sur le canvas.
   - redraw : Actualise tout l'espace de travail dès qu'un changement est effectué (modification d'attribut ou de relation).

3. *Logique de Modélisation* :
   - add_attribute / modify_attribute : Ouvre les dialogues, récupère les données saisies par l'utilisateur et met à jour le modèle.
   - add_relationship : Gère la création de clés étrangères entre les tables selon le type de relation choisi.

4. *Synchronisation Visualisation-Données* :
   - Il calcule en temps réel la position des lignes de relation ("update_relationships") pour qu'elles suivent les tables lorsqu'on les déplace à la souris.
