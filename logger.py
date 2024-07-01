import logging
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Define colors
        if record.levelno == logging.ERROR:
            color = Fore.RED
        elif record.levelno == logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno == logging.INFO:
            color = Fore.GREEN
        elif record.levelno == logging.DEBUG:
            color = Fore.CYAN
        else:
            color = Fore.WHITE

        # Apply color and format message
        log_message = f"{color}[{record.levelname}] [{current_time}]{' ' * (7-len(record.levelname))} - {record.getMessage()}{Style.RESET_ALL}"
        return log_message

# Configure the logger
logger = logging.getLogger('faprouletteDL-logger')
logger.setLevel(logging.INFO)

# Create a stream handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Set custom formatter to the handler
formatter = CustomFormatter()
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)
