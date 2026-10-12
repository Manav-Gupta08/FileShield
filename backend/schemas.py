"""Strict operation schemas reject unknown and abusive parameters."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=256)


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid")
    output_format: Literal["png", "jpeg", "webp", "tiff"] = "png"
    width: int | None = Field(default=None, ge=1, le=10000)
    height: int | None = Field(default=None, ge=1, le=10000)
    quality: int = Field(default=85, ge=1, le=100)
    rotation: Literal[0, 90, 180, 270] = 0
    crop: list[int] | None = Field(default=None, min_length=4, max_length=4)
    dpi: int | None = Field(default=None, ge=36, le=1200)
    pages: list[int] | None = Field(default=None, min_length=1, max_length=200)
    password: str | None = Field(default=None, min_length=12, max_length=256)
    expected_sha256: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")

    @model_validator(mode="after")
    def validate_dimensions(self):
        if (self.width is None) != (self.height is None):
            raise ValueError("Width and height must be supplied together")
        if self.width and self.width * self.height > 20_000_000:
            raise ValueError("Requested image exceeds pixel limit")
        if self.pages is not None and min(self.pages) < 0:
            raise ValueError("Pages use zero-based nonnegative indices")
        return self