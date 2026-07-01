import { useState } from "react";

const API = "http://localhost:8000";

const SCORE_COLORS = {
  Hot: "#e8452b",
  Warm: "#f0a020",
  Cold: "#3b82c4",
};

export default function App() {
  const [lead, setLead] = useState({
    name: "", email: "", phone: "",
    property_interest: "", message: "", source: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [decisions, setDecisions] = useState([]);
  const [override, setOverride] = useState("");

  const update = (k) => (e) => setLead({ ...lead, [k]: e.target.value });

  async function qualify() {
    setLoading(true);
    setResult(null);
    setOverride("");
    try {
      const res = await fetch(`${API}/qualify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setResult({ lead_score: "ERROR", qualification_reason: String(e) });
    }
    setLoading(false);
  }

  function record(finalScore, wasOverridden) {
    setDecisions([
      {
        name: lead.name || "(no name)",
        ai: result.lead_score,
        final: finalScore,
        overridden: wasOverridden,
      },
      ...decisions,
    ]);
    setResult(null);
    setLead({ name: "", email: "", phone: "", property_interest: "", message: "", source: "" });
  }

  const lowConfidence =
    result &&
    (result.confidence?.toLowerCase() === "low" ||
      result.lead_score === "ERROR");

  return (
    <div style={s.page}>
      <header style={s.header}>
        <h1 style={s.h1}>AI Lead Qualifier</h1>
        <p style={s.sub}>
          Decision support with human-in-the-loop review and escalation
        </p>
      </header>

      <div style={s.grid}>
        {/* ---- Input ---- */}
        <div style={s.card}>
          <h2 style={s.h2}>New lead</h2>
          {["name", "email", "phone", "property_interest", "source"].map((f) => (
            <input
              key={f}
              placeholder={f.replace("_", " ")}
              value={lead[f]}
              onChange={update(f)}
              style={s.input}
            />
          ))}
          <textarea
            placeholder="message"
            value={lead.message}
            onChange={update("message")}
            style={{ ...s.input, height: 90 }}
          />
          <button onClick={qualify} disabled={loading} style={s.primaryBtn}>
            {loading ? "Qualifying..." : "Qualify lead"}
          </button>
        </div>

        {/* ---- Result + human-in-the-loop ---- */}
        <div style={s.card}>
          <h2 style={s.h2}>AI recommendation</h2>
          {!result && <p style={s.muted}>Submit a lead to see the AI's assessment.</p>}

          {result && (
            <>
              <div
                style={{
                  ...s.scorePill,
                  background: SCORE_COLORS[result.lead_score] || "#666",
                }}
              >
                {result.lead_score}
                {result.confidence && (
                  <span style={s.conf}>confidence: {result.confidence}</span>
                )}
              </div>

              <p style={s.label}>Why</p>
              <p style={s.reason}>{result.qualification_reason}</p>

              {result.suggested_next_action && (
                <>
                  <p style={s.label}>Suggested next action</p>
                  <p style={s.reason}>{result.suggested_next_action}</p>
                </>
              )}

              {lowConfidence && (
                <div style={s.escalate}>
                  ⚠️ Low confidence — recommend escalating to a manager before acting.
                </div>
              )}

              {/* Human-in-the-loop */}
              <div style={s.hitl}>
                <p style={s.label}>Your review</p>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button
                    onClick={() => record(result.lead_score, false)}
                    style={s.acceptBtn}
                  >
                    ✓ Accept AI score
                  </button>
                  <select
                    value={override}
                    onChange={(e) => setOverride(e.target.value)}
                    style={s.select}
                  >
                    <option value="">Override to…</option>
                    <option value="Hot">Hot</option>
                    <option value="Warm">Warm</option>
                    <option value="Cold">Cold</option>
                  </select>
                  {override && (
                    <button onClick={() => record(override, true)} style={s.overrideBtn}>
                      Save override
                    </button>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ---- Decision log / review queue ---- */}
      {decisions.length > 0 && (
        <div style={{ ...s.card, marginTop: 20 }}>
          <h2 style={s.h2}>Decision log</h2>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>Lead</th>
                <th style={s.th}>AI score</th>
                <th style={s.th}>Final</th>
                <th style={s.th}>Reviewed</th>
              </tr>
            </thead>
            <tbody>
              {decisions.map((d, i) => (
                <tr key={i}>
                  <td style={s.td}>{d.name}</td>
                  <td style={s.td}>{d.ai}</td>
                  <td style={s.td}>{d.final}</td>
                  <td style={s.td}>{d.overridden ? "Overridden" : "Accepted"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const s = {
  page: { maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif", color: "#1a1a1a" },
  header: { marginBottom: 20 },
  h1: { margin: 0, fontSize: 26 },
  sub: { margin: "4px 0 0", color: "#666", fontSize: 14 },
  grid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 },
  card: { border: "1px solid #e2e2e2", borderRadius: 10, padding: 18, background: "#fff" },
  h2: { fontSize: 16, marginTop: 0, color: "#1a1a1a" },
  input: { width: "100%", padding: 9, marginBottom: 8, border: "1px solid #ccc", borderRadius: 6, boxSizing: "border-box", fontSize: 14 },
  primaryBtn: { width: "100%", padding: 11, background: "#1a1a1a", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 14, fontWeight: 600 },
  muted: { color: "#999", fontSize: 14 },
  scorePill: { display: "inline-flex", alignItems: "center", gap: 10, color: "#fff", padding: "6px 14px", borderRadius: 20, fontWeight: 700, fontSize: 15 },
  conf: { fontSize: 11, fontWeight: 500, opacity: 0.9 },
  label: { fontSize: 12, textTransform: "uppercase", letterSpacing: 0.5, color: "#888", margin: "14px 0 2px" },
  reason: { margin: 0, fontSize: 14, lineHeight: 1.4 },
  escalate: { marginTop: 14, padding: 10, background: "#fff4e5", border: "1px solid #f0a020", borderRadius: 6, fontSize: 13 },
  hitl: { marginTop: 16, paddingTop: 14, borderTop: "1px solid #eee" },
  acceptBtn: { padding: "8px 14px", background: "#2e7d32", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 13 },
  overrideBtn: { padding: "8px 14px", background: "#e8452b", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 13 },
  select: { padding: "8px 10px", border: "1px solid #ccc", borderRadius: 6, fontSize: 13 },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 13 },
  th: { textAlign: "left", padding: 8, borderBottom: "2px solid #eee", color: "#666" },
  td: { padding: 8, borderBottom: "1px solid #f0f0f0" },
};
