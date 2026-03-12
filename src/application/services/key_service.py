"""Serviço de gerenciamento de chaves de acesso"""
from typing import Optional, Tuple
from src.domain.entities.access_key import AccessKey
from src.domain.interfaces.key_repository import KeyRepository
from src.infrastructure.external.email_smtp import EmailSender

class KeyService:
    """Serviço para gerenciar chaves de acesso"""
    
    def __init__(self, key_repository: KeyRepository, email_sender: EmailSender):
        self.repository = key_repository
        self.email_sender = email_sender
    
    def request_key(self, email: str, ip: str = None) -> Tuple[bool, str, Optional[str]]:
        """Solicita uma nova chave de acesso"""
        # Verificar se já existe chave válida
        existing = self.repository.find_valid_by_email(email)
        if existing:
            return False, "Você já possui uma chave válida. Verifique seu email.", existing.key
        
        # Criar nova chave
        key = AccessKey.create(email, ip)
        self.repository.save(key)
        
        # Enviar por email
        self.email_sender.send_key(email, key.key)
        
        return True, "Chave enviada para seu email!", key.key
    
    def validate_key(self, key: str, ip: str = None) -> Tuple[bool, str, Optional[str]]:
        """Valida uma chave de acesso"""
        access_key = self.repository.find_by_key(key)
        
        if not access_key:
            return False, "Chave inválida!", None
        
        if not access_key.is_valid():
            return False, "Chave expirada ou já utilizada!", None
        
        # Marcar como usada
        self.repository.mark_as_used(key)
        
        return True, "Acesso liberado!", access_key.email
