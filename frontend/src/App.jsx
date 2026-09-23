import { useState } from "react";
import DataTable from "./components/DataTable";
import EditRowModal from "./components/EditRowModal";
import LoadingState from "./components/LoadingState";
import SyncStatus from "./components/SyncStatus";
import { useSheetSync } from "./hooks/useSheetSync";
import "./App.css";

export default function App() {
  const [editing, setEditing] = useState(false); const sync = useSheetSync();
  return <main><section className="card"><p className="eyebrow">BAJAJ EARTH REAL-TIME-DATA</p><h1>Google Sheet Sync</h1><SyncStatus connected={sync.connected} lastSynced={sync.lastSynced} notice={sync.notice} />{sync.error && <div className="error" role="alert">{sync.error}</div>}{sync.loading ? <LoadingState /> : <><DataTable rows={sync.rows} /><button className="edit" onClick={() => setEditing(true)} disabled={!sync.rows.length}>Edit rows</button></>}{editing && <EditRowModal rows={sync.rows} onClose={() => setEditing(false)} onSave={sync.update} />}</section></main>;
}
