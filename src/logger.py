from logging import Logger

singleton = None

class LoggerWrapper():
    logger: Logger = None

    def __init__(self):
        self.logger = None

    def set_logger(self, logger: Logger):
        """Set the logger instance to use for logging."""
        self.logger = logger

    def info(self, message: str):
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")

    def error(self, message: str):
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")

    def debug(self, message: str):
        if self.logger:
            self.logger.debug(message)
        else:
            print(f"DEBUG: {message}")

    def warning(self, message: str):
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")


def get_logger() -> LoggerWrapper:
    global singleton
    if singleton is None:
        singleton = LoggerWrapper()
    return singleton

def init_logger(logger: Logger):
    """Initialize the logger with a specific logger instance."""
    global singleton
    if singleton is None:
        singleton = LoggerWrapper()
    singleton.set_logger(logger)
    return singleton