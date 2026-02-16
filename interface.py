import tkinter as tk
from tkinter import messagebox
from class_gestion import Users, universite


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Gestion Université")
        self.root.geometry("500x500")

        self.users = Users()
        self.univ = universite()
        self.current_user = None

        self.menu_principal()

    
    # ==========================
    # MES EMPRUNTS
    # ==========================
    def page_mes_emprunts(self):
        self.univ = universite()  # recharge les données
        self.clear()

        tk.Label(self.root, text="Mes ressources empruntées",
                font=("Arial", 14)).pack(pady=10)

        emprunts = self.univ.get_emprunts_user(self.current_user)

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=70)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=listbox.yview)

        vide = True

        # LIVRES
        listbox.insert(tk.END, "----- LIVRES -----")
        for livre in emprunts["livre"]:
            listbox.insert(tk.END,
                        f"{livre['id_livre']} - {livre['name']}")
            vide = False

        listbox.insert(tk.END, "")

        # EQUIPEMENTS
        listbox.insert(tk.END, "----- EQUIPEMENTS -----")
        for equip in emprunts["equipement"]:
            listbox.insert(tk.END,
                        f"{equip['id_equipement']} - {equip['name']}")
            vide = False

        listbox.insert(tk.END, "")

        # SALLES
        listbox.insert(tk.END, "----- SALLES -----")
        for salle in emprunts["salle"]:
            listbox.insert(tk.END,
                        f"{salle['id_salle']} - {salle['name']}")
            vide = False

        if vide:
            listbox.insert(tk.END, "Aucune ressource empruntée.")

        tk.Button(self.root, text="Retour",
                command=self.page_gestion).pack(pady=10)

    # ==========================
    # MENU PRINCIPAL
    # ==========================
    def menu_principal(self):
        self.clear()

        tk.Label(self.root, text="Bienvenue", font=("Arial", 18)).pack(pady=20)

        tk.Button(self.root, text="Connexion", width=20, command=self.page_connexion).pack(pady=10)
        tk.Button(self.root, text="Inscription", width=20, command=self.page_inscription).pack(pady=10)

    # ==========================
    # INSCRIPTION
    # ==========================
    def page_inscription(self):
        self.clear()

        tk.Label(self.root, text="Inscription", font=("Arial", 14)).pack(pady=10)

        username = tk.Entry(self.root)
        username.pack(pady=5)

        password = tk.Entry(self.root, show="*")
        password.pack(pady=5)

        role = tk.StringVar()
        role.set("etudiant")

        tk.OptionMenu(self.root, role, "etudiant", "proff", "admin").pack(pady=5)

        def register():
            if self.users.create_user(username.get(), password.get(), role.get()):
                messagebox.showinfo("Succès", "Inscription réussie")
                self.page_connexion()
            else:
                messagebox.showerror("Erreur", "Utilisateur déjà existant")

        tk.Button(self.root, text="Valider", command=register).pack(pady=10)
        tk.Button(self.root, text="Retour", command=self.menu_principal).pack()


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

        tk.Button(self.root, text="Se connecter", command=login).pack(pady=10)
        tk.Button(self.root, text="Retour", command=self.menu_principal).pack()

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

        tk.Button(self.root, text="Déconnexion", width=25,
                  command=self.menu_principal).pack(pady=20)


    def page_affichage(self):
        self.univ = universite()  
        self.clear()

        tk.Label(self.root, text="Ressources disponibles",
                 font=("Arial", 14)).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=70)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=listbox.yview)

        listbox.insert(tk.END, "----- LIVRES -----")
        for livre in self.univ.livre:
            listbox.insert(tk.END,
                           f"{livre['id_livre']} - {livre['name']} (Stock: {livre.get('stock', 0)})")
        listbox.insert(tk.END, "")

    
        listbox.insert(tk.END, "----- EQUIPEMENTS -----")
        for equip in self.univ.equipement:
            listbox.insert(tk.END,
                           f"{equip['id_equipement']} - {equip['name']} (Stock: {equip.get('stock', 0)})")
        listbox.insert(tk.END, "")

        listbox.insert(tk.END, "----- SALLES -----")
        for salle in self.univ.salle:
            listbox.insert(tk.END,
                           f"{salle['id_salle']} - {salle['name']} "
                           f"(Capacité: {salle.get('capacity', 0)}) "
                           f"[{salle.get('status')}]")

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack(pady=10)

    
    def page_emprunt(self):
        self.clear()

        tk.Label(self.root, text="Emprunt", font=("Arial", 14)).pack(pady=10)

        type_res = tk.StringVar()
        type_res.set("livre")

        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        name = tk.Entry(self.root)
        name.pack(pady=5)

        def emprunter():
            if self.univ.emprunter_ressource(self.current_user,
                                             type_res.get(),
                                             name.get()):
                messagebox.showinfo("OK", "Emprunt réussi")
            else:
                messagebox.showerror("Erreur", "Impossible")

        tk.Button(self.root, text="Valider",
                  command=emprunter).pack(pady=10)

        tk.Button(self.root, text="Retour",
                  command=self.page_gestion).pack()

 
    def page_retour(self):
        self.clear()

        tk.Label(self.root, text="Retour", font=("Arial", 14)).pack(pady=10)

        type_res = tk.StringVar()
        type_res.set("livre")

        tk.OptionMenu(self.root, type_res,
                      "livre", "equipement", "salle").pack(pady=5)

        id_res = tk.Entry(self.root)
        id_res.pack(pady=5)

        def retourner():
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
                  command=retourner).pack(pady=10)

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

   
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()



root = tk.Tk()
App(root)
root.mainloop()
