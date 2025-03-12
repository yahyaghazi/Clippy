from Revenu import Revenu
from Depense import Depense
import csv
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from collections import defaultdict

class GestionnaireFinancier:
    def __init__(self, fichier_depenses="Depenses.csv", fichier_revenus="Revenus.csv"):
        self.fichier_depenses = fichier_depenses
        self.fichier_revenus = fichier_revenus
        self.depenses = []
        self.revenus = []
        self.charger_donnees()

    def charger_donnees(self):
        self.charger_depenses()
        self.charger_revenus()

    def charger_depenses(self):
        try:
            with open(self.fichier_depenses, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.depenses = [
                    Depense(
                        montant=float(row["montant"]),
                        categorie=row["categorie"],
                        date=datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
                    ) for row in reader
                ]
        except FileNotFoundError:
            pass

    def charger_revenus(self):
        try:
            with open(self.fichier_revenus, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.revenus = [
                    Revenu(
                        montant=float(row["montant"]),
                        source=row["source"],
                        date=datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
                    ) for row in reader
                ]
        except FileNotFoundError:
            pass

    def sauvegarder_depenses(self):
        with open(self.fichier_depenses, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["montant", "categorie", "date"])
            writer.writeheader()
            for depense in self.depenses:
                writer.writerow(depense.to_dict())

    def sauvegarder_revenus(self):
        with open(self.fichier_revenus, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["montant", "source", "date"])
            writer.writeheader()
            for revenu in self.revenus:
                writer.writerow(revenu.to_dict())

    def calculer_solde(self):
        total_revenus = sum(revenu.montant for revenu in self.revenus)
        total_depenses = sum(depense.montant for depense in self.depenses)
        return total_revenus - total_depenses

    def total_depenses_par_categorie(self):
            totaux = {}
            for depense in self.depenses:
                if depense.categorie in totaux:
                    totaux[depense.categorie] += depense.montant
                else:
                    totaux[depense.categorie] = depense.montant
            return totaux
    
    def creer_camembert_depenses(self):
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure

        # Calculer les totaux par catégorie
        totaux = self.total_depenses_par_categorie()
        categories = list(totaux.keys())
        montants = list(totaux.values())

        # Créer le graphique
        figure = Figure(figsize=(8, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.pie(montants, labels=categories, autopct='%1.1f%%', startangle=140)
        ax.set_title("Répartition des Dépenses par Catégorie")
        return figure

    def creer_histogramme_soldes(self):
        # Calculer les soldes cumulés
        soldes_mensuels = defaultdict(float)
        
        # Ajouter les revenus
        for revenu in self.revenus:
            mois = revenu.date.strftime("%Y-%m")
            soldes_mensuels[mois] += revenu.montant
        
        # Soustraire les dépenses
        for depense in self.depenses:
            mois = depense.date.strftime("%Y-%m")
            soldes_mensuels[mois] -= depense.montant

        # Trier par mois
        mois = sorted(soldes_mensuels.keys())
        
        # Calculer les soldes cumulés (somme des soldes jusqu'à chaque mois)
        soldes_cumules = []
        solde_cumule = 0
        for m in mois:
            solde_cumule += soldes_mensuels[m]
            soldes_cumules.append(solde_cumule)

        # Définir les couleurs en fonction du signe des soldes
        couleurs = ['green' if solde >= 0 else 'red' for solde in soldes_cumules]

        # Créer le graphique
        figure = Figure(figsize=(8, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.bar(mois, soldes_cumules, color=couleurs)  # Appliquer les couleurs personnalisées
        ax.set_title("Solde Cumulé par Mois")
        ax.set_xlabel("Mois")
        ax.set_ylabel("Solde (€)")
        ax.tick_params(axis='x', rotation=45)
        return figure
