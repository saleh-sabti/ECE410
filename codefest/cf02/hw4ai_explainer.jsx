import { useState } from "react";

const chapters = [
  { id: "computation", title: "1. What is Computation?", emoji: "🧠" },
  { id: "cpu", title: "2. How a CPU Works", emoji: "⚙️" },
  { id: "mac", title: "3. The MAC — One Operation Rules AI", emoji: "✖️" },
  { id: "whyhw", title: "4. Why HW Beats SW for AI", emoji: "🚀" },
  { id: "hwsw", title: "5. HW vs SW — What Are We Actually Building?", emoji: "🔧" },
  { id: "chiplet", title: "6. Chiplets & Accelerators", emoji: "🔲" },
  { id: "echo", title: "7. Your Project: Echo Detection Chiplet", emoji: "🎯" },
];

const colors = {
  blue: "#2563eb",
  orange: "#ea580c",
  green: "#16a34a",
  purple: "#7c3aed",
  gray: "#374151",
  lightBlue: "#dbeafe",
  lightOrange: "#ffedd5",
  lightGreen: "#dcfce7",
  lightPurple: "#ede9fe",
  lightGray: "#f3f4f6",
};

function Card({ color = "lightBlue", children, style = {} }) {
  return (
    <div style={{
      background: colors[color],
      borderRadius: 12,
      padding: "16px 20px",
      marginBottom: 14,
      ...style
    }}>
      {children}
    </div>
  );
}

function Highlight({ color = "blue", children }) {
  return (
    <span style={{
      background: colors["light" + color.charAt(0).toUpperCase() + color.slice(1)] || "#dbeafe",
      color: colors[color],
      fontWeight: 700,
      padding: "2px 8px",
      borderRadius: 6,
      fontSize: 15,
    }}>
      {children}
    </span>
  );
}

function SectionTitle({ children }) {
  return <h2 style={{ fontSize: 22, fontWeight: 800, color: colors.gray, marginBottom: 8, marginTop: 0 }}>{children}</h2>;
}

function Para({ children }) {
  return <p style={{ fontSize: 16, lineHeight: 1.7, color: "#374151", margin: "0 0 12px 0" }}>{children}</p>;
}

// ─── CHAPTER 1: COMPUTATION ───────────────────────────────────────────────────
function ChapterComputation() {
  const [revealed, setRevealed] = useState(false);
  return (
    <div>
      <SectionTitle>What is Computation?</SectionTitle>
      <Para>
        Before anything else — hardware, software, chiplets — your professor is asking one fundamental question: <strong>how do you turn inputs into outputs?</strong>
      </Para>
      <Para>
        That's it. Every computer, every phone, every AI chip is just answering that question in a different way.
      </Para>

      <Card color="lightBlue">
        <div style={{ textAlign: "center", fontSize: 15, fontWeight: 600, color: colors.gray, marginBottom: 12 }}>
          The Universal Model of Computation
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16, flexWrap: "wrap" }}>
          <div style={{ background: "#bfdbfe", borderRadius: 10, padding: "12px 18px", textAlign: "center", minWidth: 110 }}>
            <div style={{ fontSize: 22 }}>🎤</div>
            <div style={{ fontWeight: 700, color: colors.blue }}>Inputs</div>
            <div style={{ fontSize: 12, color: "#555" }}>audio, pixels, sensor data…</div>
          </div>
          <div style={{ fontSize: 28, color: colors.gray }}>→</div>
          <div style={{ background: colors.gray, borderRadius: 10, padding: "12px 18px", textAlign: "center", color: "white", minWidth: 130 }}>
            <div style={{ fontSize: 22 }}>📦</div>
            <div style={{ fontWeight: 700 }}>Some Function</div>
            <div style={{ fontSize: 12, color: "#ccc" }}>O = f(I)</div>
          </div>
          <div style={{ fontSize: 28, color: colors.gray }}>→</div>
          <div style={{ background: "#bbf7d0", borderRadius: 10, padding: "12px 18px", textAlign: "center", minWidth: 110 }}>
            <div style={{ fontSize: 22 }}>📊</div>
            <div style={{ fontWeight: 700, color: colors.green }}>Outputs</div>
            <div style={{ fontSize: 12, color: "#555" }}>1 bit, a label, a score…</div>
          </div>
        </div>
      </Card>

      <Para>
        The question your whole course is about is: <strong>what goes inside that box?</strong> You have options:
      </Para>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
        {[
          { label: "A CPU running code", icon: "💻", desc: "Flexible, can do anything. Slow for repetitive math." },
          { label: "A GPU", icon: "🖥️", desc: "Parallel, great at doing thousands of multiplications at once." },
          { label: "A custom chip (ASIC/chiplet)", icon: "🔲", desc: "Does ONE thing. Insanely fast at that one thing. Nothing else." },
        ].map(opt => (
          <div key={opt.label} style={{ background: colors.lightGray, borderRadius: 10, padding: 14, flex: "1 1 150px", minWidth: 150 }}>
            <div style={{ fontSize: 24, marginBottom: 4 }}>{opt.icon}</div>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{opt.label}</div>
            <div style={{ fontSize: 13, color: "#555" }}>{opt.desc}</div>
          </div>
        ))}
      </div>

      <button
        onClick={() => setRevealed(!revealed)}
        style={{ background: colors.blue, color: "white", border: "none", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontWeight: 700, fontSize: 15, marginBottom: 12 }}
      >
        {revealed ? "Hide" : "So where does your echo chiplet fit? →"}
      </button>
      {revealed && (
        <Card color="lightGreen">
          <strong>Your echo detection chiplet is option 3 — a custom chip.</strong>
          <p style={{ margin: "8px 0 0", fontSize: 15, lineHeight: 1.6 }}>
            Your inputs are two audio streams (far-end reference + near-end mic). Your function is normalized cross-correlation. Your output is 1 bit: echo present or not. You're designing the thing that goes in that box — in hardware.
          </p>
        </Card>
      )}
    </div>
  );
}

