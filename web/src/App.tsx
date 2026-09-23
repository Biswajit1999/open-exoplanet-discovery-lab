import { AnimatePresence, motion, useReducedMotion } from "motion/react"
import { useEffect, useMemo, useState } from "react"
import ResultsSection from "./ResultsSection"

type Source = {
  id: string
  name: string
  status: "ready" | "census" | "active" | "wait" | "future"
  role: string
  detail: string
}

type ProjectData = {
  release: string
  author: string
  title: string
  question: string
  sources: Source[]
  validation: { name: string; meaning: string }[]
}

const statusLabels: Record<Source["status"], string> = {
  ready: "Public / ready",
  census: "Public / census",
  active: "Public / evolving",
  wait: "Access gated",
  future: "Future adapter",
}

function PipelineFlow({ reduced }: { reduced: boolean | null }) {
  const stages = ["Archive", "Provenance", "QC", "Model", "Injection / recovery", "Cross-check", "Robustness"]
  return (
    <div className="pipeline" aria-label="Scientific evidence pipeline">
      {stages.map((stage, index) => (
        <div className="pipelineWrap" key={stage}>
          <motion.div
            className="pipelineStage"
            initial={reduced ? false : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: reduced ? 0 : index * 0.055, duration: 0.34 }}
          >
            <span className="pipelineIndex">{String(index + 1).padStart(2, "0")}</span>
            <span>{stage}</span>
          </motion.div>
          {index < stages.length - 1 && <span className="pipelineArrow" aria-hidden="true">→</span>}
        </div>
      ))}
    </div>
  )
}

function SourceCard({ source }: { source: Source }) {
  return (
    <article className="sourceCard">
      <div className="sourceTopline">
        <span className={"status status-" + source.status}>{statusLabels[source.status]}</span>
        <span className="sourceId">{source.id}</span>
      </div>
      <h3>{source.name}</h3>
      <p className="sourceRole">{source.role}</p>
      <p>{source.detail}</p>
    </article>
  )
}

function ProvenanceDrawer() {
  const [open, setOpen] = useState(false)
  return (
    <section className="provenanceSection">
      <button
        className="drawerButton"
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <span>Provenance contract</span>
        <span aria-hidden="true">{open ? "−" : "+"}</span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            className="drawerBody"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="provenanceGrid">
              <div><small>01</small><strong>Archive identity</strong><p>Product IDs, collection, instrument and target identity.</p></div>
              <div><small>02</small><strong>Reduction identity</strong><p>Pipeline version, observing mode, era and quality state.</p></div>
              <div><small>03</small><strong>Analysis identity</strong><p>Manifest hash, configuration hash and software commit.</p></div>
              <div><small>04</small><strong>Result identity</strong><p>Units, uncertainty semantics and measured/fitted/simulated state.</p></div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  )
}

function MiniSignal() {
  const points = Array.from({ length: 120 }, (_, i) => {
    const x = i / 119
    const y = 0.5 + 0.18 * Math.sin(x * Math.PI * 7.2) + 0.04 * Math.sin(x * Math.PI * 31)
    return [x, y]
  })
  const d = points
    .map(([x, y], index) => (index === 0 ? "M" : "L") + " " + (x * 760).toFixed(2) + " " + (y * 180).toFixed(2))
    .join(" ")
  return (
    <svg className="signal" viewBox="0 0 760 180" role="img" aria-label="Illustrative radial-velocity signal trace">
      <line x1="0" y1="90" x2="760" y2="90" className="axisLine" />
      <path d={d} className="signalPath" />
    </svg>
  )
}

