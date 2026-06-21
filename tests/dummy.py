from typing import cast


class Dummy:
    def __getattr__(self, name: str):
        async def fail(*args, **kwargs):
            raise AssertionError(f"unexpected interaction with Dummy.{name}")

        return fail


def make_dummy[T](spec: type[T]) -> T:
    return cast(T, Dummy())
