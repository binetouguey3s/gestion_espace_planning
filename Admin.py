class Admin:
    def __init__(self, id_admin: int, nom: str, email: str):
        self.__id_admin = id_admin
        self.__nom = nom
        self.__email = email

    @property
    def id_admin(self) -> int:
        return self.__id_admin

    @property
    def nom(self) -> str:
        return self.__nom

    @property
    def email(self) -> str:
        return self.__email

    def __repr__(self) -> str:
        return f"Admin(id_admin={self.__id_admin}, nom='{self.__nom}', email='{self.__email}')"
