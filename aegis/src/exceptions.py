class AegisBaseException(Exception):
    pass


class RMTypeErr(AegisBaseException):
    def __init__(self, rm: str) -> None:
        self.msg = f"Incorrect rm - {rm}"
        super().__init__()


class UnknownIPErr(AegisBaseException):
    def __init__(self, ip: str | None) -> None:
        self.msg = f"Incorrect ip - {ip}"
        super().__init__()
