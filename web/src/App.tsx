import { motion, useReducedMotion } from "motion/react"
import { useEffect, useMemo, useState } from "react"
import ResultsSection from "./ResultsSection"
import ResearchWorkbench, {
  ProvenanceDialog,
  type LabData,
  type ProvenanceRecord,
} from "./ResearchWorkbench"

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
  ready: "Ready",
  census: "Census",
  active: "Evolving",
  wait: "Gated",
  future: "Future",
}

function PipelineFlow({ reduced }: { reduced: boolean | null }) {
  const stages = ["Archive", "Provenance", "Quality control", "Nuisance model", "Injection / recovery", "Cross-check", "Robustness"]
  return (
    <ol className="pipeline" aria-label="Scientific evidence pipeline">
      {stages.map((stage, index) => (
        <motion.li
          key={stage}
          initial={reduced ? false : { opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: reduced ? 0 : index * 0.04, duration: 0.28 }}
        >
          <span>{String(index + 1).padStart(2, "0")}</span>
          <strong>{stage}</strong>
        </motion.li>
      ))}
    </ol>
  )
}

function SourceRow({ source }: { source: Source }) {
  return (
    <article className="sourceRow">
      <div className="sourceIdentity">
        <span className={`status status-${source.status}`}>{statusLabels[source.status]}</span>
        <span className="sourceId">{source.id}</span>
      </div>
      <div>
        <h3>{source.name}</h3>
        <p className="sourceRole">{source.role}</p>
      </div>
      <p className="sourceDetail">{source.detail}</p>
    </article>
  )
}

