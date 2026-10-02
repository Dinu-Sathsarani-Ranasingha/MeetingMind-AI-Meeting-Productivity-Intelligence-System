import { useState, useEffect, useCallback } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend
} from "recharts";

// ── Design Tokens ─────────────────────────────────────────────────────────────
const C = {
  navy:    "#0F1B2D",
  navyMid: "#162235",
  navyCard:"#1C2D42",
  border:  "#243550",
  purple:  "#7C5CFC",
  purpleL: "#9B7EFD",
  teal:    "#2ECFB4",
  amber:   "#F59E0B",
  red:     "#F87171",
  green:   "#34D399",
  textPri: "#F0F4FF",
  textSec: "#8CA0BB",
  textMut: "#4E6380",
};

const gradeColor = (score) => {
  if (score >= 80) return C.green;
  if (score >= 60) return C.teal;
  if (score >= 40) return C.amber;
  return C.red;
};

// ── Mock API (simulates the Phase 3 Flask backend) ────────────────────────────
const mockMeetings = [
  {
    meeting_id: "mtg_001", title: "Sprint 24 Planning", date: "2026-06-30",
    score: 92, grade: { label: "Excellent", color: "green" },
    action_item_count: 7, recurring_count: 0,
    summary: "This meeting scored 92/100 (Excellent). 7 action items identified. 6 have named owners and 5 have deadlines.",
    saved_at: "2026-06-30T09:30:00",
  },
  {
    meeting_id: "mtg_002", title: "Product Roadmap Review", date: "2026-06-25",
    score: 74, grade: { label: "Good", color: "teal" },
    action_item_count: 5, recurring_count: 1,
    summary: "This meeting scored 74/100 (Good). 5 action items identified. 3 have named owners.",
    saved_at: "2026-06-25T14:00:00",
  },
  {
    meeting_id: "mtg_003", title: "Engineering Standup", date: "2026-06-20",
    score: 48, grade: { label: "Fair", color: "amber" },
    action_item_count: 3, recurring_count: 2,
    summary: "This meeting scored 48/100 (Fair). 3 action items identified. 1 has a named owner.",
    saved_at: "2026-06-20T10:00:00",
  },
  {
    meeting_id: "mtg_004", title: "API Performance Review", date: "2026-06-15",
    score: 61, grade: { label: "Good", color: "teal" },
    action_item_count: 4, recurring_count: 1,
    summary: "This meeting scored 61/100 (Good). 4 action items identified.",
    saved_at: "2026-06-15T11:00:00",
  },
  {
    meeting_id: "mtg_005", title: "Stakeholder Sync", date: "2026-06-10",
    score: 35, grade: { label: "Poor", color: "red" },
    action_item_count: 2, recurring_count: 3,
    summary: "This meeting scored 35/100 (Poor). 2 action items identified.",
    saved_at: "2026-06-10T16:00:00",
  },
];

