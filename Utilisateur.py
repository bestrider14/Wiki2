class Utilisateur:
    def __init__(self):
        self.idUtilisateur = None
        self.nom = None
        self.email = None
        self.genre = None
        self.role = None

    def getInfoUtilisateur(self):
        return [self.idUtilisateur, self.nom, self.email, self.genre, self.role]

    def setInfoUtilisateur(self, id, nom, email, genre, role):
        self.idUtilisateur = id
        self.nom = nom
        self.email = email
        self.genre = genre
        self.role = role
