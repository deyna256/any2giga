from importlib import metadata, resources

from gigachat import GigaChat
from litestar import Litestar

import any2giga


def test_distribution_is_installed_and_typed() -> None:
    assert metadata.version("any2giga")
    assert resources.files(any2giga).joinpath("py.typed").is_file()


def test_runtime_dependencies_are_available() -> None:
    assert callable(GigaChat)
    assert callable(Litestar)
