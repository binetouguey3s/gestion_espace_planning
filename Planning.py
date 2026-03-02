class Planning:
    def __init__(self, reservation_service):
        self.reservation_service = reservation_service

    def afficher_global(self, date_str: str):
        lignes = self.reservation_service.planning_global(date_str)
        if not lignes:
            print("Aucun creneau affiche.")
            return

        print(f"\nPlanning global du {date_str}")
        print("=" * 62)
        for ligne in lignes:
            print(
                f"[{ligne['id_creneau']}] {ligne['heure_debut']} - {ligne['heure_fin']} | "
                f"{ligne['groupe']} | {ligne['motif']}"
            )

    def afficher_disponibilites(self, date_str: str):
        lignes = self.reservation_service.creneaux_disponibles(date_str)
        if not lignes:
            print("Aucun creneau disponible.")
            return

        print(f"\nDisponibilites du {date_str}")
        print("=" * 40)
        for ligne in lignes:
            print(f"[{ligne['id_creneau']}] {ligne['heure_debut']} - {ligne['heure_fin']}")
