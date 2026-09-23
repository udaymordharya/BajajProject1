export default function DataTable({ rows }) {
  return <div className="table-wrap"><table><thead><tr><th>A</th><th>B</th><th>C</th></tr></thead><tbody>{rows.map((row) => <tr key={row.row}><td>{row.A}</td><td>{row.B}</td><td>{row.C}</td></tr>)}</tbody></table></div>;
}
