class ReservationService:

    def __init__(self, connexion):
        self.connexion = connexion

    def reserver_par_horaire(self, date, heure_debut, heure_fin, id_groupe, motif):
        curseur = self.connexion.cursor(dictionary=True)

        # Récupérer tous les créneaux dans l’intervalle
        requete_creneaux = """
        SELECT * FROM creneaux
        WHERE heure_debut >= %s AND heure_fin <= %s
        """
        curseur.execute(requete_creneaux, (heure_debut, heure_fin))
        creneaux = curseur.fetchall()

        if not creneaux:
            print("Aucun créneau trouvé dans cet intervalle.")
            return

        # Vérifier les conflits
        for creneau in creneaux:
            requete_conflit = """
            SELECT * FROM reservations
            WHERE date_reservation = %s AND id_creneau = %s
            """
            curseur.execute(requete_conflit, (date, creneau["id_creneau"]))
            if curseur.fetchone():
                print(f"Conflit: le créneau {creneau['heure_debut']} - {creneau['heure_fin']} est déjà réservé.")
                return

        # Insérer toutes les réservations
        for creneau in creneaux:
            requete_insert = """
            INSERT INTO reservations (date_reservation, id_creneau, id_groupe, motif)
            VALUES (%s, %s, %s, %s)
            """
            curseur.execute(requete_insert, (date, creneau["id_creneau"], id_groupe, motif))

        self.connexion.commit()
        print("Réservation effectuée avec succès pour tous les créneaux.")