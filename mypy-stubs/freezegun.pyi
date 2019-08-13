import datetime
import typing


# mypy currently does not support cyclic recursive type definition, so just work-around
# see: https://github.com/python/mypy/issues/731
# AcceptableTimes = typing.Union[
#     None,
#     str,
#     datetime.date,
#     datetime.datetime,
#     datetime.timedelta,
#     typing.Callable[[], AcceptableTimes],
#     typing.Iterator[AcceptableTimes],
# ]
AcceptableTimesWithoutFuncs = typing.Union[
    None,
    str,
    datetime.date,
    datetime.datetime,
    datetime.timedelta,
]
AcceptableTimes = typing.Union[
    AcceptableTimesWithoutFuncs,
    typing.Callable[[], AcceptableTimesWithoutFuncs],
    typing.Iterator[AcceptableTimesWithoutFuncs],
]

DateTimeFactory = typing.Callable[[], datetime.datetime]


def freeze_time(
    time_to_freeze:AcceptableTimes=...,
    tz_offset: typing.Union[int, datetime.timedelta]=...,
    ignore: typing.Optional[typing.Iterable[str]]=...,
    tick: bool=...,
    as_arg: bool=...,
    auto_tick_seconds: int=...
) -> typing.ContextManager[DateTimeFactory]: ...
