NE SONT AFFICHÉES QUE LES MODIFICATIONS

Alpha:
	Tests avec 2 disques

Beta:
	Plus de 2 corps
	Beta3:
		Mise en place du quadrillage pour optimiser les calculs
	Beta4:
		Fonction qui détermine le voisinage indirect d'un disque donné
		(Sert dans 1.0, mais est dans beta car pas de mouvement,
		contient le mouvement de beta3 et cette fonction)

0.x:
	Début du TIPE
	Version simple:
		Calcul de la trajectoire voulue avec une équation de droite, puis 			
    calcul des contraintes avec un projeté orthogonal sur les disques 			
    voisins directs
1.x:
	Prise en compte des voisins indirects (voisin du voisin du voisin...)
	1.0:
		Calcul de la force total en sommant toutes les composantes des
		voisins puis en renormalisant
	1.1:
		Ordre dans le calcul, les plus proches de la sortie d'abord
		Tentative de restreindre les disques qui appliquent une force sur celui 		
    considéré, en limitant à 2: les 2 devant qui ont déjà été calculés
		intuitivement, ceux derrière seraient négligeables car appliqueraient
		une force moindre
		Puis moyenne des directions pour obtenir la nouvelle direction
	1.2.x:
		Calcul des contraintes en prenant en compte la chaîne entière des
		disques voisins indirect (en partant de la fin de la chaîne)
		Grâce à une succession de projeté orthogonaux
		1.2.0:
			Boucle permettant d'indexé pour chaque disque l'ordre de 
			calcul à suivre dans la chaîne de voisins indirects
		1.2.1:
			Ajout de la contrainte absolue des murs
		1.2.2:
			Ajout de la rotation du vecteur direction pour explorer les 				
      déplacements sur une surface proche
