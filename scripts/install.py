class Logger:
    @staticmethod
    def header(msg: str, emoji: str) -> None:
        print(f"{emoji} {msg}")

    @staticmethod
    def step(msg: str, emoji: str) -> None:
        print(f"{emoji} {msg}")

    @staticmethod
    def progress(msg: str) -> None:
        print(f"⏳ {msg}...")

    @staticmethod
    def success(msg: str, emoji: str) -> None:
        print(f"{emoji} {msg}")

    @staticmethod
    def error(msg: str, emoji: str) -> None:
        print(f"{emoji} {msg}")

    @staticmethod
    def warning(msg: str, emoji: str) -> None:
        print(f"{emoji} {msg}")

    @staticmethod
    def info(msg: str, emoji: str) -> None:
        print(f"{emoji} {msg}")
