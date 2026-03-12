from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.access_key import AccessKey

class KeyRepository(ABC):
    """Contrato para repositório de chaves"""
    
    @abstractmethod
    def save(self, key: AccessKey) -> None:
        pass
    
    @abstractmethod
    def find_by_key(self, key: str) -> Optional[AccessKey]:
        pass
    
    @abstractmethod
    def find_valid_by_email(self, email: str) -> Optional[AccessKey]:
        pass
    
    @abstractmethod
    def mark_as_used(self, key: str) -> None:
        pass