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

    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def next_id(self, tab, key_id):
        if not tab:
            return 1
        return max(item[key_id] for item in tab) + 1

    def find_by_criteria(self, tab, **criteria):
        for item in tab:
            if all(item.get(k) == v for k, v in criteria.items()):
                return item
        return None



class Users(jsonObject):

    def __init__(self):
        self.users = self.charger_json("user.json")


    def create_user(self, username, password, role):

        if self.find_by_criteria(self.users, username=username):
            return False

        id_user = self.next_id(self.users, "id_user")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        emprunt = {
            "livre": [],
            "equipement": [],
            "salle": []
        }

        new_user = {
            "id_user": id_user,
            "username": username,
            "password": hashed,
            "role": role,
            "emprunt": emprunt
        }

        self.users.append(new_user)
        self.save_json("user.json", self.users)
        return True


    def authenticate(self, username, password):

        user = self.find_by_criteria(self.users, username=username)

        if not user:
            return None

        if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return user

        return None





    def get_emprunts_user(self, user):

        emprunts_detail = {
            "livre": [],
            "equipement": [],
            "salle": []
        }

        for type_ressource in user["emprunt"]:

            data = getattr(self, type_ressource)
            key = f"id_{type_ressource}"

            for id_res in user["emprunt"][type_ressource]:
                res = self.find_by_criteria(data, **{key: id_res})
                if res:
                    emprunts_detail[type_ressource].append(res)

        return emprunts_detail


class universite(jsonObject):

    def __init__(self):
        self.livre = self.charger_json("livre.json")
        self.equipement = self.charger_json("equipement.json")
        self.salle = self.charger_json("salle.json")


    def ajouter_ressource(self, user, type_ressource, name, capacity=None):

        if user["role"] != "admin":
            return False

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        existing = self.find_by_criteria(data, name=name)


        if type_ressource == "salle":

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



    def delete_ressource_by_name(self, user, type_ressource, name):

        if user["role"] != "admin":
            return False

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


   
    def emprunter_ressource(self, user, type_ressource, name):

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        res = self.find_by_criteria(data, name=name)

        if not res:
            return False

        total_emprunts = sum(len(user["emprunt"][k]) for k in user["emprunt"])

        if user["role"] == "etudiant":
            if total_emprunts >= 3:
                return False
            if type_ressource == "salle":
                return False

        if user["role"] == "proff":
            if total_emprunts >= 10:
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

        self.save_json(filename, data)

        users = Users()
        users.users = users.charger_json("user.json")
        real_user = users.find_by_criteria(users.users, id_user=user["id_user"])
        real_user["emprunt"] = user["emprunt"]
        users.save_json("user.json", users.users)

        return True


 
    def retourner_ressource(self, user, type_ressource, id_res):

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"
        key = f"id_{type_ressource}"

        res = self.find_by_criteria(data, **{key: id_res})

        if not res:
            return False

        if id_res not in user["emprunt"][type_ressource]:
            return False

        if type_ressource == "salle":
            res["status"] = "disponible"
        else:
            res["stock"] += 1

        user["emprunt"][type_ressource].remove(id_res)

        self.save_json(filename, data)

        
        users = Users()
        users.users = users.charger_json("user.json")
        real_user = users.find_by_criteria(users.users, id_user=user["id_user"])
        real_user["emprunt"] = user["emprunt"]
        users.save_json("user.json", users.users)

        return True
