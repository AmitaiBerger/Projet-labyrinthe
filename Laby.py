import random



class Case():
    #voisins = [None,None,None,None]
    #contenu = None

    def __init__(self,indice=0):
        self.voisins = [None,None,None,None]# booléens contenant True si la case et conectée à la voisine
        # l'indice 0 est la droite, 1 le haut, 2 la gauche et 3 le bas.
        self.contenu = None# pour l'instant inutile, mais poura contenir des éléments graphiques cosmétiques
        self.i = indice
        self.visibles = {} #Liste des cases visibles c a d les cases sans murs alignees
        self.est_sortie = False

    


class Labyrinthe():

    def __init__(self,hauteur:int,largeur:int):
        self.cases = [Case(i) for i in range(largeur * hauteur)]
        self.largeur=largeur
        self.hauteur=hauteur
        self.sortie = random.randint(0, self.largeur*self.hauteur-1)

    def trier_cases(self):
        """Trie le tableau self.cases selon l'attribut i de chaque case
        pour que self.cases[k].i == k"""
        self.cases.sort(key=lambda case: case.i)

    def afficher_comme_texte(self):# généré par IA parce que peu intéressant et laborieux
        """affiche le labyrinthe sous forme de texte dans la console
        utile pour le debug"""
        print("affichage du labyrinthe")
        for h in range(self.hauteur):
            # ligne du haut
            ligne_haut = ""
            for l in range(self.largeur):
                ligne_haut += "+"
                if self.cases[h*self.largeur+l].voisins[1] != None:
                    ligne_haut += "   "
                else:
                    ligne_haut += "---"
            ligne_haut += "+"
            print(ligne_haut)

            # ligne du milieu
            ligne_milieu = ""
            for l in range(self.largeur):
                indice_actuel = h * self.largeur + l
                
                # Mur gauche
                if self.cases[indice_actuel].voisins[2] != None:
                    ligne_milieu += " "
                else:
                    ligne_milieu += "|"
                
                # --- MODIFICATION D/A ---
                if hasattr(self, 'depart') and indice_actuel == self.depart:
                    ligne_milieu += " D " # Ancien code (si tu le gardes)
                elif hasattr(self, 'joueur1') and indice_actuel == self.joueur1:
                    ligne_milieu += " 👧" # Joueur 1
                elif hasattr(self, 'joueur2') and indice_actuel == self.joueur2:
                    ligne_milieu += " 👦" # Joueur 2
                elif hasattr(self, 'sortie') and indice_actuel == self.sortie:
                    ligne_milieu += " 🚪" # Sortie (ou A)
                else:
                    ligne_milieu += "   "
                # ------------------------

            # Mur droite
            if self.cases[h*self.largeur+self.largeur-1].voisins[0] != None:
                ligne_milieu += " "
            else:
                ligne_milieu += "|"
            print(ligne_milieu)
        # ligne du bas
        ligne_bas = ""
        for l in range(self.largeur):
            ligne_bas += "+"
            if self.cases[(self.hauteur-1)*self.largeur+l].voisins[3] != None:
                ligne_bas += "   "
            else:
                ligne_bas += "---"
        ligne_bas += "+"
        print(ligne_bas)

    
    def directions_voisines(self,indice_centre:int):
        """renvoie la liste directions possibles à partir d'une case donnée
        sous forme d'un entier (une direction impossible est un coté extérieur du labyrinthe)
           droite : 0
           haut : 1
           gauche : 2
           bas : 3
           """

        #print("directions voisins à ", indice_centre)
        directions = [] #
        if not (indice_centre%self.largeur==0):# (pas à gauche)
            directions.append(2)
        if not (indice_centre%self.largeur==self.largeur-1):# pas à droite
            directions.append(0)
        if not (indice_centre//self.largeur==0): # pas en haut
            directions.append(1)
        if not (indice_centre//self.largeur==self.hauteur-1):# on n'est pas en bas
            directions.append(3)
        return directions

    def connecter_cases(self, indiceA, indiceB):
        """Connecte deux cases adjacentes dans les deux sens"""
        dir_A_vers_B = self.direction(indiceA, indiceB)
        dir_B_vers_A = (dir_A_vers_B + 2) % 4
        
        self.cases[indiceA].voisins[dir_A_vers_B] = True
        self.cases[indiceB].voisins[dir_B_vers_A] = True

    def indices_voisins(self,indice_centre:int):
        #print("indices voisins à ", indice_centre)
        vois = []
        if not (indice_centre%self.largeur<=0):# (pas à gauche)
            vois.append(indice_centre-1)
        if not (indice_centre%self.largeur>=self.largeur-1):
            vois.append(indice_centre+1)
        if not (indice_centre//self.largeur<=0): # pas en haut
            vois.append(indice_centre-self.largeur)
        if not (indice_centre//self.largeur>=self.hauteur-1):# on n'est pas en bas
            vois.append(indice_centre+self.largeur)
        return vois
    
    def direction(self,indiceA,indiceB):# généré par IA, utile pour la fonction Wilson
        """renvoie la direction de B par rapport à A
           droite : 0
           haut : 1
           gauche : 2
           bas : 3
           """
        if indiceB == indiceA+1:
            return 0
        elif indiceB == indiceA-1:
            return 2
        elif indiceB == indiceA-self.largeur:
            return 1
        elif indiceB == indiceA+self.largeur:
            return 3
        else:
            return None


    def generer_par_Wilson(self):
        """crée un labyrinthe avec l'algorithme de Wilson.
        documentaiton en anglais :
        https://en.wikipedia.org/wiki/Maze_generation_algorithm#Wilson's_algorithm
        """
        print("generation par Wilson")
        
        cases_dans_laby = set()
        premiere = random.randrange(self.largeur * self.hauteur)
        cases_dans_laby.add(premiere)
        #print("premiere case du Labyrinthe :", premiere)
        cases_non_generees = set(range(self.largeur * self.hauteur)) - cases_dans_laby
        while(cases_non_generees):
            #print("génération d'une branche")
            # génération de la premiere case de la branche
            caseActu = random.choice(list(cases_non_generees))
            
            #print("à partir de :",caseActu)
            cheminActu = [caseActu]
            while caseActu not in cases_dans_laby:
                voisins = self.indices_voisins(caseActu)
                prochain = random.choice(voisins)
                #print("prochain :",prochain)
                if(prochain in cheminActu):# si on fait une boucle, on supprime
                    #print("boucle")
                    cheminActu = cheminActu[:cheminActu.index(prochain)+1]
                else:
                    cheminActu.append(prochain)
                caseActu = prochain

            # on a trouvé un chemin qui rejoint le labyrinthe
            #print("chemin trouvé :",cheminActu)

            # On ajoute le chemin au labyrinthe
            for i in range(len(cheminActu)-1):
                #if not any(c.i == cheminActu[i] for c in self.cases):
                self.connecter_cases(cheminActu[i], cheminActu[i + 1])
                cases_dans_laby.add(cheminActu[i])
                cases_non_generees.discard(cheminActu[i])
            #self.cases.append(Case(cheminActu[-1]))
            #self.cases[-1].voisins[dir] = True

        self.cases[self.sortie].est_sortie = True
        print("labyrinthe généré")

    def visibles(self):
        for case in self.cases:
            vision = {}
            vision["droite"] = []
            vision["haut"] = []
            vision["gauche"] = []
            vision["bas"] = []
            position = case.i
            while self.cases[position].voisins[0] == True:
                position += 1
                vision["droite"].append(position)
            position = case.i
            while self.cases[position].voisins[1] == True:
                position -= self.largeur
                vision["haut"].append(position)
            position = case.i
            while self.cases[position].voisins[2] == True:
                position -= 1
                vision["gauche"].append(position)
            position = case.i
            while self.cases[position].voisins[3] == True:
                position += self.largeur
                vision["bas"].append(position)
            case.visibles = vision

    def creuser_trous(self, taux_ouverture: float = 0.4):
        """
        Supprime des culs-de-sac pour créer des boucles (chemins alternatifs).
        
        :param taux_ouverture: Float entre 0 et 1. 
                               0.0 = ne rien faire (labyrinthe parfait).
                               1.0 = supprimer tous les culs-de-sac (labyrinthe 'braid').
                               0.4 est une bonne valeur pour avoir quelques chemins principaux.
        """
        import random
        print(f"Ajout de cycles (taux: {taux_ouverture})...")

        # 1. Identifier tous les culs-de-sac
        # Un cul-de-sac est une case qui a exactement 1 seul voisin connecté (True)
        culs_de_sac = []
        for case in self.cases:
            nb_connexions = 0
            # On suppose que case.voisins est une liste de 4 éléments [D, H, G, B]
            for v in case.voisins:
                if v == True: 
                    nb_connexions += 1
            
            if nb_connexions == 1:
                culs_de_sac.append(case.i)

        # 2. Mélanger pour ne pas toujours ouvrir les mêmes zones
        random.shuffle(culs_de_sac)

        # 3. Calculer combien on en ouvre
        nombre_a_ouvrir = int(len(culs_de_sac) * taux_ouverture)

        # 4. Percer les murs
        compteur = 0
        for index_case in culs_de_sac:
            if compteur >= nombre_a_ouvrir:
                break

            # On cherche les voisins "physiques" (sur la grille)
            voisins_possibles = self.indices_voisins(index_case)
            
            # On cherche parmi eux ceux qui sont séparés par un MUR
            candidats_a_percer = []
            for voisin_idx in voisins_possibles:
                direction = self.direction(index_case, voisin_idx)
                
                # Si la connexion n'est pas True, c'est un mur qu'on peut casser
                if self.cases[index_case].voisins[direction] != True:
                    candidats_a_percer.append(voisin_idx)

            # Si on a trouvé des murs à casser, on en choisit un au hasard
            if candidats_a_percer:
                voisin_choisi = random.choice(candidats_a_percer)
                self.connecter_cases(index_case, voisin_choisi)
                compteur += 1
                
        print(f"{compteur} trous creusés.")

    def creuser_trous_intelligents(self, longueur_max_probabilite: int = 10):
        """
        Ouvre les culs-de-sac avec une probabilité dépendante de la longueur de leur branche.
        
        :param longueur_max_probabilite: La longueur de branche à partir de laquelle 
                                         on a ~100% de chance d'ouvrir le bout.
        """
        import random
        print("Création de boucles intelligentes...")
        compteur = 0

        for case_actuelle in self.cases:
            # 1. Vérifier si c'est un cul-de-sac (1 seul voisin connecté)
            voisins_connectes = [v for v in case_actuelle.voisins if v is True]
            if len(voisins_connectes) != 1:
                continue

            # 2. Mesurer la longueur de la branche (remonter jusqu'à un carrefour)
            longueur_branche = 0
            courant = case_actuelle.i
            precedent = -1 # Pour ne pas revenir en arrière
            
            while True:
                # Compter les connexions de la case courante
                nb_connexions = 0
                prochain_candidat = -1
                
                # On regarde les vraies connexions existantes
                for idx_voisin in self.indices_voisins(courant):
                    dir_v = self.direction(courant, idx_voisin)
                    if self.cases[courant].voisins[dir_v] is True:
                        nb_connexions += 1
                        if idx_voisin != precedent:
                            prochain_candidat = idx_voisin
                
                # Si on arrive à un carrefour (plus de 2 chemins) ou au bout, on arrête
                if nb_connexions > 2:
                    break
                
                # Si on est dans le couloir, on avance
                longueur_branche += 1
                precedent = courant
                courant = prochain_candidat
                
                # Sécurité pour éviter boucle infinie (si le labyrinthe est déjà tressé)
                if courant == -1: 
                    break

            # 3. Calcul de la probabilité
            # Si longueur 1 -> proba 0. Si longueur >= max -> proba 1.0
            if longueur_branche <= 1:
                proba = 0.0
            else:
                # Formule linéaire : on augmente la chance à mesure que la branche est longue
                proba = (longueur_branche - 1) / longueur_max_probabilite
                proba = min(proba, 1.0) # On plafonne à 100%

            # 4. Tentative d'ouverture
            if random.random() < proba:
                # On cherche un mur à casser (qui mène vers une case qui N'EST PAS le parent)
                # Le parent est la case qui nous permet de remonter la branche
                
                # Retrouver l'index du voisin connecté (le chemin du retour)
                voisin_retour = -1
                candidats_a_percer = []
                
                liste_indices = self.indices_voisins(case_actuelle.i)
                for v_idx in liste_indices:
                    dir_v = self.direction(case_actuelle.i, v_idx)
                    if self.cases[case_actuelle.i].voisins[dir_v] is True:
                        voisin_retour = v_idx
                    else:
                        candidats_a_percer.append(v_idx)
                
                # On perce vers un voisin qui n'est pas le chemin du retour
                if candidats_a_percer:
                    voisin_choisi = random.choice(candidats_a_percer)
                    self.connecter_cases(case_actuelle.i, voisin_choisi)
                    compteur += 1

        print(f"{compteur} boucles intelligentes créées.")
    
    def _calculer_toutes_distances(self, sources):
        """
        Retourne un dictionnaire {index_case: distance} depuis une ou plusieurs sources.
        sources peut être un entier (une case) ou une liste (le chemin principal).
        """
        if isinstance(sources, int):
            sources = [sources]
            
        distances = {i: -1 for i in range(len(self.cases))}
        file_attente = []

        for src in sources:
            distances[src] = 0
            file_attente.append(src)
        
        head = 0
        while head < len(file_attente):
            courant = file_attente[head]
            head += 1
            dist_actuelle = distances[courant]
            
            # Voisins connectés uniquement (passage ouvert)
            voisins_physiques = self.indices_voisins(courant)
            for v in voisins_physiques:
                dir_v = self.direction(courant, v)
                if self.cases[courant].voisins[dir_v] is True:
                    if distances[v] == -1:
                        distances[v] = dist_actuelle + 1
                        file_attente.append(v)
        return distances

    def _trouver_chemin(self, debut, fin):
        """Retrouve le chemin unique (liste d'indices) entre A et B"""
        pile = [(debut, [debut])]
        visites = set()
        while pile:
            (sommet, chemin) = pile.pop()
            if sommet == fin:
                return chemin
            if sommet not in visites:
                visites.add(sommet)
                voisins = self.indices_voisins(sommet)
                for v in voisins:
                    d = self.direction(sommet, v)
                    if self.cases[sommet].voisins[d] is True and v not in visites:
                        pile.append((v, chemin + [v]))
        return []

    def placer_depart(self, ratio_distance_min: float = 0.6,debug=False):
        """
        1. Place la sortie (trappe) au hasard.
        2. Place le départ à une distance suffisante.
        :param ratio_distance_min: 0.6 signifie que le joueur sera placé à au moins 
                                   60% de la distance maximale possible depuis la sortie.
        """
        
        
        # 2. Calcul des distances depuis cette sortie vers tout le reste
        distances = self._calculer_toutes_distances(self.sortie)
        
        # Trouver la distance maximale existante dans ce labyrinthe (le point le plus loin)
        max_dist = max(distances.values())
        seuil_distance = int(max_dist * ratio_distance_min)
        
        # 3. Récupérer les candidats valides (assez loin)
        candidats_depart = [case_id for case_id, dist in distances.items() if dist >= seuil_distance]
        
        if not candidats_depart:
            # Sécurité si le ratio est trop haut, on prend juste le plus loin
            self.depart = max(distances, key=distances.get)
        else:
            self.depart = random.choice(candidats_depart)
        self.cases[self.sortie].contenu = "Sortie"
        if debug:
            print(f"Jeu configuré : Départ {self.depart} -> Sortie {self.sortie} (Distance: {distances[self.depart]})")

    def creuser_trous_organiques(self, seuil_min: int = 5, longueur_ref: int = 15):
        """
        :param seuil_min: Distance en dessous de laquelle on ne creuse JAMAIS (0%).
                          Augmente ce chiffre pour supprimer les petites boucles.
        :param longueur_ref: Distance à laquelle on creuse TOUJOURS (100%).
        """
        import random
        
        if not hasattr(self, 'depart') or not hasattr(self, 'sortie'):
            print("Erreur: Définissez départ et sortie avant.")
            return

        print(f"Creusement : Rien sous {seuil_min} cases, progressif jusqu'à {longueur_ref}...")

        chemin_principal = self._trouver_chemin(self.depart, self.sortie)
        dist_au_tronc = self._calculer_toutes_distances(chemin_principal)
        
        compteur = 0
        
        for case in self.cases:
            # On ne traite que les culs-de-sac
            nb_connexions = sum(1 for v in case.voisins if v is True)
            if nb_connexions != 1:
                continue
            
            if case.i == self.depart or case.i == self.sortie:
                continue

            dist = dist_au_tronc[case.i]
            
            # --- NOUVELLE LOGIQUE ---
            
            if dist < seuil_min:
                # Si on est trop près du chemin principal, on ne touche à rien !
                # Cela garantit aucune boucle courte.
                proba = 0.0
            elif dist >= longueur_ref:
                # Si on est très loin, on ouvre forcément
                proba = 1.0
            else:
                # Entre les deux, la probabilité augmente linéairement
                # Exemple : si seuil=5 et ref=15.
                # A dist 5 -> 0%
                # A dist 10 -> 50%
                # A dist 15 -> 100%
                proba = (dist - seuil_min) / (longueur_ref - seuil_min)
            
            # ------------------------

            if random.random() < proba:
                # Recherche des murs à casser
                voisins_potentiels = self.indices_voisins(case.i)
                murs = []
                for v in voisins_potentiels:
                    d = self.direction(case.i, v)
                    if self.cases[case.i].voisins[d] is not True:
                        murs.append(v)
                
                if murs:
                    cible = random.choice(murs)
                    self.connecter_cases(case.i, cible)
                    compteur += 1
                    
        print(f"{compteur} boucles créées.") 

    def placer_deux_joueurs(self, ratio_eloignement: float = 0.6):
        """
        Place joueur1 et joueur2 de façon à ce qu'ils soient :
        - Loin de la sortie (déjà définie dans self.sortie)
        - Loin l'un de l'autre
        """
        import random

        if not hasattr(self, 'sortie'):
            print("Erreur : La sortie doit être définie avant de placer les joueurs.")
            return

        # --- ETAPE 1 : Carte des distances depuis la Sortie ---
        dists_sortie = self._calculer_toutes_distances(self.sortie)
        max_dist_sortie = max(dists_sortie.values())
        
        # --- ETAPE 2 : Placer Joueur 1 ---
        # On choisit J1 parmi les 20% des cases les plus éloignées de la sortie
        # Cela garantit que J1 est au fond d'une impasse profonde.
        seuil_j1 = int(max_dist_sortie * 0.8)
        candidats_j1 = [i for i, d in dists_sortie.items() if d >= seuil_j1]
        
        if not candidats_j1: # Sécurité cas extrême
            self.joueur1 = max(dists_sortie, key=dists_sortie.get)
        else:
            self.joueur1 = random.choice(candidats_j1)

        # --- ETAPE 3 : Carte des distances depuis Joueur 1 ---
        # Maintenant on veut savoir ce qui est loin de J1
        dists_j1 = self._calculer_toutes_distances(self.joueur1)

        # --- ETAPE 4 : Placer Joueur 2 ---
        # On cherche le meilleur candidat pour J2.
        # Critères :
        # A. Doit être assez loin de la sortie (au moins ratio * max_dist)
        # B. Parmi ceux qui respectent A, prendre le plus loin de J1
        
        seuil_min_sortie_j2 = int(max_dist_sortie * ratio_eloignement)
        
        meilleur_j2 = -1
        meilleure_dist_j1 = -1
        
        candidats_j2 = []

        for i in range(len(self.cases)):
            if i == self.sortie or i == self.joueur1:
                continue
            
            # Condition A : Est-ce assez loin de la sortie ?
            if dists_sortie[i] < seuil_min_sortie_j2:
                continue
            
            # On stocke les candidats valides
            candidats_j2.append(i)

            # Recherche du maximum de distance par rapport à J1
            if dists_j1[i] > meilleure_dist_j1:
                meilleure_dist_j1 = dists_j1[i]
                meilleur_j2 = i
        
        # Si on a trouvé un candidat idéal
        if meilleur_j2 != -1:
            # Astuce : Pour ajouter un peu de variété et ne pas toujours prendre
            # LE pixel le plus loin mathématiquement, on peut prendre un top 3
            # des candidats les plus loins de J1. Ici je reste simple :
            self.joueur2 = meilleur_j2
        else:
            # Fallback : Si le labyrinthe est trop petit ou les contraintes trop fortes,
            # on prend juste le point le plus loin de J1 sans se soucier de la sortie.
            self.joueur2 = max(dists_j1, key=dists_j1.get)

        print(f"Placement : Sortie={self.sortie}")
        print(f"J1={self.joueur1} (Dist Sortie: {dists_sortie[self.joueur1]})")
        print(f"J2={self.joueur2} (Dist Sortie: {dists_sortie[self.joueur2]}, Dist J1: {dists_j1[self.joueur2]})")





