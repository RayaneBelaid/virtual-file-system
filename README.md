## Virtual File System
***
Pour exécuter le programme, il suffit d'avoir un environnement python3 et de simplement lancer la commande : `python filesystm.py ` 

Un fichier `vfs` sera créé pour stocker les informations du disque virtuel.

Voici une liste des commandes disponibles pour notre simulation :

Soit `x` et `y` deux paramètres.

*	`help` : lister toutes les commandes existantes sur notre système de fichiers 
*	`quit` : quitter le simulateur  
* `ls` :  lister les répertoires et les fichiers existants dans le système
*	`check` : vérifier le bitmap
*	`cd x` : se déplacer vers le répertoire x
*	`open x` : ouvrir le fichier x, s’il n’existe pas, il sera créé
*	`close` : fermer le fichier ouvert 
*	`mkdir x`: créer un répertoire nommé x
*	`write x` : écrire x dans le fichier ouvert
*	`read` : lire le fichier ouvert
*	`rm x` : supprimer le fichier x
*	`rmdir x` : supprimer le répertoire x, ainsi que ses sous-répertoires et ses fichiers
*	`cp x y` : faire une copie de x dans y

