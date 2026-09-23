from app.models.sheet import SheetRow
from app.services.google_sheets import normalize_values
from app.utils.hashing import dataset_hash


def test_normalizes_empty_cells_without_shifting():
    assert normalize_values([["A", "B", "C"], ["Apple", "100"], ["", "", "Delhi"]]) == [
        SheetRow(row=2, A="Apple", B="100", C=""), SheetRow(row=3, A="", B="", C="Delhi")
    ]


def test_row_mapping_starts_after_header():
    assert normalize_values([["A", "B", "C"], ["Banana", "200", "Pune"]])[0].row == 2


def test_hash_is_deterministic_and_includes_row_number():
    first = [SheetRow(row=2, A="Apple", B="100", C="Mumbai")]
    assert dataset_hash(first) == dataset_hash(first)
    assert dataset_hash(first) != dataset_hash([SheetRow(row=3, A="Apple", B="100", C="Mumbai")])
