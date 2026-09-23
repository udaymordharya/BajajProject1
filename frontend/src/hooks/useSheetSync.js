import { useCallback, useEffect, useState } from "react";
import { fetchSheet, friendlyError, saveRow } from "../services/api";
import { createSocket } from "../services/socket";

export function useSheetSync() {
  const [rows, setRows] = useState([]); const [hash, setHash] = useState(""); const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [notice, setNotice] = useState(""); const [connected, setConnected] = useState(false); const [lastSynced, setLastSynced] = useState(null);
  const load = useCallback(async () => { try { const { data } = await fetchSheet(); setRows(data.data); setHash(data.hash); setLastSynced(new Date()); setError(""); } catch (err) { setError(friendlyError(err)); } finally { setLoading(false); } }, []);
  useEffect(() => { load(); const socket = createSocket(); socket.on("connect", () => setConnected(true)); socket.on("disconnect", () => setConnected(false)); socket.on("sheet_updated", (data) => { setRows(data); setLastSynced(new Date()); setNotice("✓ Synced"); }); return () => socket.close(); }, [load]);
  const update = async (row, values) => { try { const { data } = await saveRow(row, { ...values, expected_hash: hash }); setRows((items) => items.map((item) => item.row === row ? data.data : item)); setNotice("✓ Saved to Google Sheet"); setLastSynced(new Date()); setError(""); } catch (err) { setError(friendlyError(err)); if (err.response?.status === 409) await load(); throw err; } };
  return { rows, loading, error, notice, connected, lastSynced, update };
}
