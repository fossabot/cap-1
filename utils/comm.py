from pathlib import Path


def project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def test_path(t):

    path = Path(t)
    print(path.resolve())