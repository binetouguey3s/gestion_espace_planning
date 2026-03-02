from Authentification import AuthentificationAdmin
from Planning import Planning
from Reservation import ReservationService
from database import PlanningDatabase


class Menu:
    def __init__(self):
        self.db = PlanningDatabase()
        if not self.db.initialiser_db("script.sql"):
            raise RuntimeError("Impossible d'initialiser la base de donnees")

        self.auth = AuthentificationAdmin(self.db)
        self.reservation = ReservationService(self.db)
        self.planning = Planning(self.reservation)

    def _inscription_admin_initiale(self):
        if not self.auth.existe_admin():
            print("\n=== Creation du premier admin (obligatoire) ===")
            while True:
                nom = input("Nom: ").strip()
                email = input("Email: ").strip()
                mdp = input("Mot de passe: ").strip()
                if self.auth.inscrire_admin(nom, email, mdp):
                    break
                print("Echec creation admin, veuillez recommencer.")
            return

        print("\n=== Creation admin (optionnelle) ===")
        reponse = input("Creer un admin maintenant ? (o/n): ").strip().lower()
        if reponse != "o":
            return

        nom = input("Nom: ").strip()
        email = input("Email: ").strip()
        mdp = input("Mot de passe: ").strip()
        self.auth.inscrire_admin(nom, email, mdp)

    def _connexion_obligatoire(self):
        while self.auth.admin_connecte is None:
            print("\n=== Connexion administrateur ===")
            email = input("Email: ").strip()
            mdp = input("Mot de passe: ").strip()
            self.auth.connecter_admin(email, mdp)

# ajout pour choisir plusieurs creneaux par horaires
    # def _creneau_complet(self):
    #     print("\n===Choisir un creneau A à un crenaux B ===")
    #     for c in self.reservation.lister_creneaux():
    #         for c in self.reservation.lister_creneaux():
    #             print(c)
# fin ajout 
    def _afficher_creneaux_et_groupes(self):
        print("\nCreneaux existants")
        for c in self.reservation.lister_creneaux():
            print(f"[{c['id_creneau']}] {c['heure_debut']} - {c['heure_fin']}")


        print("\nGroupes existants")
        groupes = self.reservation.lister_groupes()
        if not groupes:
            print("Aucun groupe.")
            return
        for g in groupes:
            print(f"[{g['id_groupe']}] {g['nom_groupe']} (Resp: {g['responsable']})")

    def run(self):
        self._inscription_admin_initiale()
        self._connexion_obligatoire()

        while True:
            print("\n=== ROOM-MASTER PRO ===")
            print("1. Afficher planning global")
            print("2. Afficher disponibilites")
            print("3. Ajouter un groupe")
            print("4. Reserver un creneau")
            print("5. Reservation de creneau par intervalle horaire que l'on souhaite")
            print("6. Exporter CSV")
            print("7. Quitter")

            choix = input("Choix: ").strip()

            if choix == "1":
                date_str = input("Date (YYYY-MM-DD): ").strip()
                self.planning.afficher_global(date_str)
            elif choix == "2":
                date_str = input("Datenom (YYYY-MM-DD): ").strip()
                self.planning.afficher_disponibilites(date_str)
            elif choix == "3":
                nom = input("Nom du groupe: ").strip()
                resp = input("Responsable: ").strip()
                self.reservation.ajouter_groupe(nom, resp)
            elif choix == "4":
                self._afficher_creneaux_et_groupes()
                date_str = input("Date (YYYY-MM-DD): ").strip()
                try:
                    creneau_id = int(input("ID creneau: ").strip())
                    groupe_id = int(input("ID groupe: ").strip())
                except ValueError:
                    print("Les IDs doivent etre numeriques.")
                    continue
                motif = input("Motif (conference/reunion/atelier...): ").strip()
                self.reservation.reserver(date_str, creneau_id, groupe_id, motif)
                
            elif choix == "5":
                self.reservation = ReservationService(self.db)
                self._afficher_creneaux_et_groupes()
                date_str = input("DATE (YYYY-MM-DD): ").strip()
                try:
                    heure_debut = (input("Heure debut (HH:MN:SEC): ").strip())
                    heure_fin = input("Heure fin (HH:MN:SEC): ").strip()
                    groupe_id = int(input("ID du groupe: ").strip())
                except ValueError:
                    print("Les IDs doivent etre numeriques.")
                    continue
                motif = input("Motif (conference/reunion/atelier...): ").strip()
                self.reservation.reserver_par_horaire(date_str, heure_debut, heure_fin, groupe_id, motif)
            elif choix == "6":
                fichier = self.reservation.exporter_csv("planning_journalier.csv")
                if fichier:
                    print(f"Export termine: {fichier}")
            elif choix == "7":
                self.db.fermer()
                print("Au revoir.")
                break
            else:
                print("Choix invalide.")
Menu().run()
 