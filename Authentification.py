import bcrypt
from mysql.connector import Error

from Admin import Admin


class AuthentificationAdmin:
    def __init__(self, db):
        self.db = db
        self.connection = self.db.connecter()
        self.admin_connecte = None

    def inscrire_admin(self, nom: str, email: str, mot_de_passe: str):
        if not nom.strip() or not email.strip() or not mot_de_passe.strip():
            print("Champs invalides pour la creation du compte admin.")
            return None

        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT id_admin FROM admins WHERE email = %s", (email,))
            if cursor.fetchone():
                print("Cet email existe deja.")
                return None

            mot_de_passe_hache = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO admins (nom, email, mot_de_passe) VALUES (%s, %s, %s)",
                (nom, email, mot_de_passe_hache),
            )
            self.connection.commit()
            print("Admin cree avec succes.")
            return cursor.lastrowid
        except Error as exc:
            print(f"Erreur SQL creation admin: {exc}")
            return None
        finally:
            cursor.close()

    def existe_admin(self) -> bool:
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM admins")
            total = cursor.fetchone()[0]
            return total > 0
        except Error as exc:
            print(f"Erreur SQL verification admin: {exc}")
            return False
        finally:
            cursor.close()

    def connecter_admin(self, email: str, mot_de_passe: str):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT id_admin, nom, email, mot_de_passe FROM admins WHERE email = %s LIMIT 1",
                (email,),
            )
            row = cursor.fetchone()
            if not row:
                print("Email inconnu.")
                return None

            hash_db = row[3]
            if isinstance(hash_db, str):
                hash_db = hash_db.encode("utf-8")

            if not bcrypt.checkpw(mot_de_passe.encode("utf-8"), hash_db):
                print("Mot de passe incorrect.")
                return None

            self.admin_connecte = Admin(id_admin=row[0], nom=row[1], email=row[2])
            print(f"Connexion reussie. Bonjour {self.admin_connecte.nom}.")
            return self.admin_connecte
        except Error as exc:
            print(f"Erreur SQL connexion admin: {exc}")
            return None
        finally:
            cursor.close()