function App() {
  const reduced = useReducedMotion()
  const [data, setData] = useState<ProjectData | null>(null)
  const [lab, setLab] = useState<LabData | null>(null)
  const [selectedProvenance, setSelectedProvenance] = useState<ProvenanceRecord | null>(null)
  const [paperMode, setPaperMode] = useState(
    () => new URL(window.location.href).searchParams.get("mode") === "paper",
  )

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + "data/project.json")
      .then((response) => {
        if (!response.ok) throw new Error("Project metadata unavailable")
        return response.json()
      })
      .then(setData)
      .catch(() => setData(null))
  }, [])

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + "data/lab.json")
      .then((response) => {
        if (!response.ok) throw new Error("Research interface data unavailable")
        return response.json()
      })
      .then((payload: LabData) => {
        if (payload.schema_version !== "1.0.0") {
          throw new Error(`Unsupported research-interface schema: ${payload.schema_version}`)
        }
        setLab(payload)
      })
      .catch(() => setLab(null))
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle("paper-mode", paperMode)
    return () => document.documentElement.classList.remove("paper-mode")
  }, [paperMode])

  function togglePaperMode() {
    const next = !paperMode
    setPaperMode(next)
    const url = new URL(window.location.href)
    if (next) url.searchParams.set("mode", "paper")
    else url.searchParams.delete("mode")
    window.history.replaceState({}, "", url)
  }

  function inspectProvenance(id: string) {
    const record = lab?.provenance.find((item) => item.id === id) ?? null
    setSelectedProvenance(record)
  }

  const sourceCounts = useMemo(() => {
    if (!data) return { usable: 0, gated: 0 }
    return {
      usable: data.sources.filter((source) => ["ready", "census", "active"].includes(source.status)).length,
      gated: data.sources.filter((source) => ["wait", "future"].includes(source.status)).length,
    }
  }, [data])

  return (
    <main>
      <a className="skipLink" href="#main-content">Skip to main content</a>

      <header className="topbar">
        <a href="#main-content" className="wordmark" aria-label="Open Exoplanet Evidence Lab home">
          <span className="mark" aria-hidden="true">O</span>
          <span>Open Exoplanet<br />Evidence Lab</span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#results">Results</a>
          <a href="#atlas">Targets</a>
          <a href="#completeness">Completeness</a>
          <a href="#provenance-index">Provenance</a>
        </nav>
        <div className="topbarActions">
          <button className="paperModeButton" onClick={togglePaperMode} aria-pressed={paperMode}>{paperMode ? "Exit paper mode" : "Paper mode"}</button>
          <a className="githubLink" href="https://github.com/Biswajit1999/open-exoplanet-discovery-lab">Repository <span aria-hidden="true">↗</span></a>
        </div>
      </header>

      <section className="hero" id="main-content">
        <div className="heroCopy">
          <p className="eyebrow">2026 public research release · Biswajit Jana</p>
          <motion.h1
            initial={reduced ? false : { opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Evidence before <em>inference.</em>
          </motion.h1>
          <p className="lede">
            An open laboratory for testing whether exoplanet conclusions survive
            instrument systematics, stellar activity, wavelength, cadence and
            independent observations.
          </p>
          <div className="heroActions">
            <a className="primaryAction" href="#results">Read the results <span aria-hidden="true">↓</span></a>
            <a className="secondaryAction" href="https://github.com/Biswajit1999/open-exoplanet-discovery-lab">Inspect the code <span aria-hidden="true">↗</span></a>
          </div>
        </div>

        <aside className="releaseNote" aria-label="Release scope">
          <div className="releaseNoteTop">
            <span>Release note / 01</span>
            <span>24 Sep 2026</span>
          </div>
          <p className="releaseQuote">“A null result is only meaningful after sensitivity has been measured.”</p>
          <dl>
            <div><dt>Usable public streams</dt><dd>{sourceCounts.usable || "—"}</dd></div>
            <div><dt>Explicitly gated streams</dt><dd>{sourceCounts.gated || "—"}</dd></div>
            <div><dt>New planet claims</dt><dd>0</dd></div>
          </dl>
          <p className="releaseBoundary">Gaia DR4 and SPORES-HWO remain gated. No result depends on unreleased data.</p>
        </aside>
      </section>

      <section className="metricRail" aria-label="Public data snapshot">
        <div><strong>41</strong><span>NETS III stars</span></div>
        <div><strong>5,920</strong><span>public RV epochs</span></div>
        <div><strong>1,826</strong><span>atmosphere records</span></div>
        <div><strong>51</strong><span>scientific tests passing</span></div>
      </section>

      <ResultsSection onInspect={inspectProvenance} />

      {lab ? <ResearchWorkbench data={lab} onInspect={inspectProvenance} /> : (
        <section className="labUnavailable" role="status">The research-interface data contract could not be loaded. The static release figures remain available above.</section>
      )}

      <section className="questionSection">
        <p className="sectionKicker">Research question</p>
        <blockquote>{data?.question ?? "How stable are exoplanet conclusions when the nuisance model changes?"}</blockquote>
        <p>
          The programme rewards robustness, not a preferred outcome. More complex models
          are useful only when they improve calibrated inference without erasing the
          astrophysical signal they were meant to protect.
        </p>
      </section>

      <section id="evidence" className="contentSection evidenceSection">
        <header className="editorialHeader">
          <div><p className="sectionKicker">Data registry</p><h2>Public evidence, with boundaries.</h2></div>
          <p>Every archive is assigned a role before analysis. Availability is not scientific compatibility.</p>
        </header>
        <div className="sourceList">
          {(data?.sources ?? []).map((source) => <SourceRow key={source.id} source={source} />)}
        </div>
      </section>

      <section id="methods" className="contentSection methodsSection">
        <header className="editorialHeader">
          <div><p className="sectionKicker">Method</p><h2>The nuisance model is part of the science.</h2></div>
          <p>Three disciplines turn archive products into defensible evidence.</p>
        </header>
        <div className="methodChapters">
          <article><span>01</span><h3>Model what changed</h3><p>Instrument eras, pipeline versions, run offsets, white jitter and activity terms are explicit inputs—not footnotes added after a detection.</p></article>
          <article><span>02</span><h3>Measure what could be found</h3><p>Permutation-calibrated injection and recovery produces completeness surfaces and K50/K90 bounds instead of anecdotal non-detections.</p></article>
          <article><span>03</span><h3>Ask independent data to disagree</h3><p>Held-out eras, later TESS sectors, alternate reductions and optical/NIR comparisons are tests of stability, not decoration.</p></article>
        </div>
        <PipelineFlow reduced={reduced} />
      </section>

      <section id="provenance" className="provenanceBlock">
        <div>
          <p className="sectionKicker">Reproducibility</p>
          <h2>Every number points backward.</h2>
        </div>
        <div className="provenanceCopy">
          <p>Figures resolve to tables; tables resolve to analysis configuration, software commit, manifest hash, archive query and original product identity.</p>
          <ol>
            <li><span>01</span> Archive product and checksum</li>
            <li><span>02</span> Reduction, observing mode and quality state</li>
            <li><span>03</span> Configuration hash and software commit</li>
            <li><span>04</span> Measured, fitted, simulated or literature result state</li>
          </ol>
          <a href="https://github.com/Biswajit1999/open-exoplanet-discovery-lab">Open the reproducible repository <span aria-hidden="true">↗</span></a>
        </div>
      </section>

      <footer>
        <div><strong>Open Exoplanet Evidence Lab</strong><span>Biswajit Jana · independent open science</span></div>
        <p>Public astronomical data retain their original citation and acknowledgement requirements.</p>
      </footer>
      <ProvenanceDialog record={selectedProvenance} onClose={() => setSelectedProvenance(null)} />
    </main>
  )
}

export default App
