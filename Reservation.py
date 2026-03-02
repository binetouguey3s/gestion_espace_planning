import csv
from datetime import datetime

from mysql.connector import Error, IntegrityError


class ReservationService:
    def __init__(self, db):
        self.db = db
        self.connection = self.db.connecter()

    # autre chemin de reservation (par horaire)
    def reserver_par_horaire(self, date_str: str, heure_debut: str, heure_fin: str, groupe_id: int, motif: str):
        date_obj = self._parse_date(date_str)
        if not date_obj:
            print("Date invalide. Format attendu: YYYY-MM-DD")
            return None
        
        cursor = self.connection.cursor(dictionary=True)

        # Récupérer tous les créneaux dans l’intervalle que l' on veut choisir 
        requete_creneaux = """ SELECT * FROM creneaux WHERE heure_debut >= %s AND heure_fin <= %s """
        cursor.execute(requete_creneaux, (heure_debut, heure_fin))
        creneaux = cursor.fetchall()

        if not creneaux:
            print("Aucun créneau trouvé dans cet intervalle.")
            return
        
        for creneau in creneaux:
            requete_conflit = """ SELECT * FROM reservations WHERE date_reservation = %s AND creneau_id = %s """
            cursor.execute(requete_conflit, (date_obj, creneau["id_creneau"]))
            if cursor.fetchone():
                print(f"Conflit: le créneau  {creneau['heure_debut']} - {creneau['heure_fin']} est déjà réservé.")
                return

        for creneau in creneaux:
            requete_insert = """ INSERT INTO reservations (date_reservation, creneau_id, groupe_id, motif) VALUES (%s, %s, %s, %s) """
            cursor.execute(requete_insert, (date_obj, creneau["id_creneau"], groupe_id, motif))

        self.connection.commit()
        print("Réservation effectuée avec succès pour ces créneaux.")


#fin  reserver par horaire

    def _parse_date(self, date_str: str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    

    def ajouter_groupe(self, nom_groupe: str, responsable: str):
        if not nom_groupe.strip() or not responsable.strip():
            print("Nom de groupe et responsable obligatoires.")
            return None

        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO groupes (nom_groupe, responsable) VALUES (%s, %s)",
                (nom_groupe.strip(), responsable.strip()),
            )
            self.connection.commit()
            print("Groupe ajoute.")
            return cursor.lastrowid
        except IntegrityError:
            print("Ce groupe existe deja.")
            return None
        except Error as exc:
            print(f"Erreur SQL ajout groupe: {exc}")
            return None
        finally:
            cursor.close()

    def lister_groupes(self):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id_groupe, nom_groupe, responsable FROM groupes ORDER BY nom_groupe")
            return cursor.fetchall()
        finally:
            cursor.close()

    def lister_creneaux(self):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id_creneau, heure_debut, heure_fin FROM creneaux ORDER BY heure_debut"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def reserver(self, date_str: str, creneau_id: int, groupe_id: int, motif: str):
        date_obj = self._parse_date(date_str)
        if not date_obj:
            print("Date invalide. Format attendu: YYYY-MM-DD")
            return None

        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT id_creneau FROM creneaux WHERE id_creneau = %s", (creneau_id,))
            if not cursor.fetchall():
                print("ID creneau inexistant.")
                return None

            cursor.execute("SELECT id_groupe FROM groupes WHERE id_groupe = %s", (groupe_id,))
            if not cursor.fetchone():
                print("ID groupe inexistant.")
                return None

            cursor.execute(
                "SELECT id_reservation FROM reservations WHERE date_reservation = %s AND creneau_id = %s",
                (date_obj, creneau_id),
            )
            if cursor.fetchone():
                print("Conflit: ce creneau est deja reserve a cette date.")
                return None

            cursor.execute(
                """
                INSERT INTO reservations (date_reservation, creneau_id,  groupe_id, motif)
                VALUES (%s, %s, %s, %s)
                """,
                (date_obj, creneau_id, groupe_id, motif.strip() or "Sans motif"),
            )
            self.connection.commit()
            print("Reservation validee.")
            return cursor.lastrowid
        except IntegrityError:
            print("Conflit SQL detecte: reservation deja existante.")
            return None
        except Error as exc:
            print(f"Erreur SQL reservation: {exc}")
            return None
        finally:
            cursor.close()

    def planning_global(self, date_str: str):
        date_obj = self._parse_date(date_str)
        if not date_obj:
            print("Date invalide. Format attendu: YYYY-MM-DD")
            return []

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.id_creneau,
                    c.heure_debut,
                    c.heure_fin,
                    COALESCE(g.nom_groupe, '[LIBRE]') AS groupe,
                    COALESCE(r.motif, '-') AS motif
                FROM creneaux c
                LEFT JOIN reservations r
                    ON r.creneau_id = c.id_creneau
                    AND r.date_reservation = %s
                LEFT JOIN groupes g ON g.id_groupe = r.groupe_id
                ORDER BY c.heure_debut
                """,
                (date_obj,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def creneaux_disponibles(self, date_str: str):
        date_obj = self._parse_date(date_str)
        if not date_obj:
            print("Date invalide. Format attendu: YYYY-MM-DD")
            return []

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT c.id_creneau, c.heure_debut, c.heure_fin
                FROM creneaux c
                LEFT JOIN reservations r
                    ON r.creneau_id = c.id_creneau
                    AND r.date_reservation = %s
                WHERE r.id_reservation IS NULL
                ORDER BY c.heure_debut
                """,
                (date_obj,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def exporter_csv(self, fichier: str = "planning_journalier.csv"):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    r.date_reservation,
                    c.heure_debut,
                    c.heure_fin,
                    g.nom_groupe,
                    r.motif,
                    g.responsable
                FROM reservations r
                JOIN creneaux c ON c.id_creneau = r.creneau_id
                JOIN groupes g ON g.id_groupe = r.groupe_id
                ORDER BY r.date_reservation, c.heure_debut
                """
            )
            rows = cursor.fetchall()

            with open(fichier, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "Date",
                        "Heure debut",
                        "Heure fin",
                        "Groupe",
                        "Motif",
                        "Responsable groupe",
                    ]
                )
                for row in rows:
                    writer.writerow(
                        [
                            row["date_reservation"],
                            row["heure_debut"],
                            row["heure_fin"],
                            row["nom_groupe"],
                            row["motif"],
                            row["responsable"],
                        ]
                    )
            return fichier
        except Error as exc:
            print(f"Erreur export CSV: {exc}")
            return None
        finally:
            cursor.close()
