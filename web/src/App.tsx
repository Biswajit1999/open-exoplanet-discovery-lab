import { motion, useReducedMotion } from "motion/react";

type Stream = {
  name: string;
  instrument: string;
  role: string;
  status: "READY" | "CENSUS" | "ACTIVE" | "WAIT";
  note: string;
};

const streams: Stream[] = [
  { name: "NETS III", instrument: "NEID", role: "EPRV completeness", status: "READY", note: "41 systems; public RV + activity time series." },
  { name: "NIRPS Phase-3", instrument: "NIRPS", role: "NIR coherence", status: "CENSUS", note: "Public dynamic stream; DRS provenance is mandatory." },
  { name: "HARPS archive", instrument: "HARPS", role: "Optical comparison", status: "CENSUS", note: "Target overlap and epoch simultaneity are frozen before inference." },
  { name: "SPORES-HWO II", instrument: "multi-RV", role: "Long-baseline robustness", status: "WAIT", note: "Principal VizieR tables gated until verified public access." },
  { name: "TESS 106/107", instrument: "TESS", role: "Temporal/activity context", status: "ACTIVE", note: "Sector 106 control; Sector 107 release state is versioned." },
  { name: "Rocky Worlds", instrument: "JWST + HST", role: "Atmospheric reproducibility", status: "ACTIVE", note: "Repeated measurements are analysed as reproducibility evidence." },
];

const pipeline = ["Archive", "Provenance", "Quality control", "Model", "Injection / recovery", "Cross-check", "Robustness"];

function App() {
  const reduce = useReducedMotion();

  return (
    <main>
      <header className="hero">
        <div className="eyebrow">BISWAJIT JANA · 2026</div>
        <motion.h1 initial={reduce ? false : { opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
          Open Exoplanet<br />Evidence Lab
        </motion.h1>
        <p className="lede">
          A provenance-first framework for testing how instrument systematics, stellar activity,
          wavelength, cadence and independent archives change exoplanet inference.
        </p>
        <div className="pipeline" aria-label="Research pipeline">
          {pipeline.map((step, i) => (
            <motion.div
              className="pipe-step"
              key={step}
              initial={reduce ? false : { opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: reduce ? 0 : i * 0.06 }}
            >
              <span>{String(i + 1).padStart(2, "0")}</span>{step}
            </motion.div>
          ))}
        </div>
      </header>

      <section className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">OBSERVATIONAL BASIS</div>
            <h2>Evidence streams</h2>
          </div>
          <p>Release state is part of the analysis. A source that is still evolving is never silently treated as frozen.</p>
        </div>
        <div className="grid">
          {streams.map((stream) => (
            <motion.article whileHover={reduce ? undefined : { y: -3 }} className="card" key={stream.name}>
              <div className="card-top"><span>{stream.instrument}</span><b data-status={stream.status}>{stream.status}</b></div>
              <h3>{stream.name}</h3>
              <div className="role">{stream.role}</div>
              <p>{stream.note}</p>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="section methods">
        <div className="section-head">
          <div>
            <div className="eyebrow">SCIENTIFIC CONTRACT</div>
            <h2>What the project tests</h2>
          </div>
        </div>
        <div className="method-grid">
          <article><span>01</span><h3>Instrument robustness</h3><p>Zero points, reduction versions and observing eras are model terms rather than footnotes.</p></article>
          <article><span>02</span><h3>Stellar robustness</h3><p>Activity proxies and correlated structure are tested without assuming a Gaussian process is always preferable.</p></article>
          <article><span>03</span><h3>Chromatic robustness</h3><p>Optical and NIR RV signals are compared in period, phase and semi-amplitude with explicit instrumental nuisance terms.</p></article>
          <article><span>04</span><h3>Detection robustness</h3><p>Null results are interpreted through injection/recovery completeness rather than absence of a periodogram peak.</p></article>
        </div>
      </section>

      <footer>
        <div><strong>Open Exoplanet Evidence Lab</strong><br />Independent open-science research · Biswajit Jana</div>
        <div>Measurement ≠ inference ≠ interpretation</div>
      </footer>
    </main>
  );
}

export default App;
