import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)
Handler = Callable[..., Any]


class Router:
    def __init__(self) -> None:
        self._routes:     dict[str, dict[str, Handler]] = {}
        self._middleware: list[Callable] = []
        self._error_handlers: dict[type, Callable] = {}

    def use(self, fn: Callable) -> None:
        self._middleware.append(fn)

    def on_error(self, exc_type: type) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self._error_handlers[exc_type] = fn
            return fn
        return decorator

    def route(self, path: str, method: str = "GET") -> Callable:
        def decorator(fn: Handler) -> Handler:
            self._routes.setdefault(path, {})[method.upper()] = fn
            logger.debug("Route: %s %s → %s", method.upper(), path, fn.__name__)
            return fn
        return decorator

    def get(self, path: str)    -> Callable: return self.route(path, "GET")
    def post(self, path: str)   -> Callable: return self.route(path, "POST")
    def put(self, path: str)    -> Callable: return self.route(path, "PUT")
    def delete(self, path: str) -> Callable: return self.route(path, "DELETE")
    def patch(self, path: str)  -> Callable: return self.route(path, "PATCH")

    def resolve(self, path: str, method: str) -> Optional[Handler]:
        return self._routes.get(path, {}).get(method.upper())

    def dispatch(self, path: str, method: str = "GET", **kw: Any) -> Any:
        handler = self.resolve(path, method)
        if handler is None:
            raise KeyError(f"No route: {method} {path}")
        ctx = dict(kw)
        for mw in self._middleware:
            result = mw(ctx)
            if result is not None:
                ctx = result
        try:
            return handler(**ctx)
        except Exception as exc:
            for exc_type, fn in self._error_handlers.items():
                if isinstance(exc, exc_type):
                    return fn(exc)
            raise

    def all_routes(self) -> list[tuple[str, str, str]]:
        out = []
        for path, methods in self._routes.items():
            for method, fn in methods.items():
                out.append((method, path, fn.__name__))
        return sorted(out)

    def __repr__(self) -> str:
        n = sum(len(m) for m in self._routes.values())
        return f"<Router routes={n} middleware={len(self._middleware)}>"


router   = Router()
get      = router.get
post     = router.post
put      = router.put
delete   = router.delete
patch    = router.patch
dispatch = router.dispatch
