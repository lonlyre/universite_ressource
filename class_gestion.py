import json
import bcrypt


class jsonObject:

    def charger_json(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                contenu = file.read()
                if contenu == "":
                    return []
                return json.loads(contenu)
        except FileNotFoundError:
            return []

    # methode pour sauvegarder les données dans un fichier json
    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def next_id(self, tab, key_id):
        if not tab:
            return 1
        return max(item[key_id] for item in tab) + 1

    # methode pour trouver un item dans un tableau de données selon des critères de recherche passés en argument
    def find_by_criteria(self, tab, **criteria):
        for item in tab:
            if all(item.get(k) == v for k, v in criteria.items()):
                return item
        return None


#  USERS 

class Users(jsonObject):

    def __init__(self):
        self.users = self.charger_json("user.json")

    def create_user(self):
        id_user = self.next_id(self.users, "id_user")
        username = input("username ? ")
        password = input("password ? ").encode("utf-8")

        hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

        role = input("role ? (proff, etudiant, admin) ")

        emprunt = {'livre': [], 'equipement': [], 'salle': []}

        new_user = {
            "id_user": id_user,
            "username": username,
            "password": hashed,
            "role": role,
            "emprunt": emprunt
        }

        self.users.append(new_user)
        self.save_json("user.json", self.users)

    def authenticate(self):
        username = input("username ? ")
        password = input("password ? ").encode("utf-8")

        user = self.find_by_criteria(self.users, username=username)

        if not user:
            return None

        if bcrypt.checkpw(password, user["password"].encode("utf-8")):
            return user

        return None


# UNIVERSITE 

class universite(jsonObject):

    def __init__(self):
        self.bibliotheque = self.charger_json("bibliotheque.json")
        self.equipement = self.charger_json("equipement.json")
        self.salle = self.charger_json("salle.json")

    def afficher_ressources(self):
        print("Livres :")
        for livre in self.bibliotheque:
            print(livre)

        print("\nEquipements :")
        for equip in self.equipement:
            print(equip)

        print("\nSalles :")
        for salle in self.salle:
            print(salle)

    # TODO : factoriser les méthodes d'ajout de ressource pour éviter la redondance de code, en utilisant une méthode générique qui prend en argument le type de ressource et les données nécessaires pour la création de la ressource
    def ajouter_ressource(self, type_ressource):

        # verif admin ici vvvvv
        users = Users()
        user = users.authenticate()

        if not user or user["role"] != "admin":
            print("Accès refusé")
            return False
        # verif admin ici ^^^^^

        name = input("Nom ? ")

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        existing = self.find_by_criteria(data, name=name)

        # TODO : ajouter une fonction de modification de capacité de salle ?
        if type_ressource == "salle":
            capacity = int(input("Capacité ? "))

            if existing:
                return False

            new = {
                f"id_{type_ressource}": self.next_id(data, f"id_{type_ressource}"),
                "name": name,
                "capacity": capacity,
                "status": "disponible"
            }

        else:
            if existing:
                existing["stock"] += 1
                self.save_json(filename, data)
                return True

            new = {
                f"id_{type_ressource}": self.next_id(data, f"id_{type_ressource}"),
                "name": name,
                "stock": 1
            }

        data.append(new)
        self.save_json(filename, data)
        return True


    def delete_ressource_by_name(self):

        # verif admin ici vvvvv
        users = Users()
        user = users.authenticate()

        if not user or user["role"] != "admin":
            return False
        # verif admin ici ^^^^^

        name = input("name ? ")
        type_ressource = input("type ressource ? (livre, equipement, salle) ")

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        ressource = self.find_by_criteria(data, name=name)
        if not ressource:
            return False

        if type_ressource != "salle" and ressource.get("stock", 1) > 1:
            ressource["stock"] -= 1
        else:
            data.remove(ressource)

        self.save_json(filename, data)
        return True


    # methode emprunt ressource : demande le user, son password, la ressource et gere l'emprunt
    # renvoie false si le user n'existe pas, si la ressource n'existe pas, ou si les contraintes d'emprunt ne sont pas respectees 
    # sinon, stoke l'emprunt dans le user et met a jour le stock ou le status de la ressource
    # renvoie true si l'emprunt est reussi
    def emprunter_ressource(self):

        users = Users()
        user = users.authenticate()

        if not user:
            return False

        type_ressource = input("type ressource ? (livre, equipement, salle) ")
        name = input("nom de la ressource ? ")

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        res = self.find_by_criteria(data, name=name)

        if not res:
            return False

        total_emprunts = sum(len(user["emprunt"][k]) for k in user["emprunt"])

        if user["role"] == "etudiant":
            if total_emprunts >= 3 or type_ressource == "salle":
                return False

        if user["role"] == "proff" and total_emprunts >= 10:
            return False

        if type_ressource == "salle":
            if res["status"] != "disponible":
                return False
            res["status"] = "reservee"
        else:
            if res["stock"] <= 0:
                return False
            res["stock"] -= 1

        user["emprunt"][type_ressource].append(res[f"id_{type_ressource}"])

        self.save_json(f"{type_ressource}.json", data)
        users.save_json("user.json", users.users)

        return True


    def retourner_ressource(self):

        username = input("username ? ")
        password = input("password ? ")
        type_ressource = input("type ressource ? (livre, equipement, salle) ")
        id_res = int(input("ID ? "))

        users = Users()
        user = users.authenticate()

        if not user:
            return False

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        key = f"id_{type_ressource}"

        res = self.find_by_criteria(data, **{key: id_res})

        if id_res not in user["emprunt"][type_ressource]:
            return False

        if type_ressource == "salle":
            res["status"] = "disponible"
        else:
            res["stock"] += 1

        user["emprunt"][type_ressource].remove(id_res)

        self.save_json(f"{type_ressource}.json", data)
        users.save_json("user.json", users.users)

        return True


# TODO : creer systeme de rendu 
# TODO : interface graphique pour que elle puisse tourner et que cela soit graphique avec tkinter
# TODO : historiques des imprunts