// ─── CHAPTER 2: CPU ───────────────────────────────────────────────────────────
function ChapterCPU() {
  const [step, setStep] = useState(0);
  const steps = [
    { title: "The CPU: The Universal Machine", content: "A CPU can run any code — Excel, games, your Python script, an OS. That flexibility is exactly why it exists. But flexibility has a cost.", icon: "💻" },
    { title: "How a CPU actually works", content: "A CPU has four main parts: Control Unit (reads instructions, decides what to do), ALU (the calculator — adds, multiplies), Registers (tiny fast storage right on chip), and Memory (RAM — big but slow).", icon: "⚙️" },
    { title: "The problem: sequential execution", content: "A CPU does one instruction at a time. To compute ref[0]×mic[0] + ref[1]×mic[1] + ... it has to do each multiplication, then each addition, one after another. For N=128 samples that's 384 steps minimum.", icon: "🐢" },
    { title: "The memory bottleneck", content: "Every time the CPU needs a number it doesn't already have, it goes to RAM. RAM is physically far away and slow — it can take 100-200 CPU cycles just waiting for data to arrive. This is the main bottleneck for AI workloads.", icon: "🚧" },
  ];
  return (
    <div>
      <SectionTitle>How a CPU Works (and Why It Struggles)</SectionTitle>
      <Para>To understand why we need custom hardware, you need to understand what a CPU is doing and where it gets stuck.</Para>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {steps.map((s, i) => (
          <button key={i} onClick={() => setStep(i)} style={{
            background: step === i ? colors.blue : "#e5e7eb",
            color: step === i ? "white" : colors.gray,
            border: "none", borderRadius: 8, padding: "8px 14px", cursor: "pointer", fontWeight: 600, fontSize: 13
          }}>Step {i + 1}</button>
        ))}
      </div>

      <Card color="lightBlue" style={{ minHeight: 140 }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>{steps[step].icon}</div>
        <div style={{ fontWeight: 800, fontSize: 17, marginBottom: 8 }}>{steps[step].title}</div>
        <p style={{ margin: 0, fontSize: 15, lineHeight: 1.7 }}>{steps[step].content}</p>
      </Card>

      {step === 2 && (
        <Card color="lightOrange">
          <strong>Visual: Software doing cross-correlation (N=4 simplified)</strong>
          <div style={{ fontFamily: "monospace", fontSize: 13, marginTop: 10, lineHeight: 2 }}>
            {["ref[0]×mic[0]", "ref[1]×mic[1]", "ref[2]×mic[2]", "ref[3]×mic[3]"].map((op, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ background: "#fed7aa", padding: "2px 8px", borderRadius: 4 }}>Step {i * 2 + 1}</span>
                <span>multiply: {op}</span>
              </div>
            ))}
            <div style={{ marginTop: 4, color: colors.orange, fontWeight: 700 }}>
              Then 4 more steps for the additions. 8 steps total for N=4. For N=128: 384 sequential steps.
            </div>
          </div>
        </Card>
      )}

      {step === 3 && (
        <Card color="lightOrange">
          <strong>This is what "memory-bound" means.</strong>
          <p style={{ margin: "8px 0 0", fontSize: 15, lineHeight: 1.6 }}>
            Your arithmetic intensity of <strong>0.747 FLOP/byte</strong> means: for every byte fetched from memory, you only do 0.747 calculations. The CPU spends most of its time waiting for data, not computing. That's why hardware that keeps data on-chip (like your shift registers) changes everything.
          </p>
        </Card>
      )}
    </div>
  );
}

