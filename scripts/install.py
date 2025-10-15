class Logger:
    @staticmethod
    def header(msg, emoji):
        print(f"{emoji} {msg}")

    @staticmethod
    def step(msg, emoji):
        print(f"{emoji} {msg}")

    @staticmethod
    def progress(msg):
        print(f"⏳ {msg}...")

    @staticmethod
    def success(msg, emoji):
        print(f"{emoji} {msg}")

    @staticmethod
    def error(msg, emoji):
        print(f"{emoji} {msg}")

    @staticmethod
    def warning(msg, emoji):
        print(f"{emoji} {msg}")

    @staticmethod
    def info(msg, emoji):
        print(f"{emoji} {msg}")
