from typing import Optional

from global_continuum_placement.domain.auth.auth_token import AuthToken
from global_continuum_placement.domain.services.security_service import ISecurityService


class AuthService:
    def __init__(self, security_service: ISecurityService):
        self.security_service = security_service

    def check_access(self, token: str) -> Optional[AuthToken]:
        return self.security_service.get_auth_token(token) if token else None