const mockAnalyzeResult = (text) => ({
  meeting_id: `mtg_${Date.now()}`,
  analyzed_at: new Date().toISOString(),
  word_count: text.split(" ").length,
  action_item_count: 6,
  score: {
    score: 88,
    grade: { label: "Excellent", color: "green" },
    breakdown: [
      { criterion: "Action items with named owners", points: 28, max: 30, note: "5/6 action items have named owners" },
      { criterion: "Decisions documented",           points: 25, max: 25, note: "4 distinct decision keywords found" },
      { criterion: "Deadlines assigned to tasks",    points: 20, max: 20, note: "4 action items have deadlines" },
      { criterion: "Clear agenda present",           points: 15, max: 15, note: "Meeting agenda is documented" },
      { criterion: "No recurring issues",            points:  0, max: 10, note: "Recurring issues detected from past meetings" },
    ],
  },
  action_items: [
    { task: "John will investigate the payment API timeout issue and prepare a fix.", owner: "John", deadline: "by Thursday", priority: "High",   completed: false },
    { task: "Sarah needs to update the Q3 roadmap document and share it with stakeholders.", owner: "Sarah", deadline: "by Friday", priority: "Medium", completed: false },
    { task: "Michael should schedule sprint planning meeting for next Monday.", owner: "Michael", deadline: "next Monday", priority: "Medium", completed: true  },
    { task: "The backend team must deploy the login hotfix to staging today.", owner: "Backend Team", deadline: "today", priority: "High",   completed: false },
    { task: "Lisa agreed to prepare the job description for the backend developer role.", owner: "Lisa", deadline: "end of this week", priority: "Medium", completed: false },
    { task: "Review and update the onboarding documentation before next sprint.", owner: null, deadline: null, priority: "Low", completed: false },
  ],
  recurring_issues: [
    { topic: "authentication", appearances: 4, last_seen: "2026-06-25", severity: "High" },
    { topic: "performance",    appearances: 3, last_seen: "2026-06-20", severity: "Medium" },
  ],
  summary: "This meeting scored 88/100 (Excellent). 6 action items identified. 5 have named owners and 4 have deadlines. ⚠ 2 recurring topic(s) flagged: 'authentication', 'performance'.",
  recurring_summary: "⚠ 2 recurring issue(s) detected in the last 30 days:\n  • 'authentication' appeared in 4 meetings (last seen: 2026-06-25) — High severity\n  • 'performance' appeared in 3 meetings (last seen: 2026-06-20) — Medium severity",
});

const trendData = [
  { date: "Jun 10", score: 35, title: "Stakeholder Sync" },
  { date: "Jun 15", score: 61, title: "API Review" },
  { date: "Jun 20", score: 48, title: "Standup" },
  { date: "Jun 25", score: 74, title: "Roadmap Review" },
  { date: "Jun 30", score: 92, title: "Sprint 24" },
];

const SAMPLE_NOTES = `Agenda: Sprint 24 Planning — Engineering Team
Date: 2026-06-30

Topics discussed:
1. Authentication service performance issues
2. Q3 feature roadmap finalisation
3. Team capacity for the upcoming sprint

Decisions:
The team agreed to prioritise fixing the authentication timeout before any new feature work.
It was confirmed that the Q3 roadmap will be shared with stakeholders by Friday.
Leadership approved hiring one additional backend developer.

Action Items:
- John will investigate the payment API timeout issue and prepare a fix by Thursday.
- Sarah needs to update the Q3 roadmap document and share it with stakeholders by Friday.
- Michael should schedule the sprint planning meeting for next Monday.
- The backend team must deploy the login hotfix to staging today.
- Lisa agreed to prepare the job description for the backend developer role by end of this week.

Next meeting: Monday 9am — Sprint 24 kickoff`;

// ── Components ────────────────────────────────────────────────────────────────

function ScoreBadge({ score, size = "md" }) {
  const color = gradeColor(score);
  const sz = size === "lg" ? { width: 72, height: 72, fontSize: 22, ring: 5 }
           : size === "sm" ? { width: 40, height: 40, fontSize: 13, ring: 3 }
           : { width: 52, height: 52, fontSize: 16, ring: 4 };
  const pct = score / 100;
  const r = (sz.width / 2) - sz.ring - 2;
  const circ = 2 * Math.PI * r;
  return (
    <div style={{ position: "relative", width: sz.width, height: sz.height, flexShrink: 0 }}>
      <svg width={sz.width} height={sz.height} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={sz.width/2} cy={sz.height/2} r={r} fill="none" stroke={C.border} strokeWidth={sz.ring} />
        <circle cx={sz.width/2} cy={sz.height/2} r={r} fill="none" stroke={color} strokeWidth={sz.ring}
          strokeDasharray={circ} strokeDashoffset={circ * (1 - pct)} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.8s ease" }} />
      </svg>
      <div style={{ position:"absolute", inset:0, display:"flex", alignItems:"center", justifyContent:"center",
        fontSize: sz.fontSize, fontWeight: 700, color, fontFamily: "monospace" }}>{score}</div>
    </div>
  );
}

