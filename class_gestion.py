# import des librairies necessaires
import json
import os
import bcrypt


# gestion des objets Json et ajout id et recherhe par critere

class jsonObject:

    # charge le contenue du json sous forme de tableau de données et gere les cas de fichier vide ou inexistant
    def charger_json(self, filename):
        if not os.path.exists(filename):
            return []
        with open(filename, "r", encoding="utf-8") as file:
            contenu = file.read().strip()
            if contenu == "":
                return []
            return json.loads(contenu)
        
    # methode pour sauvegarder les données dans un fichier json
    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    # methode pour generer un id unique pour une nouvelle entrée dans un tableau de données
    def next_id(self, tab, key_id):
        if tab == []:
            return 1
        return tab[-1][key_id] + 1

    # methode pour trouver un item dans un tableau de données selon des critères de recherche passés en argument
    def find_by_criteria(self, tab, **criteria):
        for item in tab:
            if all(item.get(key) == value for key, value in criteria.items()):
                return item
        return None


# classe pour la gestion des users, avec ajout, suppression et modification par username et password

class Users(jsonObject):

    # constructeur qui charge les users depuis le fichier json
    def __init__(self):
        self.users = self.charger_json("user.json")

    # methode pour ajouter un user, demande les informations nécessaires et les stock dans le fichier json
    def ajouter_user(self):
        id_user = self.next_id(self.users, 'id_user')
        username = str(input('nom utilisateur ? '))
        password = str(input('Password ? '))
        emprunt = {'livre': [], 'equipement': [], 'salle': []}
        role = str(input('role ? (proff, etudiant) '))
        new_user = {
            'id_user': id_user,
            'username': username,
            'password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'emprunt': emprunt,
            'role': role
        }
        self.users.append(new_user)
        self.save_json("user.json", self.users)
        return new_user

    # methode pour supprimer un user, demande le username et password pour trouver le user et le supprimer du fichier json
    def supp_user_by_username_and_password(self):
        username = input('username ? ')
        password = input('password ? ')
        user = self.find_by_criteria(self.users, username=username)

        if not user:
            return False

        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            return False


        if not user:
            return False

        self.users.remove(user)
        self.save_json("user.json", self.users)
        return True

    # methode pour modifier un user, demande le username et password pour trouver le user et modifier ses informations dans le fichier json
    def modfify_user_with_username_and_password(self):
        username = input('username ? ')
        password = input('password ? ')

        user = self.find_by_criteria(self.users, username=username)

        if not user:
            return False

        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            return False

        if not user:
            return False

        user['username'] = input('new username ? ')
        new_password = input('new password ? ')
        user['password'] = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        self.save_json("user.json", self.users)
        return True


# classe en bas de l'echelle permet de crée les objets

class ressource(jsonObject):

    def __init__(self, file: str):
        data = self.charger_json(file)
        self.id = self.next_id(data, 'id')
        self.name = str(input('nom ? '))

# fille de ressource pour crée un equipement
class equipement(ressource):
    def __init__(self):
        super().__init__("equipement.json") #super() permet d'appeler le constructeur de la classe parente ressource pour initialiser l'id et le name
        existing = self.find_by_criteria(
            self.charger_json("equipement.json"),
            name=self.name
        )
        if existing:
            self.stock = existing.get('stock', 1) + 1
        else:
            self.stock = 1

# fille de ressource pour crée un livre

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

# fille de ressource pour crée une salle
class salle(ressource):
    def __init__(self):
        super().__init__("salle.json") 
        self.capacity = int(input('capacity ? '))
        self.status = 'disponible'


# experimental class pour les objects de la bibliotheque, equipement et salle

