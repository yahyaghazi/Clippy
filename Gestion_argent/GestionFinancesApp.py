import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np
import matplotlib.pyplot as plt
from tkcalendar import Calendar
from GestionnaireFinancier import GestionnaireFinancier
from Revenu import Revenu
from Depense import Depense

class GestionFinancesApp:
    def __init__(self, root):
        self.root = root
        self.gestionnaire = GestionnaireFinancier()
        self.creer_interface()

    def creer_interface(self):
        # Interface utilisateur simplifiée
        self.label_solde = tk.Label(self.root, text="Solde Global : 0.00€", font=("Arial", 12), fg="blue")
        self.label_solde.pack(pady=10)

        self.button_ajouter_depense = tk.Button(self.root, text="Ajouter Dépense", command=self.ajouter_depense)
        self.button_ajouter_depense.pack(pady=5)

        self.button_ajouter_revenu = tk.Button(self.root, text="Ajouter Revenu", command=self.ajouter_revenu)
        self.button_ajouter_revenu.pack(pady=5)

        self.button_afficher_depenses = tk.Button(self.root, text="Afficher Dépenses", command=self.afficher_depenses)
        self.button_afficher_depenses.pack(pady=5)

        self.button_afficher_revenus = tk.Button(self.root, text="Afficher Revenus", command=self.afficher_revenus)
        self.button_afficher_revenus.pack(pady=5)

        self.button_graphique = tk.Button(self.root, text="Graphes", command=self.afficher_graphiques)
        self.button_graphique.pack(pady=5)

        self.mettre_a_jour_solde()

    def mettre_a_jour_solde(self):
        solde = self.gestionnaire.calculer_solde()
        self.label_solde.config(text=f"Solde Global : {solde:.2f}€")

    def ajouter_depense(self):
        # Créer une fenêtre popup
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Ajouter une Dépense")
        fenetre.geometry("300x250")

        # Widgets pour saisir les informations
        tk.Label(fenetre, text="Montant (€)").pack(pady=5)
        entree_montant = tk.Entry(fenetre)
        entree_montant.pack(pady=5)

        tk.Label(fenetre, text="Catégorie").pack(pady=5)
        entree_categorie = tk.Entry(fenetre)
        entree_categorie.pack(pady=5)

        tk.Label(fenetre, text="Date (YYYY-MM-DD)").pack(pady=5)
        
        # Ajouter un calendrier pour choisir la date
        calendrier = Calendar(fenetre, selectmode='day', date_pattern='y-mm-dd')
        calendrier.pack(pady=5)
        
        # Fonction pour valider l'entrée
        def valider():
            try:
                montant = float(entree_montant.get())
                categorie = entree_categorie.get()
                date_str = calendrier.get_date()  # Récupérer la date sélectionnée
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                # Vérifier que les champs ne sont pas vides
                if not categorie.strip():
                    raise ValueError("La catégorie ne peut pas être vide.")
                if montant <= 0:
                    raise ValueError("Le montant doit être supérieur à 0.")

                # Ajouter la dépense
                self.gestionnaire.depenses.append(Depense(montant, categorie, date))
                self.gestionnaire.sauvegarder_depenses()
                self.mettre_a_jour_solde()
                fenetre.destroy()
            except ValueError as e:
                messagebox.showerror("Erreur", f"Erreur : {str(e)}")

        # Bouton pour valider
        bouton_valider = tk.Button(fenetre, text="Ajouter", command=valider)
        bouton_valider.pack(pady=10)

    def ajouter_revenu(self):
        # Créer une fenêtre popup
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Ajouter un Revenu")
        fenetre.geometry("300x250")

        # Widgets pour saisir les informations
        tk.Label(fenetre, text="Montant (€)").pack(pady=5)
        entree_montant = tk.Entry(fenetre)
        entree_montant.pack(pady=5)

        tk.Label(fenetre, text="Source").pack(pady=5)
        entree_source = tk.Entry(fenetre)
        entree_source.pack(pady=5)

        tk.Label(fenetre, text="Date (YYYY-MM-DD)").pack(pady=5)

        # Ajouter un calendrier pour choisir la date
        calendrier = Calendar(fenetre, selectmode='day', date_pattern='y-mm-dd')
        calendrier.pack(pady=5)
        
        # Fonction pour valider l'entrée
        def valider():
            try:
                montant = float(entree_montant.get())
                source = entree_source.get()
                date_str = calendrier.get_date()  # Récupérer la date sélectionnée
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                # Ajouter le revenu
                self.gestionnaire.revenus.append(Revenu(montant, source, date))
                self.gestionnaire.sauvegarder_revenus()
                self.mettre_a_jour_solde()
                fenetre.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides.")

        # Bouton pour valider
        bouton_valider = tk.Button(fenetre, text="Ajouter", command=valider)
        bouton_valider.pack(pady=10)

    def afficher_depenses(self):
        # Créer une nouvelle fenêtre
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Liste des Dépenses")
        fenetre.geometry("600x400")

        # Barre de recherche
        tk.Label(fenetre, text="Rechercher une dépense :").pack(pady=5)
        entree_recherche = tk.Entry(fenetre)
        entree_recherche.pack(pady=5)

        # Tableau
        cadre_tableau = tk.Frame(fenetre)
        cadre_tableau.pack(fill=tk.BOTH, expand=True)

        tableau = tk.Listbox(cadre_tableau, width=80, height=20)
        tableau.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(cadre_tableau)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tableau.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=tableau.yview)

        # Charger les données dans le tableau
        def charger_donnees(filtre=None):
            tableau.delete(0, tk.END)
            for depense in self.gestionnaire.depenses:
                texte = f"{depense.montant}€ | {depense.categorie} | {depense.date}"
                if filtre is None or filtre.lower() in texte.lower():
                    tableau.insert(tk.END, texte)

        charger_donnees()

        # Recherche en temps réel
        def rechercher(event):
            filtre = entree_recherche.get()
            charger_donnees(filtre)

        entree_recherche.bind("<KeyRelease>", rechercher)

    def afficher_revenus(self):
        # Créer une nouvelle fenêtre
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Liste des Revenus")
        fenetre.geometry("600x400")

        # Barre de recherche
        tk.Label(fenetre, text="Rechercher un revenu :").pack(pady=5)
        entree_recherche = tk.Entry(fenetre)
        entree_recherche.pack(pady=5)

        # Tableau
        cadre_tableau = tk.Frame(fenetre)
        cadre_tableau.pack(fill=tk.BOTH, expand=True)

        tableau = tk.Listbox(cadre_tableau, width=80, height=20)
        tableau.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(cadre_tableau)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tableau.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=tableau.yview)

        # Charger les données dans le tableau
        def charger_donnees(filtre=None):
            tableau.delete(0, tk.END)
            for revenu in self.gestionnaire.revenus:
                texte = f"{revenu.montant}€ | {revenu.source} | {revenu.date}"
                if filtre is None or filtre.lower() in texte.lower():
                    tableau.insert(tk.END, texte)

        charger_donnees()

        # Recherche en temps réel
        def rechercher(event):
            filtre = entree_recherche.get()
            charger_donnees(filtre)

        entree_recherche.bind("<KeyRelease>", rechercher)

    def afficher_graphique_depenses(self):
        self.gestionnaire.afficher_graphique_depenses_par_categorie()

    def afficher_graphiques(self):
        fenetre_graphiques = tk.Toplevel(self.root)
        fenetre_graphiques.title("Graphiques Financiers")
        fenetre_graphiques.geometry("800x600")

        # Frame pour disposer les graphiques horizontalement
        cadre_graphique = tk.Frame(fenetre_graphiques)
        cadre_graphique.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Histogramme du solde global avec couleurs personnalisées
        figure_histogramme = self.gestionnaire.creer_histogramme_soldes()
        canvas_histogramme = FigureCanvasTkAgg(figure_histogramme, master=cadre_graphique)
        canvas_histogramme.draw()
        canvas_histogramme.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Camembert des dépenses
        figure_camembert = self.gestionnaire.creer_camembert_depenses()
        canvas_camembert = FigureCanvasTkAgg(figure_camembert, master=cadre_graphique)
        canvas_camembert.draw()
        canvas_camembert.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
