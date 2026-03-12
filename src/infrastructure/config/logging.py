"""Configuração de logging para a aplicação"""
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO):
    """Configura o logging da aplicação"""
    
    # Formato dos logs
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    # Handler para arquivo (opcional)
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / 'app.log')
    file_handler.setFormatter(log_format)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduzir logs de bibliotecas muito verbosas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name):
    """Retorna um logger configurado"""
    return logging.getLogger(name)