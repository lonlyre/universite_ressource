import json
import bcrypt
import tkinter as tk
from tkinter import messagebox



class jsonObject:

    def charger_json(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                contenu = file.read()
                if contenu == "":
                    if filename == "user.json":
                        return [
    {
        "id_user": 1,
        "username": "root",
        "password": "$2b$12$v.MhXuQba13sDSCO3e0N5uRifVH6IDCKgYvIrXn/dz.mfLGGTRb8m",
        "role": "admin",
        "emprunt": {
            "livre": [],
            "equipement": [],
            "salle": []
        }
    }
]
                    return []
                return json.loads(contenu)
        except FileNotFoundError:
                if filename == "user.json":
                    return [    {
        "id_user": 1,
        "username": "root",
        "password": "$2b$12$v.MhXuQba13sDSCO3e0N5uRifVH6IDCKgYvIrXn/dz.mfLGGTRb8m",
        "role": "admin",
        "emprunt": {
            "livre": [],
            "equipement": [],
            "salle": [] 
        }
    }]
                else :
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

        new_user = {
            "id_user": id_user,
            "username": username,
            "password": hashed,
            "role": role,
            "emprunt": {"livre": [], "equipement": [], "salle": []}
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



class universite(jsonObject):

    def __init__(self):
        self.reload()

    def reload(self):
        self.livre = self.charger_json("livre.json")
        self.equipement = self.charger_json("equipement.json")
        self.salle = self.charger_json("salle.json")

    def get_emprunts_user(self, user):
        self.reload()

        emprunts_detail = {"livre": [], "equipement": [], "salle": []}

        for type_ressource in user["emprunt"]:
            data = getattr(self, type_ressource)
            key = f"id_{type_ressource}"

            for id_res in user["emprunt"][type_ressource]:
                res = self.find_by_criteria(data, **{key: id_res})
                if res:
                    emprunts_detail[type_ressource].append(res)

        return emprunts_detail

    def emprunter_ressource(self, user, type_ressource, name):
        self.reload()

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        res = self.find_by_criteria(data, name=name)
        if not res:
            return False

        total = sum(len(user["emprunt"][k]) for k in user["emprunt"])

        if user["role"] == "etudiant":
            if total >= 3 or type_ressource == "salle":
                return False

        if user["role"] == "proff" and total >= 10:
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
        self.reload()

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



class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Gestion Université")
        self.root.geometry("500x500")

        self.users = Users()
        self.univ = universite()
        self.current_user = None

        self.menu_principal()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def menu_principal(self):
        self.clear()

        tk.Label(self.root, text="Bienvenue", font=("Arial", 18)).pack(pady=20)

        tk.Button(self.root, text="Connexion", width=20,
                  command=self.page_connexion).pack(pady=10)

        tk.Button(self.root, text="Inscription", width=20,
                  command=self.page_inscription).pack(pady=10)


    def page_inscription(self):
        self.clear()

        tk.Label(self.root, text="Inscription", font=("Arial", 14)).pack(pady=10)

        username = tk.Entry(self.root)
        username.pack(pady=5)

        password = tk.Entry(self.root, show="*")
        password.pack(pady=5)

        role = tk.StringVar(value="etudiant")
        
        if self.current_user and self.current_user["role"] == "admin":
            tk.OptionMenu(self.root, role, "etudiant", "proff", "admin")
        else:
            tk.OptionMenu(self.root, role, "etudiant", "proff")

        def register():
            if self.users.create_user(username.get(), password.get(), role.get()):
                messagebox.showinfo("Succès", "Inscription réussie")
                if self.current_user and self.current_user["role"] == "admin":
                    self.page_gestion()
                else:
                    self.menu_principal()
            else:
                messagebox.showerror("Erreur", "Utilisateur déjà existant")

        tk.Button(self.root, text="Valider",
                  command=register).pack(pady=10)

        if self.current_user and self.current_user["role"] == "admin":
            tk.Button(self.root, text="Retour",
                      command=self.page_gestion).pack()
        else:
            tk.Button(self.root, text="Retour",
                      command=self.menu_principal).pack()
            
    
    
    
    def page_connexion(self):
        self.clear()

        tk.Label(self.root, text="Connexion", font=("Arial", 14)).pack(pady=10)

        username = tk.Entry(self.root)
        username.pack(pady=5)

        password = tk.Entry(self.root, show="*")
        password.pack(pady=5)

        def login():
            user = self.users.authenticate(username.get(), password.get())
            if user:
                self.current_user = user
                self.page_gestion()
            else:
                messagebox.showerror("Erreur", "Identifiants incorrects")

        tk.Button(self.root, text="Se connecter",
                  command=login).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.menu_principal).pack()


    def page_gestion(self):
        self.clear()

        tk.Label(self.root,
                 text=f"Bienvenue {self.current_user['username']} ({self.current_user['role']})",
                 font=("Arial", 12)).pack(pady=10)

        tk.Button(self.root, text="Voir les ressources", width=25,
                  command=self.page_affichage).pack(pady=5)

        
        tk.Button(self.root, text="Mes emprunts", width=25,
          command=self.page_mes_emprunts).pack(pady=5)


        tk.Button(self.root, text="Emprunter", width=25,
                  command=self.page_emprunt).pack(pady=5)

        tk.Button(self.root, text="Retourner", width=25,
                  command=self.page_retour).pack(pady=5)

        if self.current_user["role"] == "admin":
            tk.Button(self.root, text="Ajouter ressource", width=25,
                      command=self.page_ajout).pack(pady=5)

            tk.Button(self.root, text="Supprimer ressource", width=25,
                      command=self.page_suppression).pack(pady=5)
            
            tk.Button(self.root, text="ajout utilisateur", width=25,
                  command=self.page_inscription).pack(pady=5)


        tk.Button(self.root, text="Déconnexion", width=25,
                  command=self.menu_principal).pack(pady=20)

    def page_mes_emprunts(self):
        self.clear()

        emprunts = self.univ.get_emprunts_user(self.current_user)

        tk.Label(self.root, text="Mes ressources empruntées",
                 font=("Arial", 14)).pack(pady=10)

        listbox = tk.Listbox(self.root, width=60)
        listbox.pack(pady=10)

        vide = True
        for type_res in emprunts:
            for res in emprunts[type_res]:
                listbox.insert(
                    tk.END,
                    f"{type_res} | ID:{res[f'id_{type_res}']} | {res['name']}"
                )


        if vide:
            listbox.insert(tk.END, "Aucune ressource empruntée.")

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack(pady=10)



    def page_affichage(self):
        self.univ.reload()
        self.clear()

        tk.Label(self.root, text="Ressources disponibles",
                 font=("Arial", 14)).pack(pady=10)

        listbox = tk.Listbox(self.root, width=70)
        listbox.pack(pady=10)

        for livre in self.univ.livre:
            listbox.insert(tk.END, f"Livre: {livre['name']} (Stock {livre['stock']})")

        for equip in self.univ.equipement:
            listbox.insert(tk.END, f"Equip: {equip['name']} (Stock {equip['stock']})")

        for salle in self.univ.salle:
            listbox.insert(tk.END, f"Salle: {salle['name']} ({salle['status']})")

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack(pady=10)



    def page_emprunt(self):
        self.clear()

        type_res = tk.StringVar(value="livre")
        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        name = tk.Entry(self.root)
        name.pack(pady=5)

        def valider():
            if self.univ.emprunter_ressource(self.current_user,
                                             type_res.get(),
                                             name.get()):
                messagebox.showinfo("OK", "Emprunt réussi")
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Valider",
                  command=valider).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()



    def page_retour(self):
        self.clear()

        type_res = tk.StringVar(value="livre")
        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        id_res = tk.Entry(self.root)
        id_res.pack(pady=5)

        def valider():
            try:
                if self.univ.retourner_ressource(self.current_user,
                                                 type_res.get(),
                                                 int(id_res.get())):
                    messagebox.showinfo("OK", "Retour réussi")
                else:
                    messagebox.showerror("Erreur", "Impossible")
            except:
                messagebox.showerror("Erreur", "ID invalide")

        tk.Button(self.root, text="Valider",
                  command=valider).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()

    def page_ajout(self):
            self.clear()

            tk.Label(self.root, text="Ajout ressource",
                    font=("Arial", 14)).pack(pady=10)

            type_res = tk.StringVar()
            type_res.set("livre")

            tk.OptionMenu(self.root, type_res,
                        "livre", "equipement", "salle").pack(pady=5)

            name = tk.Entry(self.root)
            name.pack(pady=5)

            capacity = tk.Entry(self.root)
            capacity.pack(pady=5)

            def ajouter():
                cap = None
                if type_res.get() == "salle":
                    try:
                        cap = int(capacity.get())
                    except:
                        messagebox.showerror("Erreur", "Capacité invalide")
                        return

                if self.univ.ajouter_ressource(self.current_user,
                                            type_res.get(),
                                            name.get(),
                                            cap):
                    messagebox.showinfo("OK", "Ajout réussi")
                else:
                    messagebox.showerror("Erreur", "Impossible")

            tk.Button(self.root, text="Valider",
                    command=ajouter).pack(pady=10)

            tk.Button(self.root, text="Retour",
                    command=self.page_gestion).pack()

    
    
    def page_suppression(self):
        self.clear()

        tk.Label(self.root, text="Suppression ressource",
                 font=("Arial", 14)).pack(pady=10)

        type_res = tk.StringVar()
        type_res.set("livre")

        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        name = tk.Entry(self.root)
        name.pack(pady=5)

        def supprimer():
            if self.univ.delete_ressource_by_name(self.current_user,
                                                  type_res.get(),
                                                  name.get()):
                messagebox.showinfo("OK", "Supprimé")
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Valider",
                  command=supprimer).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()




root = tk.Tk()
App(root)
root.mainloop()

