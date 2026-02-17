
# importation des librairies
import json
import bcrypt
import tkinter as tk
from tkinter import messagebox


# classe abstraite json, etendu sur tout systeme des objets
class jsonObject:

    #permet un chargement du json sous forme de tableau
    def charger_json(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                contenu = file.read()
                if contenu == "":
                    return []
                return json.loads(contenu)
        except FileNotFoundError:
            return []

    #save le json dans les fichier donnée
    def save_json(self, filename, data):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    #genere la prochaine ID pour les insertions dans le json
    def next_id(self, tab, key_id):
        if not tab:
            return 1
        return max(item[key_id] for item in tab) + 1

    #permet de ressortir un element des dictionnaires du json en fonction d'autant de critere que l'on veut, si rien trouvé renvoie none
    def find_by_criteria(self, tab, **criteria):
        for item in tab:
            if all(item.get(k) == v for k, v in criteria.items()):
                return item
        return None

# gestion utilisateur (depend de JsonObject)
class Users(jsonObject):

    # recupere le dictionnaire par la methode de la class JsonObject
    def __init__(self):
        self.users = self.charger_json("user.json")

        # si vide on utilise cette base en tant que base avec un admin root, password changeable 
        if not self.users:
            self.users = [
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
            #on crée 2 autre compte test afin de faciliter la tache du test
            self.create_user("stud", "1234", "etudiant", None)
            self.create_user("prod", "1234", "proff", None)
            # on reload le dictionnaire car tout as été inserer dans le fichier json
            self.users = self.charger_json("user.json")



    #methode de creation de user si reussi True, si pas possible False
    def create_user(self, username, password, role, current_user = None):

    # Si on essaie de créer un admin sans etre admin ducoup False
        if role == "admin" and current_user["role"] != "admin":
            return False
    # Si il existe deja jpp crée et ducoup False
        if self.find_by_criteria(self.users, username=username):
            return False
    # Donne la prochaine id et hash le mdp 
        id_user = self.next_id(self.users, "id_user")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    # Crée le user
        new_user = {
            "id_user": id_user,
            "username": username,
            "password": hashed,
            "role": role,
            "emprunt": {"livre": [], "equipement": [], "salle": []}
        }
    # l'ajoute a la base et le save dans le json et ducoup True
        self.users.append(new_user)
        self.save_json("user.json", self.users)

        return True

    #renvoie le user apres avoir verifier si le mdp est good sinon none
    def authenticate(self, username, password):
        # on pecho le user 
        user = self.find_by_criteria(self.users, username=username)
        # si il existe pas bas pas de verif
        if not user:
            return None
        # si le mdp est chiffré est egal a l'autre mdp (merci bcrypt de gerer ca T^T) renvoie true sinon false
        if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return user #et ducoup on renvoie le user en question
        # sinon pas bon password donc None
        return None

    # detruit le user pas son username et renvoie un booléen True si reussi et false sinon
    def delete_user(self, current_user, username_to_delete):

        # sécurité admin
        if not current_user or current_user["role"] != "admin":
            return False

        # on ne peut pas supprimer root
        if username_to_delete == "root":
            return False

        # pecho le user par le nom donnée
        user = self.find_by_criteria(self.users, username=username_to_delete)
        # is existe pas on peut pas supp
        if not user:
            return False
        #retire l'element du dico et save dans le json ducoup True
        self.users.remove(user)
        self.save_json("user.json", self.users)

        return True

    # modifie le mdp du user et son role
    def modify_user(self, current_user, username, new_password=None, new_role=None):
        
        #securité car faut etre admin
        if not current_user or current_user["role"] != "admin":
            return False

        #pecho le user par le username
        user = self.find_by_criteria(self.users, username=username)

        # si existe pas stop
        if not user:
            return False

        # protection root pour que juste change son mdp
        if user["username"] == "root" and current_user["username"] != 'root':
            return False

        # modification mot de passe
        if new_password:
            hashed = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            user["password"] = hashed

        # modification rôle
        if new_role:

            # seul root peut modifier un admin
            if user["role"] == "admin" and current_user["username"] != "root":
                return False
            
            # root ne peut pas changer de role 
            if new_role != current_user["role"] and current_user["username"] == "root" and user["username"] == 'root':
                return False

            user["role"] = new_role
            
        self.save_json("user.json", self.users)

        return True

# gestion des ressources etendu avec JsonObjest 
class universite(jsonObject):

    #on charge les ressources avec la methode de reload
    def __init__(self):
        self.reload()
    
    # permet un refresh
    def reload(self):
        self.livre = self.charger_json("livre.json")
        self.equipement = self.charger_json("equipement.json")
        self.salle = self.charger_json("salle.json")

    # crée un dico de donnée bien ranger
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

        # recherche insensible à la casse
        res = None
        for item in data:
            if name.lower() in item["name"].lower():
                res = item
                break

        if not res:
            return False

        # veification nombre d'emprunt    
        total = sum(len(user["emprunt"][k]) for k in user["emprunt"])

        #contrainte par role 
        if user["role"] == "etudiant" and total >= 3:
            return False

        if user["role"] == "proff" and total >= 10:
            return False

        # gestion si salle pour reserver ou sinon retire un exemplaire
        if type_ressource == "salle":
            if res["status"] != "disponible":
                return False
            res["status"] = "reservee"
        else:
            if res["stock"] <= 0:
                return False
            res["stock"] -= 1

        user["emprunt"][type_ressource].append(res[f"id_{type_ressource}"])

        self.save_json(filename, data) # save 

        users = Users()
        real_user = users.find_by_criteria(users.users, id_user=user["id_user"])
        real_user["emprunt"] = user["emprunt"]
        users.save_json("user.json", users.users)

        return True

    def retourner_ressource(self, user, type_ressource, id_res):
        self.reload()

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
        real_user = users.find_by_criteria(users.users, id_user=user["id_user"])
        real_user["emprunt"] = user["emprunt"]
        users.save_json("user.json", users.users)

        return True


    def ajouter_ressource(self, user, type_ressource, name, capacity=None):

        # sécurité admin
        if user["role"] != "admin":
            return False

        self.reload()

        #verif si l'attribut existe
        if not hasattr(self, type_ressource):
            return False

        # recupere l'attribut dynamiquement, et defini le json a acceder
        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        # si salle ajouter une nouvelle
        if type_ressource == "salle":
            # éviter doublon salle
            for item in data:
                if item["name"].lower() == name.lower():
                    return False

            new_id = self.next_id(data, f"id_{type_ressource}")

            new_item = {
                f"id_{type_ressource}": new_id,
                "name": name,
                "status": "disponible"
            }

            data.append(new_item)
            self.save_json(filename, data)
            return True

        # si object a systeme de stock
        else:
            # vérifier si sa existe
            for item in data:
                if item["name"].lower() == name.lower():
                    # ducoup on ajoute au stock
                    item["stock"] += capacity
                    self.save_json(filename, data)
                    return True

            # sinon nouvelle ressource
            new_id = self.next_id(data, f"id_{type_ressource}")

            new_item = {
                f"id_{type_ressource}": new_id,
                "name": name,
                "stock": capacity
            }

            # enregiste et retourne la reussite
            data.append(new_item)
            self.save_json(filename, data)
            return True



    def delete_ressource_by_name(self, user, type_ressource, name):

        # sécurité admin
        if user["role"] != "admin":
            return False

        self.reload()

        if not hasattr(self, type_ressource):
            return False

        data = getattr(self, type_ressource)
        filename = f"{type_ressource}.json"

        for item in data:
            if item["name"].lower() == name.lower():

                # si une salle supp direct
                if type_ressource == "salle":
                    data.remove(item)

                # si un stock 
                else:
                    # si y en as plus de 1 bas - 1
                    if item["stock"] > 1:
                        item["stock"] -= 1
                    # sinon bas on supp
                    else:
                        data.remove(item)

                self.save_json(filename, data)
                return True

        return False


# class de gestion 
class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Gestion Université")
        self.root.geometry("500x600")

        self.users = Users()
        self.univ = universite()
        self.current_user = None

        self.menu_principal()

    #permet une VIDANGE de l ecran 
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

    def page_connexion(self):
        self.clear()

        tk.Label(self.root, text="Connexion", font=("Arial", 14)).pack(pady=10)

        tk.Label(root, text="Username :").pack()
        username = tk.Entry(self.root,)
        username.pack(pady=5)

        tk.Label(root, text="Password :").pack()
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

    # page de gestion perso
    def page_gestion(self):
        # vidage de l'interface 
        self.clear()
        # si tu es un user tu as cela normalement
        tk.Label(
            self.root,
            text=f"Bienvenue {self.current_user['username']} ({self.current_user['role']})",
            font=("Arial", 12)
        ).pack(pady=10)


        tk.Button(
            self.root,
            text="Voir les ressources",
            width=25,
            command=self.page_affichage
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Mes emprunts",
            width=25,
            command=self.page_mes_emprunts
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Emprunter",
            width=25,
            command=self.page_emprunt
        ).pack(pady=5)

        # si t'es admin tu as acces a ca en plus 
        if self.current_user["role"] == "admin":

            tk.Label(self.root, text="--- Administration ---",
                     font=("Arial", 10, "bold")).pack(pady=5)

            tk.Button(
                self.root,
                text="Ajouter ressource",
                width=25,
                command=self.page_ajout
            ).pack(pady=5)

            tk.Button(
                self.root,
                text="Supprimer ressource",
                width=25,
                command=self.page_suppression
            ).pack(pady=5)

            tk.Button(
                self.root,
                text="Liste des utilisateurs",
                width=25,
                command=self.page_liste_users
            ).pack(pady=5)

            
            tk.Button(
                self.root,
                text="Créer utilisateur",
                width=25,
                command=self.page_inscription
            ).pack(pady=5)

            tk.Button(
                self.root,
                text="Modifier utilisateur",
                width=25,
                command=self.page_modifier_user
            ).pack(pady=5)

            tk.Button(
                self.root,
                text="Supprimer utilisateur",
                width=25,
                command=self.page_supprimer_user
            ).pack(pady=5)




        def logout():
            self.current_user = None
            self.menu_principal()

        tk.Button(
            self.root,
            text="Déconnexion",
            width=25,
            command=logout
        ).pack(pady=20)


    def page_mes_emprunts(self):
        self.clear()

        emprunts = self.univ.get_emprunts_user(self.current_user)

        tk.Label(self.root, text="Mes ressources empruntées",
                 font=("Arial", 14)).pack(pady=10)

        listbox = tk.Listbox(self.root, width=70)
        listbox.pack(pady=10)

        has_item = False

        for type_res in emprunts:
            for res in emprunts[type_res]:
                listbox.insert(
                    tk.END,
                    f"{type_res}|{res[f'id_{type_res}']}|{res['name']}"
                )
                has_item = True

        if not has_item:
            listbox.insert(tk.END, "Aucune ressource empruntée.")

        def retourner_selection():
            selection = listbox.get(tk.ACTIVE)
            if not selection or "Aucune" in selection:
                return

            type_res, id_res, _ = selection.split("|")
            id_res = int(id_res)

            if self.univ.retourner_ressource(
                self.current_user, type_res, id_res
            ):
                messagebox.showinfo("OK", "Retour réussi")
                self.page_mes_emprunts()
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Retourner sélection",
                  command=retourner_selection).pack(pady=5)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack(pady=10)

    def page_emprunt(self):
        self.clear()

        type_res = tk.StringVar(value="livre")
        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)
        tk.Label(root, text="Nom Ressource :").pack()
        name = tk.Entry(self.root)
        name.pack(pady=5)

        def valider():
            if self.univ.emprunter_ressource(
                self.current_user,
                type_res.get(),
                name.get()
            ):
                messagebox.showinfo("OK", "Emprunt réussi")
                self.page_gestion()
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Valider",
                  command=valider).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()

    def page_inscription(self):
        self.clear()

        tk.Label(self.root, text="Inscription",
                 font=("Arial", 14)).pack(pady=10)

        tk.Label(root, text="Username :").pack()
        username = tk.Entry(self.root)
        username.pack(pady=5)

        tk.Label(root, text="Password :").pack()
        password = tk.Entry(self.root, show="*")
        password.pack(pady=5)

        role = tk.StringVar(value="etudiant")

        if self.current_user and self.current_user["username"] == "root":
            menu = tk.OptionMenu(self.root, role,
                                 "etudiant", "proff", "admin")
        else:
            menu = tk.OptionMenu(self.root, role,
                                 "etudiant", "proff")

        menu.pack(pady=5)

        def register():
            if role.get() == "admin" and (
                not self.current_user or
                self.current_user["username"] != "root"
            ):
                messagebox.showerror("Erreur",
                                     "Seul root peut créer un admin")
                return

            if self.users.create_user(username.get(),
                                      password.get(),
                                      role.get(), self.current_user ):
                messagebox.showinfo("Succès",
                                    "Compte créé")
                if self.current_user:
                    self.page_gestion()
                else:
                    self.menu_principal()
            else:
                messagebox.showerror("Erreur",
                                     "Utilisateur déjà existant")

        tk.Button(self.root, text="Valider",
                  command=register).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion if self.current_user
                  else self.menu_principal).pack()


    def page_affichage(self):
        self.univ.reload()
        self.clear()

        tk.Label(self.root, text="Ressources disponibles",
                 font=("Arial", 14)).pack(pady=10)

        listbox = tk.Listbox(self.root, width=70)
        listbox.pack(pady=10)

        for livre in self.univ.livre:
            listbox.insert(
                tk.END,
                f"Livre | ID:{livre['id_livre']} | {livre['name']} (Stock {livre['stock']})"
            )

        for equip in self.univ.equipement:
            listbox.insert(
                tk.END,
                f"Equipement | ID:{equip['id_equipement']} | {equip['name']} (Stock {equip['stock']})"
            )

        for salle in self.univ.salle:
            listbox.insert(
                tk.END,
                f"Salle | ID:{salle['id_salle']} | {salle['name']} ({salle['status']})"
            )

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack(pady=10)


    def page_ajout(self):
        self.clear()

        tk.Label(self.root, text="Ajout ressource",
                 font=("Arial", 14)).pack(pady=10)

        type_res = tk.StringVar(value="livre")
        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        tk.Label(root, text="Nom Ressource :").pack()
        name = tk.Entry(self.root)
        name.pack(pady=5)

        tk.Label(root, text="Stock a ajouter :").pack()
        capacity = tk.Entry(self.root)
        capacity.pack(pady=5)

        def ajouter():
            cap = None
            if type_res.get() != "salle":
                try:
                    cap = int(capacity.get())
                except:
                    messagebox.showerror("Erreur",
                                         "Capacité invalide")
                    return

            if self.univ.ajouter_ressource(
                self.current_user,
                type_res.get(),
                name.get(),
                cap
            ):
                messagebox.showinfo("OK",
                                    "Ajout réussi")
                self.page_gestion()
            else:
                messagebox.showerror("Erreur",
                                     "Impossible")

        tk.Button(self.root, text="Valider",
                  command=ajouter).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()


    def page_suppression(self):
        self.clear()

        tk.Label(self.root, text="Suppression ressource",
                 font=("Arial", 14)).pack(pady=10)

        type_res = tk.StringVar(value="livre")
        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        tk.Label(root, text="Nom Ressource :").pack()
        name = tk.Entry(self.root)
        name.pack(pady=5)

        def supprimer():
            if self.univ.delete_ressource_by_name(
                self.current_user,
                type_res.get(),
                name.get()
            ):
                messagebox.showinfo("OK",
                                    "Supprimé")
                self.page_gestion()
            else:
                messagebox.showerror("Erreur",
                                     "Impossible")

        tk.Button(self.root, text="Valider",
                  command=supprimer).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()

    def page_supprimer_user(self):
        self.clear()

        tk.Label(self.root, text="Supprimer utilisateur",
                 font=("Arial", 14)).pack(pady=10)

        tk.Label(root, text="Username :").pack()
        username = tk.Entry(self.root)
        username.pack(pady=5)

        def supprimer():
            if self.users.delete_user(
                    self.current_user,
                    username.get()):
                messagebox.showinfo("OK", "Utilisateur supprimé")
                self.page_gestion()
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Valider",
                  command=supprimer).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()


    def page_modifier_user(self):
        self.clear()

        tk.Label(self.root, text="Modifier utilisateur",
                 font=("Arial", 14)).pack(pady=10)

        tk.Label(root, text="Username :").pack()
        username = tk.Entry(self.root)
        username.pack(pady=5)

        tk.Label(root, text="Nouveau Mdp :").pack()
        new_password = tk.Entry(self.root, show="*")
        new_password.pack(pady=5)

        new_role = tk.StringVar(value="etudiant")

        tk.OptionMenu(self.root, new_role,
                      "etudiant", "proff", "admin").pack(pady=5)

        def modifier():
            password_value = new_password.get()
            role_value = new_role.get()

            if password_value == "":
                password_value = None

            if self.users.modify_user(
                    self.current_user,
                    username.get(),
                    password_value,
                    role_value):
                messagebox.showinfo("OK", "Modification réussie")
                self.page_gestion()
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Valider",
                  command=modifier).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()

    def page_liste_users(self):
        self.clear()

        # sécurité interface
        if not self.current_user or self.current_user["role"] != "admin":
            messagebox.showerror("Erreur", "Accès refusé")
            self.page_gestion()
            return

        tk.Label(self.root,
                 text="Liste des utilisateurs",
                 font=("Arial", 14)).pack(pady=10)

        listbox = tk.Listbox(self.root, width=60)
        listbox.pack(pady=10)

        # recharge les users
        self.users = Users()

        for user in self.users.users:
            listbox.insert(
                tk.END,
                f"ID:{user['id_user']} | {user['username']} | Rôle: {user['role']}"
            )

        tk.Button(self.root,
                  text="Retour",
                  command=self.page_gestion).pack(pady=10)


root = tk.Tk()
App(root)
root.mainloop()