// ─── CHAPTER 3: MAC ───────────────────────────────────────────────────────────
function ChapterMAC() {
  const [a, setA] = useState(3);
  const [b, setB] = useState(4);
  const [acc, setAcc] = useState(0);
  const [history, setHistory] = useState([]);

  const doMAC = () => {
    const newAcc = acc + a * b;
    setHistory([...history, { a, b, product: a * b, acc: newAcc }]);
    setAcc(newAcc);
  };
  const reset = () => { setAcc(0); setHistory([]); };

  return (
    <div>
      <SectionTitle>The MAC — One Operation Rules AI</SectionTitle>
      <Para>
        Your professor's big reveal: <strong>virtually all of AI reduces to one operation</strong>. The Multiply-Accumulate, or MAC.
      </Para>

      <Card color="lightPurple">
        <div style={{ fontWeight: 800, fontSize: 18, color: colors.purple, marginBottom: 8 }}>What a MAC does:</div>
        <div style={{ fontFamily: "monospace", fontSize: 20, background: "#fff", padding: "10px 16px", borderRadius: 8, color: colors.purple, textAlign: "center" }}>
          accumulator ← accumulator + (a × b)
        </div>
        <p style={{ margin: "10px 0 0", fontSize: 15, lineHeight: 1.6 }}>
          That's it. Multiply two numbers, add the result to a running total. One MAC = 2 FLOPs (1 multiply + 1 add). It looks tiny but it's the atom everything is built from.
        </p>
      </Card>

      <Para>
        <strong>Try it — this is literally how your echo detection hardware works:</strong>
      </Para>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 12 }}>
        <div style={{ background: colors.lightGray, borderRadius: 10, padding: 16, flex: 1, minWidth: 200 }}>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Set inputs (ref[i] × mic[i])</div>
          <div style={{ display: "flex", gap: 12, marginBottom: 10 }}>
            <div>
              <label style={{ fontSize: 13, fontWeight: 600 }}>a (ref)</label>
              <input type="number" value={a} onChange={e => setA(Number(e.target.value))}
                style={{ display: "block", width: 70, padding: 6, borderRadius: 6, border: "1px solid #d1d5db", fontSize: 16, marginTop: 4 }} />
            </div>
            <div>
              <label style={{ fontSize: 13, fontWeight: 600 }}>b (mic)</label>
              <input type="number" value={b} onChange={e => setB(Number(e.target.value))}
                style={{ display: "block", width: 70, padding: 6, borderRadius: 6, border: "1px solid #d1d5db", fontSize: 16, marginTop: 4 }} />
            </div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={doMAC} style={{ background: colors.purple, color: "white", border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontWeight: 700 }}>
              Fire MAC
            </button>
            <button onClick={reset} style={{ background: "#e5e7eb", color: colors.gray, border: "none", borderRadius: 8, padding: "8px 16px", cursor: "pointer", fontWeight: 600 }}>
              Reset
            </button>
          </div>
        </div>
        <div style={{ background: "#f5f3ff", borderRadius: 10, padding: 16, flex: 1, minWidth: 200 }}>
          <div style={{ fontWeight: 700, marginBottom: 8, color: colors.purple }}>Accumulator = {acc}</div>
          <div style={{ maxHeight: 150, overflowY: "auto" }}>
            {history.length === 0 && <div style={{ color: "#888", fontSize: 14 }}>No operations yet. Fire a MAC!</div>}
            {history.map((h, i) => (
              <div key={i} style={{ fontSize: 13, fontFamily: "monospace", padding: "3px 0", borderBottom: "1px solid #e5e7eb" }}>
                {h.acc - h.product} + ({h.a} × {h.b}) = <strong>{h.acc}</strong>
              </div>
            ))}
          </div>
          {history.length > 0 && <div style={{ fontSize: 13, color: colors.purple, marginTop: 8, fontWeight: 600 }}>This is a dot product of {history.length} terms.</div>}
        </div>
      </div>

      <Card color="lightGreen">
        <strong>The key insight from your professor's slides:</strong>
        <ul style={{ margin: "8px 0 0", paddingLeft: 20, fontSize: 15, lineHeight: 1.9 }}>
          <li>A dot product (w·x) = N MACs chained together</li>
          <li>One neural network layer = M dot products = a matrix multiply (GEMM)</li>
          <li>GPUs are fast because they're built to run millions of MACs in parallel</li>
          <li>Your echo chiplet is fast for the same reason — N MACs, all parallel</li>
        </ul>
      </Card>
    </div>
  );
}

