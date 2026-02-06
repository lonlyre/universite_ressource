import json
import os

class Users:

    def __init__(self):
        self.users = self._charger_users()

    def _charger_users(self):
        if not os.path.exists(self.FICHIER):
            return []
        with open(self.FICHIER, "r", encoding="utf-8") as file:
            contenu = file.read().strip()
            if contenu == "":
                return []
            return json.load(contenu)
        
    def ajouter_user(self):
        id_user= len(self.users) + 1
        username = str(input('nom utilisateur ?'))
        password = str(input('Password ?'))
        emprunt = {'livre':[], 'equipement':[], 'salle':[] }
        new_user ={'id_user':id_user,'username':username,'password':password,'emprunt':new_user }
        self.users.append(new_user)
        with open("user.json", "w", encoding="utf-8") as file:
            json.dump(self.users, file, indent=4, ensure_ascii=False)
        return new_user
        
        
        
