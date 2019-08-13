import json
from typing import Any, Callable, Dict, Optional

DefaultFunc = Optional[Callable[[Any], Any]]

def dumps(obj: Any, default: DefaultFunc=None) -> str:
    return json.dumps(obj, default=default, ensure_ascii=False, separators=(',', ':'))
