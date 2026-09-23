




''' 
    dijka, il faut un visited, et on marque le visited
    seulement une fois qu on a quitter le curr node et qu on a a safe les short path
    donc il faut garder track, de ou on est, ou on va et le cout pour les mouvements
    ensuite additioner ce coute pour chaque node, et une fois fait on bouge to
    the next node et on marque l ancien node comme visited. Ensuite, il suffira
    de backtrack la listes des nodes qu on a save, cette liste ne sera constituer 
    que des nodes aux coups les plus bas.

    Il faut aussi utiliser heapq (check si obligatoire ou si je peux contourner)

    
'''