function App() {
  const reduced = useReducedMotion()
  const [data, setData] = useState<ProjectData | null>(null)
  const [active, setActive] = useState<"evidence" | "validation" | "method">("evidence")

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + "data/project.json")
      .then((response) => {
        if (!response.ok) throw new Error("Project metadata unavailable")
        return response.json()
      })
      .then(setData)
      .catch(() => setData(null))
  }, [])

  const sourceCounts = useMemo(() => {
    if (!data) return { usable: 0, gated: 0 }
    return {
      usable: data.sources.filter((s) => ["ready", "census", "active"].includes(s.status)).length,
      gated: data.sources.filter((s) => ["wait", "future"].includes(s.status)).length,
    }
  }, [data])

  return (
    <main>
      <header className="topbar">
        <a href="#top" className="wordmark">OEEL</a>
        <nav aria-label="Primary">
          <a href="#evidence">Evidence</a>
          <a href="#methods">Methods</a>
          <a href="#provenance">Provenance</a>
          <a href="https://github.com/Biswajit1999/open-exoplanet-discovery-lab">GitHub</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <div className="heroCopy">
          <p className="eyebrow">Extreme-precision radial velocity · cross-archive inference</p>
          <motion.h1
            initial={reduced ? false : { opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55 }}
          >
            Open Exoplanet<br />Evidence Lab
          </motion.h1>
          <p className="lede">
            A provenance-first framework for testing how instrument systematics, stellar activity,
            wavelength, cadence and independent observations change exoplanet inference.
          </p>
          <div className="heroMeta">
            <span>Biswajit Jana</span>
            <span>2026 research release</span>
            <span>Python + public astronomical archives</span>
          </div>
        </div>
        <div className="heroFigure">
          <div className="figureLabel"><span>RV TRACE</span><span>illustrative · not a detection</span></div>
          <MiniSignal />
          <div className="figureStats">
            <div><small>analysis principle</small><strong>measurement ≠ inference</strong></div>
            <div><small>validation principle</small><strong>nulls remain results</strong></div>
          </div>
        </div>
      </section>

      <section className="pipelineSection">
        <p className="sectionKicker">Evidence path</p>
        <PipelineFlow reduced={reduced} />
      </section>

      <section className="researchQuestion">
        <p className="sectionKicker">Central question</p>
        <h2>{data?.question ?? "How stable are exoplanet conclusions when the nuisance model changes?"}</h2>
        <p>
          The project tests robustness rather than rewarding a particular outcome. A more complex model
          is useful only when it improves calibrated inference without absorbing the astrophysical signal.
        </p>
      </section>

      <section id="evidence" className="contentSection">
        <div className="sectionHeader">
          <div>
            <p className="sectionKicker">Public evidence</p>
            <h2>Archive layer</h2>
          </div>
          <div className="metricPair">
            <div><strong>{sourceCounts.usable}</strong><span>usable streams</span></div>
            <div><strong>{sourceCounts.gated}</strong><span>explicitly gated</span></div>
          </div>
        </div>

        <div className="segmented" role="tablist" aria-label="Research sections">
          {(["evidence", "validation", "method"] as const).map((key) => (
            <button
              key={key}
              role="tab"
              aria-selected={active === key}
              className={active === key ? "selected" : ""}
              onClick={() => setActive(key)}
            >
              {key === "evidence" ? "Data streams" : key === "validation" ? "Validation" : "Inference"}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {active === "evidence" && (
            <motion.div key="evidence" className="sourceGrid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {(data?.sources ?? []).map((source) => <SourceCard key={source.id} source={source} />)}
            </motion.div>
          )}
          {active === "validation" && (
            <motion.div key="validation" className="validationGrid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {(data?.validation ?? []).map((item, index) => (
                <article className="validationCard" key={item.name}>
                  <span className="validationNumber">{String(index + 1).padStart(2, "0")}</span>
                  <h3>{item.name}</h3>
                  <p>{item.meaning}</p>
                </article>
              ))}
            </motion.div>
          )}
          {active === "method" && (
            <motion.div key="method" className="methodGrid" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <article><small>RV</small><h3>Instrument-aware likelihood</h3><p>Per-era offsets, formal uncertainty, white jitter, activity terms and optional correlated covariance.</p></article>
              <article><small>SEARCH</small><h3>Calibrated periodicity</h3><p>GLS plus observing-window analysis, false-alarm calibration, aliases and held-out epochs.</p></article>
              <article><small>SENSITIVITY</small><h3>Injection / recovery</h3><p>Frozen injections generate completeness surfaces and K50/K90 rather than anecdotal detections.</p></article>
              <article><small>CROSS-CHECK</small><h3>Chromatic coherence</h3><p>HARPS and NIRPS compare period, phase, semi-amplitude and activity without assuming NIR activity is weaker.</p></article>
              <article><small>ATMOSPHERE</small><h3>Repeatability floor</h3><p>Repeated spectra/eclipses estimate additional inter-visit or inter-reduction variance.</p></article>
              <article><small>REPORT</small><h3>Typed result state</h3><p>Every number is labelled measured, derived, fitted, simulated, literature or provisional.</p></article>
            </motion.div>
          )}
        </AnimatePresence>
      </section>

      <ResultsSection />

      <section id="methods" className="twoColumn">
        <div>
          <p className="sectionKicker">Research discipline</p>
          <h2>The nuisance model is part of the science.</h2>
        </div>
        <div className="principles">
          <p><span>01</span> Instrument upgrades and reduction versions are explicit model inputs.</p>
          <p><span>02</span> Activity correction is tested for planet-amplitude bias, not judged by residual RMS alone.</p>
          <p><span>03</span> Non-detections require measured sensitivity.</p>
          <p><span>04</span> Cross-archive joins need a physical reason.</p>
          <p><span>05</span> Novelty language requires a dated literature audit.</p>
        </div>
      </section>

      <section id="provenance" className="contentSection provenanceBlock">
        <p className="sectionKicker">Traceability</p>
        <h2>Every result can point backward.</h2>
        <p className="wideCopy">
          From a figure to its machine-readable table, analysis configuration, software commit,
          manifest hash, archive query and original product identifier.
        </p>
        <ProvenanceDrawer />
      </section>

      <footer>
        <div><strong>Open Exoplanet Evidence Lab</strong><span>Biswajit Jana · 2026</span></div>
        <p>Public astronomical data retain their original citation and acknowledgement requirements.</p>
      </footer>
    </main>
  )
}

export default App
