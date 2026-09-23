from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.models.sheet import ErrorResponse, SheetResponse, SheetRowUpdate, UpdateResponse
from app.utils.hashing import dataset_hash

router = APIRouter(prefix="/api/sheet", tags=["Google Sheet"])


def get_sheets(request: Request):
    if request.app.state.sheets is None:
        raise HTTPException(status_code=503, detail="Google Sheets is not configured.")
    return request.app.state.sheets


@router.get("", response_model=SheetResponse, summary="Read the current Google Sheet data")
async def get_sheet(sheets=Depends(get_sheets)):
    rows = sheets.get_rows()
    return SheetResponse(data=rows, hash=dataset_hash(rows))


@router.put("/{row_number}", response_model=UpdateResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}, summary="Update exactly A:C in an existing Sheet row")
async def update_sheet_row(row_number: int, update: SheetRowUpdate, request: Request, sheets=Depends(get_sheets)):
    if row_number < 1:
        raise HTTPException(status_code=400, detail="Row 1 contains headers and cannot be changed.")
    rows = sheets.get_rows()
    if not any(item.row == row_number for item in rows):
        raise HTTPException(status_code=404, detail="Sheet row was not found.")
    current_hash = dataset_hash(rows)
    if update.expected_hash and update.expected_hash != current_hash:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The Sheet changed externally. Reloaded data is required before saving.")
    data = sheets.update_row(row_number, update)
    refreshed = sheets.get_rows()
    request.app.state.sync.last_hash = dataset_hash(refreshed)
    await request.app.state.sync.broadcast(refreshed)
    return UpdateResponse(message="Row updated successfully", row=row_number, data=data)
