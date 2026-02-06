import json
import os

class User:
    
    
    FICHIER = "user.json"

    def __init__(self):
        users = self._charger_users()

        if len(users) == 0:
            self.userid = 1
        else:
            self.userid = len(users) + 1

        
        
        
    def _charger_users(self):
        if not os.path.exists(self.FICHIER):
            return []

        try:
            with open(self.FICHIER, "r", encoding="utf-8") as f:
                contenu = f.read().strip()
                if contenu == "":
                    return []
                return json.load(contenu)
        except json.JSONDecodeError:
            return []


lass ressource:
    
    __init__(self, id:int, name:str, type : str , status : str ):
        self.id = id
        self.name = name
        self.type = type
        self.status = status
        

class universite :
    
        __init__(self):
            self.bibliotheque 
            self.equipement
            self.salle
        
        
