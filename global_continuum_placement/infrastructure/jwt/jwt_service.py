import logging
from typing import Optional

import jwt

from global_continuum_placement.domain.auth.auth_token import AuthToken
from global_continuum_placement.domain.services.security_service import ISecurityService


class JwtService(ISecurityService):
    def __init__(self, secret_key: str):
        self.logger = logging.getLogger("AuthService")
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def get_auth_token(self, token: str) -> Optional[AuthToken]:
        try:
            decoded_token = jwt.decode(
                jwt=token,
                key=self.secret_key,
                verify=True,
                algorithms=self.algorithm,
            )
            self.logger.debug("Token decoded - %s", decoded_token)
            return AuthToken(user_id=decoded_token["user_id"])
        except jwt.DecodeError as err:
            self.logger.warning("Token decoding failed - %s", err)
            return None
        except jwt.ExpiredSignatureError as err:
            self.logger.warning("Token expired - %s", err)
            return None
