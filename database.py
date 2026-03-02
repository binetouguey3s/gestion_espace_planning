import mysql.connector
from mysql.connector import Error


class PlanningDatabase:
    def __init__(
        self,
        host: str = "localhost",
        user: str = "planning_user",
        password: str = "MotDePassereserve123!",
        database: str = "reservation",
        port: int = 3306,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self._connection = None

    def connecter(self):
        if self._connection and self._connection.is_connected():
            return self._connection

        self._connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
        )
        return self._connection

    def fermer(self) -> None:
        if self._connection and self._connection.is_connected():
            self._connection.close()

    def initialiser_db(self, sql_file: str = "script.sql") -> bool:
        connexion_serveur = None
        cursor = None
        try:
            connexion_serveur = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
            )
            cursor = connexion_serveur.cursor()

            with open(sql_file, "r", encoding="utf-8") as f:
                sql_content = f.read()

            for statement in [s.strip() for s in sql_content.split(";") if s.strip()]:
                cursor.execute(statement)

            connexion_serveur.commit()
            return True
        except (Error, OSError) as exc:
            print(f"Erreur initialisation MySQL: {exc}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connexion_serveur and connexion_serveur.is_connected():
                connexion_serveur.close()
