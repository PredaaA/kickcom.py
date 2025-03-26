import json
from typing import Any

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


# Borrowed from discord.py
# https://github.com/Rapptz/discord.py/blob/master/discord/utils.py#L662-L674

if HAS_ORJSON:

    def json_dumps(obj: Any) -> str:
        return orjson.dumps(obj).decode("utf-8")

    json_loads = orjson.loads  # type: ignore

else:

    def json_dumps(obj: Any) -> str:
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)

    json_loads = json.loads
