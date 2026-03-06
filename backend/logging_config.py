import logging
import os
import json
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Criar diretório de logs se não existir
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class AccessLogFilter(logging.Filter):
    """Filtro para logs de acesso - ignora health checks"""
    def filter(self, record):
        # Não logar health checks para não poluir
        if hasattr(record, 'path') and record.path in ['/api/health', '/']:
            return False
        return True

def setup_logging():
    """Configura logging estruturado para a aplicação"""
    
    # Formato JSON para logs estruturados [citation:1]
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            
            # Adicionar atributos extras se existirem
            for attr in ['method', 'path', 'status_code', 'client_ip', 
                        'user_agent', 'process_time', 'user']:
                if hasattr(record, attr):
                    log_record[attr] = getattr(record, attr)
            
            return json.dumps(log_record)
    
    # Configuração dos handlers
    handlers = {
        'access': TimedRotatingFileHandler(
            filename=os.path.join(LOG_DIR, 'access.log'),
            when='midnight',
            interval=1,
            backupCount=30,  # Manter 30 dias de histórico
            encoding='utf-8'
        ),
        'error': TimedRotatingFileHandler(
            filename=os.path.join(LOG_DIR, 'error.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        ),
        'app': TimedRotatingFileHandler(
            filename=os.path.join(LOG_DIR, 'app.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
    }
    
    # Configurar formatters
    json_formatter = JsonFormatter()
    for handler in handlers.values():
        handler.setFormatter(json_formatter)
    
    # Configurar logger de acesso
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(handlers['access'])
    access_logger.addFilter(AccessLogFilter())
    
    # Configurar logger de erro
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)
    error_logger.addHandler(handlers['error'])
    
    # Configurar logger da aplicação
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(handlers['app'])
    
    return {
        'access': access_logger,
        'error': error_logger,
        'app': app_logger
    }

# Singleton dos loggers
loggers = setup_logging()

def get_logger(name):
    """Retorna o logger solicitado"""
    return loggers.get(name, logging.getLogger(name))
