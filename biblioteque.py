import json
import os

# gestion des objets Json et ajout id et recherhe par critere

class jsonObject:

    def charger_json(self, filename):
        if not os.path.exists(filename):
            return []
        with open(filename, "r", encoding="utf-8") as file:
            contenu = file.read().strip()
            if contenu == "":
                return []
            return json.loads(contenu)

    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def next_id(self, tab, key_id):
        if tab == []:
            return 1
        return tab[-1][key_id] + 1

    def find_by_criteria(self, tab, **criteria):
        for item in tab:
            if all(item.get(key) == value for key, value in criteria.items()):
                return item
        return None


# classe user TODO : ajouter l'emprunt, les roles 

class Users(jsonObject):

    def __init__(self):
        self.users = self.charger_json("user.json")

    def ajouter_user(self):
        id_user = self.next_id(self.users, 'id_user')
        username = str(input('nom utilisateur ? '))
        password = str(input('Password ? '))
        emprunt = {'livre': [], 'equipement': [], 'salle': []}
        role = str(input('role ? (proff, etudiant) '))
        new_user = {
            'id_user': id_user,
            'username': username,
            'password': password,
            'emprunt': emprunt,
            'role': role
        }
        self.users.append(new_user)
        self.save_json("user.json", self.users)
        return new_user

    def supp_user_by_username_and_password(self):
        username = input('username ? ')
        password = input('password ? ')

        user = self.find_by_criteria(
            self.users,
            username=username,
            password=password
        )

        if not user:
            return False

        self.users.remove(user)
        self.save_json("user.json", self.users)
        return True

    def modfify_user_with_username_and_password(self):
        username = input('username ? ')
        password = input('password ? ')

        user = self.find_by_criteria(
            self.users,
            username=username,
            password=password
        )

        if not user:
            return False

        user['username'] = input('new username ? ')
        user['password'] = input('new password ? ')

        self.save_json("user.json", self.users)
        return True


# experimental class pour les objects de la bibliotheque, equipement et salle

class ressource(jsonObject):

    def __init__(self, file: str):
        data = self.charger_json(file)
        self.id = self.next_id(data, 'id')
        self.name = str(input('nom ? '))


class equipement(ressource):
    def __init__(self):
        super().__init__("equipement.json")
        existing = self.find_by_criteria(
            self.charger_json("equipement.json"),
            name=self.name
        )
        if existing:
            self.stock = existing.get('stock', 1) + 1
        else:
            self.stock = 1


class livre(ressource):
    def __init__(self):
        super().__init__("bibliotheque.json")
        existing = self.find_by_criteria(
            self.charger_json("bibliotheque.json"),
            name=self.name
        )
        if existing:
            self.stock = existing.get('stock', 1) + 1
        else:
            self.stock = 1


class salle(ressource):
    def __init__(self):
        super().__init__("salle.json")
        self.capacity = int(input('capacity ? '))
        self.status = 'disponible'


# experimental class pour les objects de la bibliotheque, equipement et salle

class universite(jsonObject):

    def __init__(self):
        self.bibliotheque = self.charger_json("bibliotheque.json")
        self.equipement = self.charger_json("equipement.json")
        self.salle = self.charger_json("salle.json")

    def ajouter_livre(self):
        
        new_livre_obj = livre()

        existing = self.find_by_criteria(
            self.bibliotheque,
            name=new_livre_obj.name
        )

        if existing:
            existing['stock'] = new_livre_obj.stock
            self.save_json("bibliotheque.json", self.bibliotheque)
            return existing

        new_livre = {
            'id_livre': new_livre_obj.id,
            'name': new_livre_obj.name,
            'stock': new_livre_obj.stock,
            'status': 'disponible'
        }

        self.bibliotheque.append(new_livre)
        self.save_json("bibliotheque.json", self.bibliotheque)
        return new_livre

    def ajouter_equipement(self):
        new_equipement_obj = equipement()
        
        exist = self.find_by_criteria(
            self.equipement,
            name=new_equipement_obj.name
        )
        
        if exist:
            exist['stock'] = new_equipement_obj.stock
            self.save_json("equipement.json", self.equipement)
            return exist
        
        new_equipement = {
            'id_equipement': new_equipement_obj.id,
            'name': new_equipement_obj.name,
            'stock': new_equipement_obj.stock,
            'status': 'disponible'
        }  
        
        self.equipement.append(new_equipement)
        self.save_json("equipement.json", self.equipement)
        return new_equipement
    
    def ajouter_salle(self):
        new_salle_obj = salle()
        
        new_salle = {
            'id_salle': new_salle_obj.id,
            'name': new_salle_obj.name,
            'capacity': new_salle_obj.capacity,
            'status': new_salle_obj.status
        }  
        
        self.salle.append(new_salle)
        self.save_json("salle.json", self.salle)
        return new_salle
    
    
    def delete_ressource_by_name(self):
        name = input('name ? ')
        type_ressource = input('type ressource ? (livre, equipement, salle) ')
        
        if not type_ressource in ['livre', 'equipement', 'salle']:
            return False
        
        if type_ressource == 'livre':
            data = self.bibliotheque
            filename = "bibliotheque.json"
            has_stock = True

        elif type_ressource == 'equipement':
            data = self.equipement
            filename = "equipement.json"
            has_stock = True

        elif type_ressource == 'salle':
            data = self.salle
            filename = "salle.json"
            has_stock = False

        else:
            return False

        ressource = self.find_by_criteria(data, name=name)
        if not ressource:
            return False

        if has_stock and ressource.get('stock', 1) > 1:
            ressource['stock'] -= 1
        else:
            data.remove(ressource)

        self.save_json(filename, data)
        return True