// ─── CHAPTER 4: WHY HW BEATS SW ───────────────────────────────────────────────
function ChapterWhyHW() {
  const [mode, setMode] = useState("sw");
  const N = 8;

  return (
    <div>
      <SectionTitle>Why Hardware Beats Software for AI</SectionTitle>
      <Para>
        Same math. Different way of doing it. The difference is <strong>when</strong> things happen and <strong>where</strong> the data lives.
      </Para>

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={() => setMode("sw")} style={{
          background: mode === "sw" ? colors.orange : "#e5e7eb", color: mode === "sw" ? "white" : colors.gray,
          border: "none", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontWeight: 700, fontSize: 15
        }}>Software (CPU)</button>
        <button onClick={() => setMode("hw")} style={{
          background: mode === "hw" ? colors.green : "#e5e7eb", color: mode === "hw" ? "white" : colors.gray,
          border: "none", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontWeight: 700, fontSize: 15
        }}>Hardware (Chiplet)</button>
      </div>

      {mode === "sw" && (
        <Card color="lightOrange">
          <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 10 }}>CPU runs cross-correlation (N={N})</div>
          <div style={{ fontFamily: "monospace", fontSize: 13, lineHeight: 2.2 }}>
            {Array.from({ length: N }, (_, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ background: "#fed7aa", padding: "1px 8px", borderRadius: 4, minWidth: 60, textAlign: "right" }}>
                  step {i + 1}
                </span>
                <span style={{ color: colors.orange }}>→</span>
                <span>fetch ref[{i}] from RAM</span>
                <span style={{ color: "#aaa" }}>→ fetch mic[{i}] from RAM → multiply → add to sum</span>
              </div>
            ))}
            <div style={{ marginTop: 8, fontWeight: 700, color: colors.orange }}>
              Total: {N * 3} sequential steps. Each RAM fetch can take 100+ CPU cycles waiting.
            </div>
          </div>
        </Card>
      )}

      {mode === "hw" && (
        <Card color="lightGreen">
          <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 10 }}>Chiplet runs cross-correlation (N={N})</div>
          <div style={{ fontSize: 14, color: "#555", marginBottom: 10 }}>All {N} multipliers fire at the same time. Data is already on-chip in shift registers — no RAM access.</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            {Array.from({ length: N }, (_, i) => (
              <div key={i} style={{ background: "#bbf7d0", borderRadius: 8, padding: "8px 10px", textAlign: "center", fontSize: 12, fontWeight: 700, color: colors.green, border: "2px solid #4ade80" }}>
                <div>MAC {i}</div>
                <div style={{ fontFamily: "monospace", fontSize: 11, color: "#555" }}>r[{i}]×m[{i}]</div>
              </div>
            ))}
          </div>
          <div style={{ background: "#4ade80", borderRadius: 8, padding: "8px 16px", textAlign: "center", fontWeight: 800, color: "white", fontSize: 15 }}>
            ↑ All {N} fire in ONE clock cycle ↑
          </div>
          <div style={{ marginTop: 10, fontWeight: 700, color: colors.green }}>
            Then: add them all up (tree reduction), normalize, compare. Done in ~log₂({N}) = {Math.ceil(Math.log2(N))} more cycles.
          </div>
        </Card>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 8 }}>
        {[
          { label: "Latency", sw: `~${N * 3 * 100}+ cycles`, hw: `~${Math.ceil(Math.log2(N)) + 2} cycles`, icon: "⏱️" },
          { label: "Memory traffic", sw: "Every sample fetched from RAM", hw: "Zero — shift registers on-chip", icon: "💾" },
          { label: "Overhead", sw: "Fetch/decode/branch/OS/jitter", hw: "None — just wires and gates", icon: "⚡" },
          { label: "Arithmetic intensity", sw: "0.747 FLOP/byte (memory-bound)", hw: "Compute-bound (no DRAM)", icon: "📊" },
        ].map(row => (
          <div key={row.label} style={{ background: colors.lightGray, borderRadius: 10, padding: 12 }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>{row.icon} {row.label}</div>
            <div style={{ fontSize: 12 }}>
              <span style={{ color: colors.orange, fontWeight: 600 }}>SW: </span>{row.sw}
            </div>
            <div style={{ fontSize: 12, marginTop: 3 }}>
              <span style={{ color: colors.green, fontWeight: 600 }}>HW: </span>{row.hw}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── CHAPTER 5: HW VS SW ──────────────────────────────────────────────────────
function ChapterHWSW() {
  const [q, setQ] = useState(null);
  const questions = [
    { q: "Is Python code hardware or software?", a: "Software. It runs on a CPU (which IS hardware), but the code itself — the instructions — is software. Your echo_detect.py is software.", correct: "sw" },
    { q: "Is a neural network hardware or software?", a: "Depends on where it runs. PyTorch running on a CPU = software. A weight matrix baked into an ASIC = hardware. Same math, different medium.", correct: "both" },
    { q: "Is SystemVerilog hardware or software?", a: "It's a hardware description language — it describes circuits, not instructions. When OpenLane 2 compiles it, the output is a layout of transistors on silicon. That's hardware.", correct: "hw" },
  ];
  return (
    <div>
      <SectionTitle>HW vs SW — What Are You Actually Building?</SectionTitle>
      <Para>
        This is the question that confused you: "if we're writing code, isn't it software?" Short answer: no — depends on what the code <em>describes</em>.
      </Para>

      <Card color="lightBlue">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div>
            <div style={{ fontWeight: 800, color: colors.blue, marginBottom: 8 }}>💻 Software (Instructions)</div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 14, lineHeight: 2 }}>
              <li>Tells a processor WHAT TO DO</li>
              <li>Runs step by step</li>
              <li>Can be changed any time</li>
              <li>Lives in memory, executed by CPU</li>
              <li><strong>Your Python baseline = this</strong></li>
            </ul>
          </div>
          <div>
            <div style={{ fontWeight: 800, color: colors.green, marginBottom: 8 }}>🔲 Hardware (Circuits)</div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 14, lineHeight: 2 }}>
              <li>Describes WHAT CONNECTIONS EXIST</li>
              <li>Everything happens simultaneously</li>
              <li>Fixed after fabrication</li>
              <li>Lives in silicon as transistors</li>
              <li><strong>Your SystemVerilog = this</strong></li>
            </ul>
          </div>
        </div>
      </Card>

      <Para>The analogy that might help: Python is like giving someone <em>verbal instructions</em> to build furniture. SystemVerilog is like drawing <em>blueprints</em> for the furniture itself. Same end result, completely different medium.</Para>

      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 10 }}>Quick check — test yourself:</div>
      {questions.map((item, i) => (
        <div key={i} style={{ marginBottom: 12 }}>
          <div style={{ background: colors.lightGray, borderRadius: 10, padding: 14 }}>
            <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 8 }}>{item.q}</div>
            <div style={{ display: "flex", gap: 8 }}>
              {["sw", "hw", "both"].map(opt => (
                <button key={opt} onClick={() => setQ({ ...q, [i]: opt })} style={{
                  background: q?.[i] === opt ? (opt === item.correct ? colors.green : "#ef4444") : "#e5e7eb",
                  color: q?.[i] === opt ? "white" : colors.gray,
                  border: "none", borderRadius: 8, padding: "6px 14px", cursor: "pointer", fontWeight: 600, fontSize: 13
                }}>{opt === "sw" ? "Software" : opt === "hw" ? "Hardware" : "Both / Depends"}</button>
              ))}
            </div>
            {q?.[i] && (
              <div style={{ marginTop: 10, fontSize: 14, color: q[i] === item.correct ? colors.green : "#ef4444", fontWeight: 600 }}>
                {q[i] === item.correct ? "✓ " : "✗ "}{item.a}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── CHAPTER 6: CHIPLETS ──────────────────────────────────────────────────────
function ChapterChiplet() {
  const [selected, setSelected] = useState(null);
  const chips = [
    { id: "cpu", label: "CPU", color: "#bfdbfe", desc: "General purpose. Does everything. Slow for repetitive AI math because it's sequential and flexible.", icon: "⚙️", pos: { top: 20, left: 20 } },
    { id: "gpu", label: "GPU", color: "#fef3c7", desc: "Thousands of small cores. Great at running the same instruction on many pieces of data at once — GEMM, matrix multiply. That's why it accelerates deep learning.", icon: "🖥️", pos: { top: 20, right: 20 } },
    { id: "acc", label: "AI Acc", color: "#d1fae5", desc: "A dedicated accelerator (like a TPU or your chiplet). Designed for one workload. No flexibility. Maximum efficiency for that specific operation.", icon: "🔲", pos: { bottom: 30, left: "50%", transform: "translateX(-50%)" } },
    { id: "mem", label: "Memory", color: "#ede9fe", desc: "On-chip SRAM or off-chip DRAM. The bottleneck between compute and data. Your shift registers are a form of on-chip memory — keeping data close to the compute units.", icon: "💾", pos: { bottom: 30, left: 20 } },
  ];
  return (
    <div>
      <SectionTitle>Chiplets and the Hardware Landscape</SectionTitle>
      <Para>
        Your professor showed the "path to extreme heterogeneity." The short version: the industry moved from one big CPU doing everything, to mixing specialized chips on the same package. That mix is called a <strong>heterogeneous architecture</strong>.
      </Para>
      <Para>
        A <strong>chiplet</strong> is a small chip that does one job and connects to other chiplets via a high-speed bus (like UCIe). Instead of making one giant chip that tries to do everything, you make a team of specialists.
      </Para>

      <div style={{ background: "#f8fafc", borderRadius: 14, border: "2px dashed #94a3b8", padding: 20, position: "relative", minHeight: 200, marginBottom: 16 }}>
        <div style={{ textAlign: "center", fontWeight: 700, color: "#64748b", marginBottom: 12 }}>Click a block to learn what it does</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center" }}>
          {chips.map(chip => (
            <div key={chip.id} onClick={() => setSelected(chip.id === selected ? null : chip.id)}
              style={{
                background: chip.color, borderRadius: 10, padding: "14px 18px", cursor: "pointer",
                border: selected === chip.id ? `3px solid ${colors.blue}` : "3px solid transparent",
                fontWeight: 700, fontSize: 16, textAlign: "center", minWidth: 90,
                boxShadow: selected === chip.id ? "0 0 0 2px #3b82f6" : "none",
                transition: "all 0.15s"
              }}>
              <div style={{ fontSize: 24 }}>{chip.icon}</div>
              <div>{chip.label}</div>
            </div>
          ))}
        </div>
        {selected && (
          <div style={{ marginTop: 14, background: "white", borderRadius: 10, padding: 14, border: "1px solid #e2e8f0" }}>
            <strong>{chips.find(c => c.id === selected)?.label}:</strong> {chips.find(c => c.id === selected)?.desc}
          </div>
        )}
      </div>

      <Card color="lightGreen">
        <strong>PPAC — the 4 metrics every hardware designer optimizes for:</strong>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
          {[
            { letter: "P", word: "Performance", desc: "How fast does it compute?" },
            { letter: "P", word: "Power", desc: "How many watts does it burn?" },
            { letter: "A", word: "Area", desc: "How much silicon does it use? (smaller = cheaper)" },
            { letter: "C", word: "Cost", desc: "Total cost to build and manufacture" },
          ].map(m => (
            <div key={m.word} style={{ background: "#f0fdf4", borderRadius: 8, padding: "8px 12px" }}>
              <span style={{ fontWeight: 800, color: colors.green, fontSize: 18 }}>{m.letter} </span>
              <span style={{ fontWeight: 700 }}>{m.word}:</span>
              <span style={{ fontSize: 14, color: "#555" }}> {m.desc}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

// ─── CHAPTER 7: YOUR PROJECT ───────────────────────────────────────────────────
function ChapterEcho() {
  const [expandedQ, setExpandedQ] = useState(null);
  const heilmeier = [
    { q: "Q1: What are you trying to do?", a: "Build a hardware chiplet that detects echoes in real-time audio by computing normalized cross-correlation between the speaker output and the mic input. Output: 1 bit. No CPU involved." },
    { q: "Q2: How is it done today + limits?", a: "Software on CPU/DSP. Limits: latency (ms of delay = audible), CPU load (competes with audio tasks), power (keeping a core active drains batteries in earbuds/hearing aids)." },
    { q: "Q3: What's new in your approach?", a: "Fixed-function chiplet. Same math, but wired directly in silicon. Every window is identical (dot product + normalize + compare), which is exactly what makes it a good fit for custom hardware." },
    { q: "Q4-Q7 (M1): What's at risk, impact, timeline?", a: "Still to write. Q4: risks (threshold tuning, interface overhead). Q5: faster detection, lower power for voice AI devices. Q6: semester timeline. Q7: working HDL + synthesis as mid-term check." },
  ];

  const pipeline = [
    { label: "Far-end ref x[n]", color: "#bfdbfe", icon: "🔊" },
    { label: "Shift Reg (N taps)", color: "#ddd6fe", icon: "📝" },
    { label: "N-wide MAC Array", color: "#fde68a", icon: "✖️" },
    { label: "Normalizer ÷ energy", color: "#d1fae5", icon: "📐" },
    { label: "Comparator ρ>τ", color: "#fecdd3", icon: "⚖️" },
    { label: "1-bit output", color: "#bbf7d0", icon: "💡" },
  ];

  return (
    <div>
      <SectionTitle>Your Project: Echo Detection Chiplet</SectionTitle>
      <Para>
        Everything you just learned converges here. Your project is a real answer to the question your professor keeps asking: <em>why build custom hardware?</em>
      </Para>

      <Card color="lightBlue">
        <div style={{ fontWeight: 800, fontSize: 15, marginBottom: 10 }}>The algorithm in one line:</div>
        <div style={{ fontFamily: "monospace", background: "#1e293b", color: "#7dd3fc", padding: "12px 16px", borderRadius: 8, fontSize: 15 }}>
          ρ = Σ(ref[i] × mic[i]) / √(Σref[i]² × Σmic[i]²)
        </div>
        <p style={{ margin: "10px 0 0", fontSize: 14, color: "#555" }}>
          If ρ ≥ threshold → echo detected. That's it. Three dot products, one divide, one compare.
        </p>
      </Card>

      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 8 }}>Your hardware pipeline (click to follow data through):</div>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 6, marginBottom: 16 }}>
        {pipeline.map((stage, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ background: stage.color, borderRadius: 10, padding: "10px 12px", textAlign: "center", minWidth: 90, fontSize: 13, fontWeight: 600 }}>
              <div style={{ fontSize: 20 }}>{stage.icon}</div>
              {stage.label}
            </div>
            {i < pipeline.length - 1 && <div style={{ fontSize: 20, color: "#94a3b8" }}>→</div>}
          </div>
        ))}
      </div>

      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 8 }}>Why this workload is perfect for hardware (the argument you need to make):</div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
        {[
          { check: "Same operation every window", why: "No branching logic in hardware needed" },
          { check: "All N MACs are independent", why: "Fire them all in 1 clock cycle — that's your speedup" },
          { check: "Streaming audio (shift registers)", why: "Data lives on-chip — no DRAM = not memory-bound" },
          { check: "Binary output", why: "Minimal output bandwidth, no complex post-processing" },
        ].map(item => (
          <div key={item.check} style={{ background: colors.lightGray, borderRadius: 10, padding: 12 }}>
            <div style={{ color: colors.green, fontWeight: 700, marginBottom: 4 }}>✓ {item.check}</div>
            <div style={{ fontSize: 13, color: "#555" }}>{item.why}</div>
          </div>
        ))}
      </div>

      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 8 }}>Heilmeier Catechism — where you stand:</div>
      {heilmeier.map((item, i) => (
        <div key={i} style={{ marginBottom: 8, border: "1px solid #e2e8f0", borderRadius: 10, overflow: "hidden" }}>
          <button onClick={() => setExpandedQ(expandedQ === i ? null : i)}
            style={{ width: "100%", textAlign: "left", background: expandedQ === i ? "#1e293b" : colors.lightGray,
              color: expandedQ === i ? "white" : colors.gray, border: "none", padding: "12px 16px",
              fontWeight: 700, fontSize: 14, cursor: "pointer", display: "flex", justifyContent: "space-between" }}>
            <span>{item.q}</span>
            <span>{expandedQ === i ? "▲" : "▼"}</span>
          </button>
          {expandedQ === i && (
            <div style={{ padding: "12px 16px", fontSize: 14, lineHeight: 1.7, background: "white" }}>
              {item.a}
            </div>
          )}
        </div>
      ))}

      <Card color="lightGreen" style={{ marginTop: 16 }}>
        <strong>The one-sentence version of your whole project:</strong>
        <p style={{ margin: "8px 0 0", fontSize: 15, lineHeight: 1.7 }}>
          You're proving that taking cross-correlation echo detection out of software and wiring it directly into silicon — with N parallel MACs reading from on-chip shift registers instead of DRAM — eliminates the memory bottleneck, drops the detection latency from milliseconds to nanoseconds, and frees the CPU entirely.
        </p>
      </Card>
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
const chapterComponents = {
  computation: ChapterComputation,
  cpu: ChapterCPU,
  mac: ChapterMAC,
  whyhw: ChapterWhyHW,
  hwsw: ChapterHWSW,
  chiplet: ChapterChiplet,
  echo: ChapterEcho,
};

