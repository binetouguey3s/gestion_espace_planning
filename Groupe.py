class Groupe:
    def __init__(self, id_groupe: int, nom_groupe: str, responsable: str):
        self.__id_groupe = id_groupe
        self.__nom_groupe = nom_groupe
        self.__responsable = responsable

    @property
    def id_groupe(self) -> int:
        return self.__id_groupe

    @property
    def nom_groupe(self) -> str:
        return self.__nom_groupe

    @property
    def responsable(self) -> str:
        return self.__responsable

    def __repr__(self) -> str:
        return (
            f"Groupe(id_groupe={self.__id_groupe}, "
            f"nom_groupe='{self.__nom_groupe}', responsable='{self.__responsable}')"
        )
