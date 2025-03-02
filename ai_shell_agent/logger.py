import logging
from colorama import init, Fore, Style

# Initialize colorama
init()

# Create a custom formatter
class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.CYAN + "%(message)s" + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + "%(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "%(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "%(message)s" + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + "%(message)s" + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Create logger
logger = logging.getLogger('ai_shell')
logger.setLevel(logging.INFO)

# Create console handler with custom formatter
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(ColoredFormatter())

# Add handler to logger
logger.addHandler(ch)

# Convenience methods
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical 