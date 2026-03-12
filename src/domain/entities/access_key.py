from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets
import string

@dataclass
class AccessKey:
    """Entidade que representa uma chave de acesso"""
    email: str
    key: str
    created_at: datetime
    expires_at: datetime
    used: bool = False
    ip: str = None
    
    @classmethod
    def create(cls, email: str, ip: str = None):
        """Factory method para criar nova chave"""
        key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        now = datetime.now()
        return cls(
            email=email.lower(),
            key=key,
            created_at=now,
            expires_at=now + timedelta(hours=4),
            ip=ip
        )
    
    def is_valid(self) -> bool:
        """Verifica se a chave é válida"""
        return not self.used and datetime.now() < self.expires_at
    
    def use(self):
        """Marca a chave como usada"""
        self.used = True