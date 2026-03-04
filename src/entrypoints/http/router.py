"""HTTP router for index entrypoint."""

from __future__ import annotations

from typing import Any

from src.app.context import AppContext
from src.entrypoints.http.dto import HttpRequest, HttpResponse
from src.entrypoints.http.frontend_compat_handlers import FrontendRootHandler
from src.entrypoints.http.frontend_v2_handler import FrontendV2Handler
from src.entrypoints.http.group_query_handler import GroupQueryHandler


class HttpRouter:
    """Route table based HTTP router."""

    def __init__(self, ctx: AppContext, *, frontend_readmodel_repo_cls: Any) -> None:
        self._group_query_handler = GroupQueryHandler(ctx)
        self._frontend_root_handler = FrontendRootHandler(ctx)
        self._frontend_v2_handler = FrontendV2Handler(ctx, frontend_readmodel_repo_cls=frontend_readmodel_repo_cls)

    async def dispatch(self, req: HttpRequest) -> HttpResponse | None:
        group_query_response = await self._group_query_handler.handle(req)
        if group_query_response is not None:
            return group_query_response
        root_response = self._frontend_root_handler.handle(req)
        if root_response is not None:
            return root_response
        return self._frontend_v2_handler.handle(req)
