class FlyInError(Exception):
    """Mere de toutes les erreurs que le programme explique a l utilisateur."""


class ParseError(FlyInError):
    def __init__(self, line: int | None, cause: str) -> None:
        self.line = line
        self.cause = cause
        where = f"line {line}: " if line is not None else ""
        super().__init__(f"{where}{cause}")


class NoPathError(FlyInError):
    """Aucun chemin entre start et end."""


class SimulationError(FlyInError):
    """Garde-fou : ne doit jamais arriver si Clock et Engine sont d accord."""
