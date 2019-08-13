import json
from typing import Any, Callable, Dict, Optional

# TODO: handling of datetime.{datetime,date,time}

# TODO: support other dumper than json.dumps
# - https://github.com/ijl/orjson
# - https://github.com/python-rapidjson/python-rapidjson
# - https://github.com/esnme/ultrajson/

DefaultFunc = Optional[Callable[[Any], Any]]

def dumps(obj: Any, default: DefaultFunc=None) -> str:
    return json.dumps(obj, default=default, ensure_ascii=False, separators=(',', ':'))
