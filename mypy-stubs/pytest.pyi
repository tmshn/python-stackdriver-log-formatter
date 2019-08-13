import typing


Ret = typing.Any
FixtureFunc = typing.Callable[[], Ret]


@typing.overload
def fixture(
    scope: str=...,
    params: typing.Optional[typing.List[typing.Any]]=...,
    autouse: bool=...,
    ids: typing.Optional[typing.List[str]]=...,
    name: typing.Optional[str]=...,
) -> typing.Callable[[FixtureFunc], FixtureFunc]: ...


@typing.overload
def fixture(
    scope: FixtureFunc,
) -> FixtureFunc: ...

