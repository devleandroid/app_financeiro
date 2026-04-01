"""Compatibilidade - encaminha para email_smtp"""
from .email_smtp import EmailSender

# Re-exportar a classe
__all__ = ['EmailSender']

# Instância global
email_sender = EmailSender()"""Compatibilidade - encaminha para email_smtp"""
from .email_smtp import EmailSender

# Re-exportar a classe
__all__ = ['EmailSender']

# Instância global
email_sender = EmailSender()