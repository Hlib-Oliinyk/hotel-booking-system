
class AppError(Exception):
    status_code: int = 500
    detail: str = "Internal Server Error"
    headers: dict[str, str] | None = None

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)
