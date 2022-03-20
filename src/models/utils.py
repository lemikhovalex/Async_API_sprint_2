from orjson import dumps
from orjson import loads as orjson_loads


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode,
    # поэтому декодируем
    return dumps(v, default=default).decode()
