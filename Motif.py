class Motif:
    def __init__(self, libelle: str):
        self.__libelle = libelle.strip()

    @property
    def libelle(self) -> str:
        return self.__libelle

    def __str__(self) -> str:
        return self.__libelle