export default function App() {
  const [activeChapter, setActiveChapter] = useState("computation");
  const ActiveComponent = chapterComponents[activeChapter];
  const currentIndex = chapters.findIndex(c => c.id === activeChapter);

  return (
    <div style={{ fontFamily: "system-ui, -apple-system, sans-serif", minHeight: "100vh", background: "#f8fafc", display: "flex" }}>
      {/* Sidebar */}
      <div style={{ width: 240, background: "#1e293b", flexShrink: 0, padding: "24px 12px", minHeight: "100vh" }}>
        <div style={{ color: "#7dd3fc", fontWeight: 800, fontSize: 13, marginBottom: 4, paddingLeft: 8 }}>ECE 410/510</div>
        <div style={{ color: "white", fontWeight: 700, fontSize: 15, marginBottom: 20, paddingLeft: 8 }}>HW4AI Explainer</div>
        {chapters.map(ch => (
          <button key={ch.id} onClick={() => setActiveChapter(ch.id)} style={{
            display: "block", width: "100%", textAlign: "left",
            background: activeChapter === ch.id ? "#3b82f6" : "transparent",
            color: activeChapter === ch.id ? "white" : "#94a3b8",
            border: "none", borderRadius: 8, padding: "10px 12px", cursor: "pointer",
            fontWeight: activeChapter === ch.id ? 700 : 500, fontSize: 13,
            marginBottom: 2, lineHeight: 1.4, transition: "all 0.1s"
          }}>
            {ch.emoji} {ch.title}
          </button>
        ))}
        <div style={{ marginTop: 24, paddingLeft: 8, color: "#475569", fontSize: 11 }}>
          Saleh Sabti | Spring 2026
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, padding: "32px 36px", maxWidth: 820, overflowY: "auto" }}>
        <ActiveComponent />

        {/* Navigation */}
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 32, paddingTop: 20, borderTop: "1px solid #e2e8f0" }}>
          <button
            onClick={() => setActiveChapter(chapters[currentIndex - 1]?.id)}
            disabled={currentIndex === 0}
            style={{ background: currentIndex === 0 ? "#e5e7eb" : "#1e293b", color: currentIndex === 0 ? "#9ca3af" : "white",
              border: "none", borderRadius: 8, padding: "10px 20px", cursor: currentIndex === 0 ? "not-allowed" : "pointer", fontWeight: 700 }}>
            ← Previous
          </button>
          <span style={{ fontSize: 13, color: "#94a3b8", alignSelf: "center" }}>
            {currentIndex + 1} / {chapters.length}
          </span>
          <button
            onClick={() => setActiveChapter(chapters[currentIndex + 1]?.id)}
            disabled={currentIndex === chapters.length - 1}
            style={{ background: currentIndex === chapters.length - 1 ? "#e5e7eb" : colors.blue,
              color: currentIndex === chapters.length - 1 ? "#9ca3af" : "white",
              border: "none", borderRadius: 8, padding: "10px 20px", cursor: currentIndex === chapters.length - 1 ? "not-allowed" : "pointer", fontWeight: 700 }}>
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}
