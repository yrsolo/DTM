from src.contexts.rendering.internal import usecase as _impl

now_in_timezone = _impl.now_in_timezone
today_in_timezone = _impl.today_in_timezone


class RenderUseCase(_impl.RenderUseCase):
    def build_plan(self, req):
        _impl.now_in_timezone = now_in_timezone
        _impl.today_in_timezone = today_in_timezone
        return super().build_plan(req)


__all__ = ["RenderUseCase", "now_in_timezone", "today_in_timezone"]
