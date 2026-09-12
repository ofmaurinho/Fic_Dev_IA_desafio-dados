import logging
import os


def configurar_logging() -> None:
    """Configura o registro de logs da aplicação."""

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename="logs/processamento.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )