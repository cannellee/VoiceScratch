import re

text="Avence de 145 pixels. Tourna droite. Annule l'action précédente. Supprimer toutes les commandes. Recule de 23 pixels. Avence de 10 pixels. Puis tourna gauche."


match=re.search("tourn[ea][zr]?\W.*gauche\D*(\d+)?°?", text, re.IGNORECASE)
print("Tourner à gauche :", match)
print(match.group(1))

match=re.search("tourn[ea][zr]?\W.*droite\D*(\d+)?°?", text, re.IGNORECASE)
print("Tourner à droite :", match)
print(match.group(1))
