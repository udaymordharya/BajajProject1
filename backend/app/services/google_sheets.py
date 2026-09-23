from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.config import Settings
from app.models.sheet import SheetRow, SheetRowUpdate

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def normalize_values(values: list[list[str]]) -> list[SheetRow]:
    """Maps returned A:C values to physical Sheets rows without shifting empties."""
    rows: list[SheetRow] = []
    for sheet_row, value in enumerate(values, start=1):
        cells = list(value[:3]) + [""] * (3 - len(value[:3]))
        rows.append(SheetRow(row=sheet_row, A=str(cells[0]), B=str(cells[1]), C=str(cells[2])))
    return rows


class GoogleSheetsService:
    def __init__(self, settings: Settings):
        if not all((settings.google_project_id, settings.google_client_email, settings.google_private_key, settings.google_sheet_id)):
            raise RuntimeError("Google Sheets is not configured. Set the required GOOGLE_* environment variables.")
        credentials = Credentials.from_service_account_info({
            "type": "service_account", "project_id": settings.google_project_id,
            "client_email": settings.google_client_email,
            "private_key": settings.google_private_key.replace("\\n", "\n"),
            "token_uri": "https://oauth2.googleapis.com/token",
        }, scopes=SCOPES)
        self.client = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        self.sheet_id = settings.google_sheet_id
        self.range = settings.google_sheet_range

    def get_rows(self) -> list[SheetRow]:
        result = self.client.spreadsheets().values().get(
            spreadsheetId=self.sheet_id, range=self.range, majorDimension="ROWS"
        ).execute()
        return normalize_values(result.get("values", []))

    def update_row(self, row_number: int, update: SheetRowUpdate) -> SheetRow:
        sheet_name = self.range.split("!", 1)[0] if "!" in self.range else "Sheet1"
        target = f"{sheet_name}!A{row_number}:C{row_number}"
        self.client.spreadsheets().values().update(
            spreadsheetId=self.sheet_id, range=target, valueInputOption="USER_ENTERED",
            body={"values": [[update.A, update.B, update.C]]},
        ).execute()
        return SheetRow(row=row_number, A=update.A, B=update.B, C=update.C)
