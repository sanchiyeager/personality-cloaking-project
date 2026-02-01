import logging, os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/simulation.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def get_logger():
    return logging.getLogger("sim")
