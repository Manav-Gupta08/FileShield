import pytest
from pydantic import ValidationError

from backend.schemas import Credentials, Options
from backend.storage import display_filename, job_directory


def test_command_injection_parameter_rejected():
    with pytest.raises(ValidationError):
        Options.model_validate({"output_format": "png; whoami"})
    with pytest.raises(ValidationError):
        Options.model_validate({"shell": True})


def test_dimensions_bounded():
    with pytest.raises(ValidationError):
        Options(width=10000, height=10000)


def test_filename_is_label_only():
    assert display_filename("../../etc/passwd") == "passwd"
    with pytest.raises(ValueError):
        display_filename("bad\x00name")
    with pytest.raises(ValueError):
        job_directory("../../etc/passwd")


def test_credentials_reject_short_password():
    with pytest.raises(ValidationError):
        Credentials(username="user", password="short")