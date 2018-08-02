NE SONT AFFICHÉES QUE LES MODIFICATIONS  
  
Pour plus de détails, observer les notes prises sur les versions >0.0  
(Docstring au début du programme)  
  
0.0:  
	Rigidité absolue si déplacement impossible  
	Fonction de coût qui dépend de:  
		distance d'un amas à la sortie, distance entre le barycentre avant  
		et après déplacement, distance de chaque disque au barycentre  
	Pour chaque amas:  
		Calcul de la trajectore -> déplacement du barycentre  
		Puis calcul de générations successives en ne gardant que les 4  
		meilleures à la fin de chaque calcul  

0.1:  
	Correction de la fonction déplacement possible (si un disque sort pendant le  
	calcul, il ne doit plus être pris en compte)  
	Aléatoire:  
		On explore une surface et on y choisit aléatoirement un point au lieu  
		de choisir aléatoirement un vecteur directement  
	Ajout de l'utilisation du fichier coordonnees pour visionner le mouvement après  
  
0.2:  
	Fonction de cout ne prend QUE en compte la distance à la sortie  
  
0.3:  
	si un disque quelconque peut se déplacer librement (dans un amas ou non)  
	alors il se déplace  
	Grande augmentation de la surface et recherche et diminution de la précision  
	de recherche  