function StatCard({ icon, label, value, sub, color = C.purple }) {
  return (
    <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12,
      padding: "18px 20px", display: "flex", alignItems: "center", gap: 14 }}>
      <div style={{ width: 44, height: 44, borderRadius: 10, background: `${color}22`,
        display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, flexShrink: 0 }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: 11, color: C.textSec, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 2 }}>{label}</div>
        <div style={{ fontSize: 22, fontWeight: 700, color: C.textPri, lineHeight: 1 }}>{value}</div>
        {sub && <div style={{ fontSize: 11, color: C.textMut, marginTop: 3 }}>{sub}</div>}
      </div>
    </div>
  );
}

function PriorityBadge({ priority }) {
  const cfg = { High: { bg: "#F8717122", color: C.red }, Medium: { bg: "#F59E0B22", color: C.amber }, Low: { bg: "#34D39922", color: C.green } };
  const { bg, color } = cfg[priority] || cfg.Medium;
  return <span style={{ background: bg, color, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>{priority}</span>;
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button onClick={onClick} style={{ display: "flex", alignItems: "center", gap: 10, width: "100%",
      padding: "10px 14px", borderRadius: 8, border: "none", cursor: "pointer", textAlign: "left",
      background: active ? `${C.purple}22` : "transparent",
      color: active ? C.purple : C.textSec,
      fontWeight: active ? 600 : 400, fontSize: 14, transition: "all 0.15s" }}>
      <span style={{ fontSize: 18 }}>{icon}</span>{label}
      {active && <div style={{ marginLeft: "auto", width: 3, height: 18, borderRadius: 2, background: C.purple }} />}
    </button>
  );
}

// ── Screens ───────────────────────────────────────────────────────────────────

function DashboardScreen() {
  const scores = mockMeetings.map(m => m.score);
  const avg = Math.round(scores.reduce((a,b) => a+b, 0) / scores.length);
  const totalActions = mockMeetings.reduce((a, m) => a + m.action_item_count, 0);
  const totalRecurring = mockMeetings.reduce((a, m) => a + m.recurring_count, 0);

  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    return <circle cx={cx} cy={cy} r={5} fill={gradeColor(payload.score)} stroke={C.navy} strokeWidth={2} />;
  };

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 8, padding: "10px 14px" }}>
        <div style={{ color: C.textPri, fontWeight: 600, fontSize: 13 }}>{d.title}</div>
        <div style={{ color: gradeColor(d.score), fontSize: 20, fontWeight: 700 }}>{d.score}<span style={{ fontSize: 12, color: C.textSec }}>/100</span></div>
        <div style={{ color: C.textSec, fontSize: 11 }}>{d.date}</div>
      </div>
    );
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ color: C.textPri, fontSize: 22, fontWeight: 700, margin: 0 }}>Team Overview</h2>
        <p style={{ color: C.textSec, fontSize: 13, margin: "4px 0 0" }}>Engineering team · Last 30 days</p>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 14, marginBottom: 24 }}>
        <StatCard icon="📊" label="Avg Score"         value={`${avg}/100`}   sub="↑ 12 pts this month"   color={C.purple} />
        <StatCard icon="✅" label="Meetings Analyzed"  value={mockMeetings.length} sub="Last 30 days"    color={C.teal}   />
        <StatCard icon="📋" label="Action Items"       value={totalActions}   sub="Across all meetings"  color={C.amber}  />
        <StatCard icon="⚠️" label="Recurring Issues"   value={totalRecurring} sub="Topics to resolve"    color={C.red}    />
      </div>

      {/* Score trend chart */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 20 }}>
        <h3 style={{ color: C.textPri, margin: "0 0 18px", fontSize: 15, fontWeight: 600 }}>Meeting Score Trend</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={trendData} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
            <XAxis dataKey="date" tick={{ fill: C.textSec, fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fill: C.textSec, fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="score" stroke={C.purple} strokeWidth={2.5} dot={<CustomDot />} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Recent meetings */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
        <h3 style={{ color: C.textPri, margin: "0 0 16px", fontSize: 15, fontWeight: 600 }}>Recent Meetings</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {mockMeetings.slice(0, 4).map(m => (
            <div key={m.meeting_id} style={{ display: "flex", alignItems: "center", gap: 14,
              padding: "12px 14px", background: C.navy, borderRadius: 8, border: `1px solid ${C.border}` }}>
              <ScoreBadge score={m.score} size="sm" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ color: C.textPri, fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{m.title}</div>
                <div style={{ color: C.textSec, fontSize: 11 }}>{m.date} · {m.action_item_count} actions · {m.grade.label}</div>
              </div>
              {m.recurring_count > 0 && (
                <span style={{ background: `${C.red}22`, color: C.red, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600, whiteSpace: "nowrap" }}>
                  {m.recurring_count} recurring
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AnalyzeScreen({ onAnalyzed }) {
  const [text, setText] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = () => {
    if (!text.trim()) return;
    setLoading(true);
    setTimeout(() => {
      setResult(mockAnalyzeResult(text));
      setLoading(false);
    }, 1800);
  };

  const handleSave = () => {
    if (result) { onAnalyzed(result, title || "Untitled Meeting"); }
  };

  if (result) return <AnalysisResultScreen result={result} title={title} onSave={handleSave} onBack={() => setResult(null)} />;

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ color: C.textPri, fontSize: 22, fontWeight: 700, margin: 0 }}>Analyze Meeting</h2>
        <p style={{ color: C.textSec, fontSize: 13, margin: "4px 0 0" }}>Paste your meeting notes and get instant AI analysis</p>
      </div>

      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
        <label style={{ display: "block", color: C.textSec, fontSize: 12, fontWeight: 600, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>Meeting Title</label>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Sprint 24 Planning"
          style={{ width: "100%", background: C.navy, border: `1px solid ${C.border}`, borderRadius: 8,
            padding: "10px 14px", color: C.textPri, fontSize: 14, outline: "none", boxSizing: "border-box",
            fontFamily: "inherit" }} />
      </div>

      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <label style={{ color: C.textSec, fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>Meeting Notes</label>
          <button onClick={() => setText(SAMPLE_NOTES)} style={{ background: `${C.purple}22`, color: C.purpleL,
            border: "none", borderRadius: 6, padding: "4px 10px", fontSize: 11, cursor: "pointer", fontFamily: "inherit" }}>
            Load sample notes
          </button>
        </div>
        <textarea value={text} onChange={e => setText(e.target.value)}
          placeholder="Paste your meeting notes here — include action items, decisions made, agenda topics..."
          rows={12} style={{ width: "100%", background: C.navy, border: `1px solid ${C.border}`, borderRadius: 8,
            padding: "12px 14px", color: C.textPri, fontSize: 13, outline: "none", resize: "vertical",
            lineHeight: 1.6, fontFamily: "inherit", boxSizing: "border-box" }} />
        <div style={{ textAlign: "right", color: C.textMut, fontSize: 11, marginTop: 6 }}>{text.split(/\s+/).filter(Boolean).length} words</div>
      </div>

      <button onClick={handleAnalyze} disabled={!text.trim() || loading}
        style={{ width: "100%", padding: "14px", background: text.trim() && !loading ? C.purple : C.border,
          color: C.textPri, border: "none", borderRadius: 10, fontSize: 15, fontWeight: 600,
          cursor: text.trim() && !loading ? "pointer" : "not-allowed", fontFamily: "inherit", transition: "background 0.2s" }}>
        {loading ? "🧠 Analyzing..." : "⚡ Analyze Meeting"}
      </button>
    </div>
  );
}

function AnalysisResultScreen({ result, title, onSave, onBack }) {
  const [saved, setSaved] = useState(false);
  const { score, action_items, recurring_issues, summary, breakdown } = result;

  const handleSave = () => { onSave(); setSaved(true); };

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <button onClick={onBack} style={{ background: C.navyCard, border: `1px solid ${C.border}`, color: C.textSec,
          borderRadius: 8, padding: "6px 12px", cursor: "pointer", fontSize: 13, fontFamily: "inherit" }}>← Back</button>
        <div>
          <h2 style={{ color: C.textPri, fontSize: 20, fontWeight: 700, margin: 0 }}>{title || "Analysis Result"}</h2>
          <p style={{ color: C.textSec, fontSize: 12, margin: "2px 0 0" }}>{result.word_count} words · {result.action_item_count} action items</p>
        </div>
        <button onClick={handleSave} disabled={saved}
          style={{ marginLeft: "auto", background: saved ? `${C.green}22` : C.purple, color: saved ? C.green : "#fff",
            border: "none", borderRadius: 8, padding: "8px 16px", cursor: saved ? "default" : "pointer",
            fontSize: 13, fontWeight: 600, fontFamily: "inherit" }}>
          {saved ? "✓ Saved" : "Save Meeting"}
        </button>
      </div>

      {/* Score overview */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 16,
        display: "flex", alignItems: "center", gap: 20 }}>
        <ScoreBadge score={score.score} size="lg" />
        <div style={{ flex: 1 }}>
          <div style={{ color: C.textPri, fontWeight: 700, fontSize: 18 }}>
            {score.grade.label} Meeting
          </div>
          <div style={{ color: C.textSec, fontSize: 13, lineHeight: 1.5, marginTop: 4 }}>{summary}</div>
        </div>
      </div>

      {/* Score breakdown */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
        <h3 style={{ color: C.textPri, margin: "0 0 16px", fontSize: 15, fontWeight: 600 }}>Score Breakdown</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {score.breakdown.map((b, i) => (
            <div key={i}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                <span style={{ color: C.textSec, fontSize: 13 }}>{b.criterion}</span>
                <span style={{ color: gradeColor((b.points/b.max)*100), fontWeight: 700, fontSize: 13, fontFamily: "monospace" }}>{b.points}/{b.max}</span>
              </div>
              <div style={{ height: 6, background: C.border, borderRadius: 3, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${(b.points/b.max)*100}%`, background: gradeColor((b.points/b.max)*100),
                  borderRadius: 3, transition: "width 0.8s ease" }} />
              </div>
              <div style={{ color: C.textMut, fontSize: 11, marginTop: 3 }}>{b.note}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Action items */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 16 }}>
        <h3 style={{ color: C.textPri, margin: "0 0 16px", fontSize: 15, fontWeight: 600 }}>Action Items ({action_items.length})</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {action_items.map((item, i) => (
            <div key={i} style={{ background: C.navy, border: `1px solid ${C.border}`, borderRadius: 8,
              padding: "12px 14px", display: "flex", gap: 12, alignItems: "flex-start" }}>
              <div style={{ width: 18, height: 18, borderRadius: 4, border: `2px solid ${item.completed ? C.green : C.border}`,
                background: item.completed ? `${C.green}22` : "transparent", marginTop: 1, flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center" }}>
                {item.completed && <span style={{ color: C.green, fontSize: 11 }}>✓</span>}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ color: item.completed ? C.textMut : C.textPri, fontSize: 13, lineHeight: 1.5,
                  textDecoration: item.completed ? "line-through" : "none" }}>{item.task}</div>
                <div style={{ display: "flex", gap: 8, marginTop: 6, flexWrap: "wrap", alignItems: "center" }}>
                  <PriorityBadge priority={item.priority} />
                  {item.owner && <span style={{ color: C.teal, fontSize: 11 }}>👤 {item.owner}</span>}
                  {item.deadline && <span style={{ color: C.amber, fontSize: 11 }}>📅 {item.deadline}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recurring issues */}
      {recurring_issues.length > 0 && (
        <div style={{ background: `${C.red}11`, border: `1px solid ${C.red}44`, borderRadius: 12, padding: 20 }}>
          <h3 style={{ color: C.red, margin: "0 0 12px", fontSize: 15, fontWeight: 600 }}>⚠ Recurring Issues Detected</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {recurring_issues.map((issue, i) => (
              <div key={i} style={{ background: C.navy, border: `1px solid ${C.border}`, borderRadius: 8, padding: "10px 14px",
                display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <span style={{ color: C.textPri, fontWeight: 600, fontSize: 13 }}>"{issue.topic}"</span>
                  <span style={{ color: C.textSec, fontSize: 12, marginLeft: 8 }}>appeared in {issue.appearances} meetings</span>
                </div>
                <span style={{ background: issue.severity === "High" ? `${C.red}22` : `${C.amber}22`,
                  color: issue.severity === "High" ? C.red : C.amber,
                  borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>
                  {issue.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MeetingsScreen() {
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h2 style={{ color: C.textPri, fontSize: 22, fontWeight: 700, margin: 0 }}>Meeting History</h2>
          <p style={{ color: C.textSec, fontSize: 13, margin: "4px 0 0" }}>{mockMeetings.length} meetings analyzed</p>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {mockMeetings.map(m => (
          <div key={m.meeting_id} style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 18 }}>
            <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
              <ScoreBadge score={m.score} size="md" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8, flexWrap: "wrap" }}>
                  <div style={{ color: C.textPri, fontWeight: 600, fontSize: 15 }}>{m.title}</div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <span style={{ background: `${gradeColor(m.score)}22`, color: gradeColor(m.score),
                      borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>{m.grade.label}</span>
                    {m.recurring_count > 0 && (
                      <span style={{ background: `${C.red}22`, color: C.red, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>
                        {m.recurring_count} recurring
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ color: C.textSec, fontSize: 12, margin: "4px 0 8px" }}>{m.date} · {m.action_item_count} action items</div>
                <div style={{ color: C.textMut, fontSize: 12, lineHeight: 1.5 }}>{m.summary}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalyticsScreen() {
  const byPriority = [
    { name: "High",   value: 6, color: C.red   },
    { name: "Medium", value: 14, color: C.amber },
    { name: "Low",    value: 5, color: C.green  },
  ];
  const byOwner = [
    { name: "John",         tasks: 5 },
    { name: "Sarah",        tasks: 4 },
    { name: "Michael",      tasks: 4 },
    { name: "Lisa",         tasks: 3 },
    { name: "Unassigned",   tasks: 9 },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ color: C.textPri, fontSize: 22, fontWeight: 700, margin: 0 }}>Analytics</h2>
        <p style={{ color: C.textSec, fontSize: 13, margin: "4px 0 0" }}>Team productivity insights · Last 30 days</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16, marginBottom: 20 }}>
        {/* Action items by priority */}
        <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
          <h3 style={{ color: C.textPri, margin: "0 0 16px", fontSize: 14, fontWeight: 600 }}>Actions by Priority</h3>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={byPriority} cx="50%" cy="50%" innerRadius={40} outerRadius={65} paddingAngle={4} dataKey="value">
                {byPriority.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 8, color: C.textPri }} />
              <Legend iconType="circle" iconSize={8} formatter={(v) => <span style={{ color: C.textSec, fontSize: 11 }}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Tasks per owner */}
        <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
          <h3 style={{ color: C.textPri, margin: "0 0 16px", fontSize: 14, fontWeight: 600 }}>Actions by Owner</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={byOwner} layout="vertical" margin={{ left: 0, right: 10 }}>
              <XAxis type="number" tick={{ fill: C.textSec, fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fill: C.textSec, fontSize: 11 }} axisLine={false} tickLine={false} width={70} />
              <Tooltip contentStyle={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 8, color: C.textPri }} />
              <Bar dataKey="tasks" fill={C.purple} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recurring issues tracker */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, marginBottom: 20 }}>
        <h3 style={{ color: C.textPri, margin: "0 0 16px", fontSize: 15, fontWeight: 600 }}>Top Recurring Issues</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { topic: "authentication", appearances: 4, severity: "High",   last_seen: "2026-06-25" },
            { topic: "performance",    appearances: 3, severity: "Medium",  last_seen: "2026-06-20" },
            { topic: "deployment",     appearances: 3, severity: "Medium",  last_seen: "2026-06-15" },
          ].map((issue, i) => (
            <div key={i} style={{ background: C.navy, borderRadius: 8, border: `1px solid ${C.border}`,
              padding: "12px 14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span style={{ color: C.textPri, fontWeight: 600, fontSize: 13 }}>"{issue.topic}"</span>
                <span style={{ color: C.textSec, fontSize: 12, marginLeft: 10 }}>
                  Appeared {issue.appearances}× · Last: {issue.last_seen}
                </span>
              </div>
              <span style={{ background: issue.severity === "High" ? `${C.red}22` : `${C.amber}22`,
                color: issue.severity === "High" ? C.red : C.amber,
                borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600 }}>{issue.severity}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Score distribution */}
      <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
        <h3 style={{ color: C.textPri, margin: "0 0 4px", fontSize: 15, fontWeight: 600 }}>Score Distribution</h3>
        <p style={{ color: C.textSec, fontSize: 12, margin: "0 0 16px" }}>Percentage of meetings in each grade band</p>
        {[
          { label: "Excellent (80–100)", count: 1, pct: 20, color: C.green  },
          { label: "Good (60–79)",       count: 2, pct: 40, color: C.teal   },
          { label: "Fair (40–59)",       count: 1, pct: 20, color: C.amber  },
          { label: "Poor (0–39)",        count: 1, pct: 20, color: C.red    },
        ].map((b, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
              <span style={{ color: C.textSec, fontSize: 12 }}>{b.label}</span>
              <span style={{ color: b.color, fontWeight: 700, fontSize: 12, fontFamily: "monospace" }}>{b.count} meetings ({b.pct}%)</span>
            </div>
            <div style={{ height: 6, background: C.border, borderRadius: 3 }}>
              <div style={{ height: "100%", width: `${b.pct}%`, background: b.color, borderRadius: 3 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────

export default function App() {
  const [screen, setScreen] = useState("dashboard");
  const [savedMeetings, setSavedMeetings] = useState([]);

  const handleAnalyzed = (result, title) => {
    setSavedMeetings(prev => [{ ...result, title, saved_at: new Date().toISOString() }, ...prev]);
  };

  const screens = {
    dashboard: <DashboardScreen />,
    analyze:   <AnalyzeScreen onAnalyzed={handleAnalyzed} />,
    meetings:  <MeetingsScreen />,
    analytics: <AnalyticsScreen />,
  };

  return (
    <div style={{ display: "flex", height: "100vh", background: C.navy, color: C.textPri, fontFamily: "'Inter', 'Segoe UI', sans-serif", overflow: "hidden" }}>
      {/* Sidebar */}
      <div style={{ width: 220, background: C.navyMid, borderRight: `1px solid ${C.border}`,
        display: "flex", flexDirection: "column", padding: "20px 12px", flexShrink: 0 }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "4px 10px", marginBottom: 28 }}>
          <div style={{ width: 34, height: 34, borderRadius: 8, background: `linear-gradient(135deg, ${C.purple}, ${C.teal})`,
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🧠</div>
          <div>
            <div style={{ color: C.textPri, fontWeight: 700, fontSize: 15, lineHeight: 1 }}>MeetingMind</div>
            <div style={{ color: C.textMut, fontSize: 10, marginTop: 2 }}>AI Productivity</div>
          </div>
        </div>

        {/* Nav */}
        <div style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
          <NavItem icon="📊" label="Dashboard"  active={screen === "dashboard"} onClick={() => setScreen("dashboard")} />
          <NavItem icon="⚡" label="Analyze"    active={screen === "analyze"}   onClick={() => setScreen("analyze")}   />
          <NavItem icon="📁" label="Meetings"   active={screen === "meetings"}  onClick={() => setScreen("meetings")}  />
          <NavItem icon="📈" label="Analytics"  active={screen === "analytics"} onClick={() => setScreen("analytics")} />
        </div>

        {/* User pill */}
        <div style={{ background: C.navyCard, border: `1px solid ${C.border}`, borderRadius: 10, padding: "10px 12px",
          display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 30, height: 30, borderRadius: "50%",
            background: `linear-gradient(135deg, ${C.purple}, ${C.teal})`,
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, flexShrink: 0 }}>D</div>
          <div>
            <div style={{ color: C.textPri, fontSize: 12, fontWeight: 600 }}>Dinu</div>
            <div style={{ color: C.textMut, fontSize: 10 }}>Engineering Manager</div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, overflowY: "auto", padding: "28px 28px" }}>
        <div style={{ maxWidth: 820, margin: "0 auto" }}>
          {screens[screen]}
        </div>
      </div>
    </div>
  );
}
