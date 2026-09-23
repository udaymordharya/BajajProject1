from pydantic import BaseModel, ConfigDict, Field


class SheetRow(BaseModel):
    row: int = Field(ge=1, description="Actual 1-based Google Sheet row number")
    A: str = ""
    B: str = ""
    C: str = ""


class SheetRowUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False)
    A: str = Field(max_length=1000)
    B: str = Field(max_length=1000)
    C: str = Field(max_length=1000)
    expected_hash: str | None = Field(default=None, min_length=64, max_length=64)


class SheetResponse(BaseModel):
    data: list[SheetRow]
    hash: str


class UpdateResponse(BaseModel):
    message: str
    row: int
    data: SheetRow


class ErrorResponse(BaseModel):
    detail: str
