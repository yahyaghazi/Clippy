class Depense:
    def __init__(self, montant, categorie, date):
        self.montant = montant
        self.categorie = categorie
        self.date = date

    def to_dict(self):
        return {
            "montant": self.montant,
            "categorie": self.categorie,
            "date": self.date.strftime("%Y-%m-%d")
        }
