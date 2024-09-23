from pathlib import Path, PosixPath
from unittest.mock import patch

import pytest

from aider.main import load_dotenv_files


@pytest.fixture
def mock_generate_search_path_list():
    with patch("aider.main.generate_search_path_list") as mock:
        mock.return_value = [PosixPath("/app/.env"), PosixPath("/app/.env.local")]
        yield mock


@pytest.fixture
def mock_load_dotenv():
    with patch("aider.main.load_dotenv") as mock:
        yield mock


def test_load_dotenv_files_permission_error(
    mock_generate_search_path_list, mock_load_dotenv, capsys
):
    def mock_is_file(self):
        return self in [PosixPath("/app/.env"), PosixPath("/app/.env.local")]

    def mock_load_dotenv_with_permission_error(*args, **kwargs):
        if PosixPath(args[0]) == PosixPath("/app/.env"):
            raise PermissionError(13, "Permission denied", str(args[0]))

    with patch.object(Path, "is_file", mock_is_file):
        mock_load_dotenv.side_effect = mock_load_dotenv_with_permission_error
        result = load_dotenv_files("/app", ".env")

    # Check that the function returned only the second file and skipped the first
    assert result == [PosixPath("/app/.env.local")]

    # Check that the correct error messages were printed
    captured = capsys.readouterr()
    assert "Permission denied for" in captured.out
    assert str(PosixPath("/app/.env")) in captured.out
    assert str(PosixPath("/app/.env.local")) not in captured.out

    # Check that load_dotenv was called twice (attempted for both files)
    assert mock_load_dotenv.call_count == 2
    # mock_load_dotenv.assert_any_call(str(PosixPath("/app/.env")), override=True, encoding="utf-8")
    # mock_load_dotenv.assert_any_call(
    #     str(PosixPath("/app/.env.local")), override=True, encoding="utf-8"
    # )


def test_load_dotenv_files_success(mock_generate_search_path_list, mock_load_dotenv):
    with patch.object(Path, "is_file", return_value=True):
        result = load_dotenv_files("/app", ".env")

    # Check that the function returned both files as loaded
    assert result == [PosixPath("/app/.env"), PosixPath("/app/.env.local")]

    # Check that load_dotenv was called twice (once for each file)
    assert mock_load_dotenv.call_count == 2
    # mock_load_dotenv.assert_any_call(str(PosixPath("/app/.env")), override=True, encoding="utf-8")
    # mock_load_dotenv.assert_any_call(
    #     str(PosixPath("/app/.env.local")), override=True, encoding="utf-8"
    # )
