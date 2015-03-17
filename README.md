#PANDROIDE
Recap des principals commandes:

recuperer le depot pour la premiere fois (totalité du projet): 
	git clone <une adresse>

recuperer la derniere version du depot:
	git pull

ajouter un fichier (encore jamais versionné): 
	git add  <nom fichier>

mettre a jour les fichiers: 
	git commit -a -m «commentaire » 
	git push


Pour les moins famillier avec cet outils si vous avez des problemes de conflits qui ne se resolve pas automatiquement, preferez regler les conflits a la main c’est plus simple.
En recuperent la derniere version du depot et en ajoutant vos modifications.
En theorie si on se separt bien le travail, il ne devrait pas en avoir.


un tuto asses complet sur le site du zeros:
http://fr.openclassrooms.com/informatique/cours/gerez-vos-codes-source-avec-git


Régle de courtoisis:
	- Toujours faire des commits en expliquant (en quelques mots ce que l’on a change)
	- On ne modifie jamais du code de quelqu’un (parce qu’on voit un optimissation ou un bug…). 
	  Soit on laisse un commentaire en debut de fichier ou un mail. 