class universite(jsonObject):

    # charge les données de l'universite
    def __init__(self):
        self.bibliotheque = self.charger_json("bibliotheque.json")
        self.equipement = self.charger_json("equipement.json")
        self.salle = self.charger_json("salle.json")

    def afficher_ressources(self):
        print("Livres :")
        for livre in self.bibliotheque:
            print(f"ID: {livre['id_livre']}, Name: {livre['name']}, Stock: {livre['stock']}, Status: {livre['status']}")

        print("\nEquipements :")
        for equip in self.equipement:
            print(f"ID: {equip['id_equipement']}, Name: {equip['name']}, Stock: {equip['stock']}, Status: {equip['status']}")

        print("\nSalles :")
        for salle in self.salle:
            print(f"ID: {salle['id_salle']}, Name: {salle['name']}, Capacity: {salle['capacity']}, Status: {salle['status']}")

    # TODO : factoriser les méthodes d'ajout de ressource pour éviter la redondance de code, en utilisant une méthode générique qui prend en argument le type de ressource et les données nécessaires pour la création de la ressource
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
         # verif admin ici vvvvv
        user= Users()
        username = input('username ? ')
        password = input('password ? ')
        user = user.find_by_criteria(
            user.users,
            username=username
        )
        if not user:
            return False
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            return False
        if user['role'] != 'admin':
            return False
        # verif admin ici ^^^^^
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
    
    # TODO : ajouter une fonction de modification de capacité de salle ?
    def ajouter_salle(self):
         # verif admin ici vvvvv
        user= Users()
        username = input('username ? ')
        password = input('password ? ')
        user = user.find_by_criteria(
            user.users,
            username=username
        )
        if not user:
            return False
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            return False
        if user['role'] != 'admin':
            return False
        # verif admin ici ^^^^^
        
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
        # verif admin ici vvvvv
        user= Users()
        username = input('username ? ')
        password = input('password ? ')
        user = user.find_by_criteria(
            user.users,
            username=username
        )
        if not user:
            return False
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            return False
        if user['role'] != 'admin':
            return False
        # verif admin ici ^^^^^
        
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


    # methode emprunt ressource : demande le user, son password, la ressource et gere l'emprunt
    # renvoie false si le user n'existe pas, si la ressource n'existe pas, ou si les contraintes d'emprunt ne sont pas respectees 
    # sinon, stoke l'emprunt dans le user et met a jour le stock ou le status de la ressource
    # renvoie true si l'emprunt est reussi
    
    def emprunter_ressource(self):
        # demande des informations pour l'emprunt
        username = input('username ? ')
        password = input('password ? ')
        type_ressource = input('type ressource ? (livre, equipement, salle) ')
        name = input('nom de la ressource ? ')

        # accede au users et pecho celui qui est demander
        users = Users()
        user = users.find_by_criteria(
            users.users,
            username=username,
            password=password
        )

        if not user:
            return False

        role = user['role']

        # total des emprunts 
        total_emprunts = (
            len(user['emprunt']['livre']) +
            len(user['emprunt']['equipement']) +
            len(user['emprunt']['salle'])
        )
        
        # contraintes d'emprunt selon le role de l'utilisateur
        if role == 'etudiant':
            if total_emprunts >= 3:
                return False
            if type_ressource == 'salle':
                return False

        if role == 'proff':
            if total_emprunts >= 10:
                return False
          
        # pour appeler le bon fichier et tableau de ressource
        if type_ressource == 'livre':
            data = self.bibliotheque
            filename = "bibliotheque.json"

        elif type_ressource == 'equipement':
            data = self.equipement
            filename = "equipement.json"

        elif type_ressource == 'salle':
            data = self.salle
            filename = "salle.json"

        else:
            return False
        
        # pecho la ressource et si elle existe pas pouff return false
        ressource = self.find_by_criteria(data, name=name)
        if not ressource:
            return False

        # faire les stock et satus
        if type_ressource != 'salle':
            if ressource.get('stock', 0) < 1:
                return False
            ressource['stock'] -= 1
        else:
            if ressource['status'] != 'disponible':
                return False
            ressource['status'] = 'reservee'

        # stoker l'emprunt dans le user
        user['emprunt'][type_ressource].append(ressource)

        self.save_json(filename, data)
        users.save_json("user.json", users.users)
        return True

    def retourner_ressource(self):
        # demande des informations pour le retour
        username = input('username ? ')
        password = input('password ? ')
        type_ressource = input('type ressource ? (livre, equipement, salle) ')
        name = input('nom de la ressource ? ')

        # accede au users et pecho celui qui est demander
        users = Users()
        user = users.find_by_criteria(
            users.users,
            username=username,
            password=password
        )

        if not user:
            return False

        # pour appeler le bon fichier et tableau de ressource
        if type_ressource == 'livre':
            data = self.bibliotheque
            filename = "bibliotheque.json"

        elif type_ressource == 'equipement':
            data = self.equipement
            filename = "equipement.json"

        elif type_ressource == 'salle':
            data = self.salle
            filename = "salle.json"

        else:
            return False
        
        # pecho la ressource et si elle existe pas pouff return false
        # si elle existe dans emprunt du user mais pas dans le tableau de ressource, c'est que le user a emprunter la ressource mais elle a été supprimé du tableau de ressource, dans ce cas on ajoute la ressource au tableau de ressource avec un stock de 1 ou un status disponible selon le type de ressource, et on continue le processus de retour normalement
        ressource = self.find_by_criteria(data, name=name)
        if not ressource:
            if name  in user['emprunt'][type_ressource]:
                if type_ressource == 'salle':
                    self.salle.append({
                        'id_salle': user['emprunt'][type_ressource]['id_salle'],
                        'name': user['emprunt'][type_ressource]['name'],
                        'capacity': user['emprunt'][type_ressource]['capacity'],
                        'status': 'disponible'
                    })
                if type_ressource == 'equipement':
                    self.equipement.append({
                        'id_equipement': user['emprunt'][type_ressource]['id_equipement'],
                        'name': user['emprunt'][type_ressource]['name'],
                        'stock': 1
                    })
                if type_ressource == 'livre':
                    self.bibliotheque.append({
                        'id_livre': user['emprunt'][type_ressource]['id_livre'],
                        'name': user['emprunt'][type_ressource]['name'],
                        'stock': 1
                    })
            return False

        # faire les stock et satus
        if type_ressource != 'salle':
            ressource['stock'] += 1
        else:
            ressource['status'] = 'disponible'

        # retirer l'emprunt du user
        user['emprunt'][type_ressource].remove(ressource)

        self.save_json(filename, data)
        users.save_json("user.json", users.users)
        return True
    
    
# TODO : interface graphique pour que elle puisse tourner et que cela soit graphique avec tkinter
# TODO : historiques des imprunts

