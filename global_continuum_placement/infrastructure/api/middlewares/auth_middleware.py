from collections import Callable

from aiohttp import web
from dependency_injector.wiring import Provide
from global_continuum_placement.application.auth_service import AuthService
from global_continuum_placement.container import ApplicationContainer
from global_continuum_placement.infrastructure.api.schemas.error_schema import ErrorSchema


# Design decorator to indicate that
def skip():
    def wrapper(handler: Callable):
        handler.auth_skip = True
        return handler

    return wrapper


def handle(
    public_paths: [str],
    service: AuthService = Provide[ApplicationContainer.auth_service],
):
    @web.middleware
    async def middleware_handler(request: web.Request, handler):
        is_public = any(request.path.startswith(item) for item in public_paths)
        if is_public:
            return await handler(request)
        elif getattr(handler, "auth_skip", False):
            return await handler(request)
        else:
            token = request.headers.get("Authorization", None)
            token_payload = service.check_access(token)
            if not token_payload:
                result = ErrorSchema().dump({"name": "Access denied"})
                return web.json_response(result, status=401)
            else:
                request["user_id"] = token_payload.user_id
                return await handler(request)

    return middleware_handler
