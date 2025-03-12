class Revenu:
    def __init__(self, montant, source, date):
        self.montant = montant
        self.source = source
        self.date = date

    def to_dict(self):
        return {
            "montant": self.montant,
            "source": self.source,
            "date": self.date.strftime("%Y-%m-%d")
        }