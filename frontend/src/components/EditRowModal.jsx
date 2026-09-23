import { useEffect, useState } from "react";
export default function EditRowModal({ rows, onClose, onSave }) {
  const [rowNumber, setRowNumber] = useState(rows[0]?.row || "");
  const selected = rows.find((row) => row.row === Number(rowNumber));
  const [form, setForm] = useState(selected || { A: "", B: "", C: "" });
  const [saving, setSaving] = useState(false);
  useEffect(() => { if (selected) setForm(selected); }, [rowNumber]);
  const submit = async (event) => { event.preventDefault(); setSaving(true); try { await onSave(selected.row, form); onClose(); } finally { setSaving(false); } };
  return <div className="backdrop" role="presentation"><form className="modal" onSubmit={submit}><h2>Edit a row</h2><label>Row<select aria-label="Select row" value={rowNumber} onChange={(e) => setRowNumber(e.target.value)}>{rows.map((row) => <option key={row.row} value={row.row}>Row {row.row}</option>)}</select></label>{["A", "B", "C"].map((field) => <label key={field}>{field}<input value={form[field]} maxLength="1000" onChange={(e) => setForm({ ...form, [field]: e.target.value })} required /></label>)}<div className="actions"><button type="button" className="secondary" onClick={onClose} disabled={saving}>Cancel</button><button disabled={saving}>{saving ? "Saving…" : "Submit"}</button></div></form></div>;
}
