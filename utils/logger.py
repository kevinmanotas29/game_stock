"""
Sistema de logging centralizado para GameStock
"""
import logging
import os
from datetime import datetime

# Crear carpeta de logs si no existe
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Nombre del archivo de log con fecha
log_file = os.path.join(log_dir, f'gamestock_{datetime.now().strftime("%Y%m%d")}.log')

# Configurar el formato del log
log_format = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Configurar el logger principal
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        # Handler para archivo
        logging.FileHandler(log_file, encoding='utf-8'),
        # Handler para consola
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """
    Obtiene un logger con el nombre especificado
    
    Args:
        name: Nombre del módulo (usa __name__)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

# Logger principal
logger = get_logger('GameStock')
logger.info("=" * 80)
logger.info("Sistema de logging inicializado")
logger.info(f"Archivo de log: {log_file}")
logger.info("=" * 80)
