export default function SyncStatus({ connected, lastSynced, notice }) {
  return <div className="sync-status"><span className={connected ? "dot online" : "dot"} /> {connected ? "Connected" : "Disconnected"}<span className="sync-time">Last synchronized: {lastSynced ? lastSynced.toLocaleTimeString() : "—"}</span>{notice && <span className="notice">{notice}</span>}</div>;
}
