# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 22:04:37 2025

@author: marce
"""
import logging
import os
from logging.handlers import RotatingFileHandler

# Caminho para o diretório de logs
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pdf_monitor.log")

# Certifique-se de que o diretório de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

# Configuração do logger
def setup_logger():
    logger = logging.getLogger("PDFMonitor")
    logger.setLevel(logging.DEBUG)  # Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Formato dos logs
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # Handler para salvar logs em arquivo (com rotação de arquivos)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler para exibir logs no console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Adiciona os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Instancia o logger global
logger = setup_logger()


