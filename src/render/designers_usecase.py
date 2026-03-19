from src.contexts.rendering.internal import designers_usecase as _impl

now_in_timezone = _impl.now_in_timezone
today_in_timezone = _impl.today_in_timezone


class DesignersRenderUseCase(_impl.DesignersRenderUseCase):
    def build_plan(self, req):
        _impl.now_in_timezone = now_in_timezone
        _impl.today_in_timezone = today_in_timezone
        return super().build_plan(req)


__all__ = ["DesignersRenderUseCase", "now_in_timezone", "today_in_timezone"]
