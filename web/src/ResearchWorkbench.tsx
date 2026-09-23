import { useEffect, useMemo, useRef, useState } from "react"

export type ProvenanceRecord = {
  id: string
  title: string
  claim_label: string
  evidence_state: string
  archive: string
  source_id: string
  generated_at_utc: string
  software_commit: string | null
  configuration_hash: string
  primary_output: string
  checksum_record: string
  boundary: string
}

type TargetRecord = {
  id: string
  target: string
  observations: number
  runs: number
  baseline_days: number
  median_formal_error_mps: number
  mean_completeness: Record<string, number>
  mean_delta_era_activity_minus_baseline: number
  power_thresholds: Record<string, number>
}

type PopulationCell = {
  model: string
  period_days: number
  semi_amplitude_mps: number
  mean_completeness: number
  median_completeness: number
  targets: number
}

type DeltaCell = {
  period_days: number
  semi_amplitude_mps: number
  delta_completeness: number
}

type KThreshold = {
  model: string
  period_days: number
  k50_mps: number | null
  k90_mps: number | null
}

type TransferRecord = {
  period_days: number
  median_transfer: number
  worst_phase_median: number
}

type LiteratureGate = {
  stream: string
  status: string
  increment: string
  excluded_claim: string
}

export type LabData = {
  schema_version: string
  release: string
  snapshot_date: string
  targets: TargetRecord[]
  completeness: {
    models: string[]
    population: PopulationCell[]
    delta: DeltaCell[]
    k_thresholds: KThreshold[]
    leave_one_era_out: TransferRecord[]
  }
  provenance: ProvenanceRecord[]
  literature_gates: LiteratureGate[]
}

const REPOSITORY = "https://github.com/Biswajit1999/open-exoplanet-discovery-lab"

function updateUrl(values: Record<string, string | null>, hash: string) {
  const url = new URL(window.location.href)
  for (const [key, value] of Object.entries(values)) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  url.hash = hash
  window.history.replaceState({}, "", url)
}

function modelName(model: string) {
  if (model === "baseline") return "Global offset"
  if (model === "era") return "Run offsets"
  if (model === "era_activity") return "Run + activity"
  return "Δ run+activity − baseline"
}

function completenessClass(value: number) {
  return `heat-${Math.min(5, Math.max(0, Math.floor(value * 6)))}`
}

function deltaClass(value: number) {
  const magnitude = Math.min(3, Math.ceil(Math.abs(value) / 0.12))
  if (magnitude === 0) return "delta-zero"
  return value > 0 ? `delta-positive-${magnitude}` : `delta-negative-${magnitude}`
}

function TargetAtlas({ targets }: { targets: TargetRecord[] }) {
  const initialTarget = new URL(window.location.href).searchParams.get("target")
  const defaultTarget = [...targets].sort((left, right) => right.observations - left.observations)[0]?.id
  const [query, setQuery] = useState("")
  const [sort, setSort] = useState("observations")
  const [expanded, setExpanded] = useState(false)
  const [selectedId, setSelectedId] = useState(
    targets.some((target) => target.id === initialTarget) ? initialTarget! : defaultTarget,
  )

  const filtered = useMemo(() => {
    const visible = targets.filter((target) =>
      target.target.toLowerCase().includes(query.trim().toLowerCase()),
    )
    return visible.sort((left, right) => {
      if (sort === "precision") return left.median_formal_error_mps - right.median_formal_error_mps
      if (sort === "delta") {
        return Math.abs(right.mean_delta_era_activity_minus_baseline) - Math.abs(left.mean_delta_era_activity_minus_baseline)
      }
      return right.observations - left.observations
    })
  }, [query, sort, targets])

  const selected = targets.find((target) => target.id === selectedId) ?? filtered[0]
  const visibleTargets = expanded || query.trim() ? filtered : filtered.slice(0, 12)

  function selectTarget(target: TargetRecord) {
    setSelectedId(target.id)
    updateUrl({ target: target.id }, "atlas")
  }

  return (
    <section className="labModule atlasModule" id="atlas" aria-labelledby="atlas-title">
      <header className="moduleHeader">
        <div>
          <p className="sectionKicker">Target atlas / NETS III</p>
          <h2 id="atlas-title">Forty sensitivity experiments, not one average star.</h2>
        </div>
        <p>Search the frozen analysis sample and inspect the observation geometry behind each target-level completeness surface.</p>
      </header>

      <div className="atlasControls">
        <label>
          <span>Find a target</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} type="search" placeholder="HD 10780" />
        </label>
        <label>
          <span>Order by</span>
          <select value={sort} onChange={(event) => setSort(event.target.value)}>
            <option value="observations">Most observations</option>
            <option value="precision">Best formal precision</option>
            <option value="delta">Largest model sensitivity</option>
          </select>
        </label>
        <p aria-live="polite">{filtered.length} of {targets.length} targets shown</p>
      </div>

      <div className="atlasLayout">
        <div className="targetList" aria-label="NETS III targets">
          {visibleTargets.map((target) => (
            <button
              className={target.id === selected?.id ? "targetRow is-selected" : "targetRow"}
              key={target.id}
              onClick={() => selectTarget(target)}
              aria-pressed={target.id === selected?.id}
            >
              <span><strong>{target.target}</strong><small>{target.observations} epochs · {target.runs} runs</small></span>
              <span>{target.median_formal_error_mps.toFixed(2)}<small>m s⁻¹</small></span>
            </button>
          ))}
          {filtered.length === 0 && <p className="emptyState">No target matches that search.</p>}
          {!query.trim() && filtered.length > 12 && (
            <button className="showTargets" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>
              {expanded ? "Show fewer targets" : `Show all ${filtered.length} targets`}
            </button>
          )}
        </div>

        {selected && (
          <article className="targetDetail" aria-live="polite">
            <div className="targetDetailTop">
              <div><p className="findingNumber">Selected target</p><h3>{selected.target}</h3></div>
              <span className="evidencePill">Sensitivity record</span>
            </div>
            <dl className="targetMetrics">
              <div><dt>Observations</dt><dd>{selected.observations}</dd></div>
              <div><dt>Instrument runs</dt><dd>{selected.runs}</dd></div>
              <div><dt>Baseline</dt><dd>{selected.baseline_days.toFixed(1)} d</dd></div>
              <div><dt>Median formal error</dt><dd>{selected.median_formal_error_mps.toFixed(2)} m s⁻¹</dd></div>
            </dl>
            <div className="targetComparison">
              <p><span>Global-offset mean recovery</span><strong>{(100 * selected.mean_completeness.baseline).toFixed(1)}%</strong></p>
              <p><span>Run + activity mean recovery</span><strong>{(100 * selected.mean_completeness.era_activity).toFixed(1)}%</strong></p>
              <p><span>Mean model shift</span><strong>{selected.mean_delta_era_activity_minus_baseline >= 0 ? "+" : ""}{selected.mean_delta_era_activity_minus_baseline.toFixed(3)}</strong></p>
            </div>
            <p className="scopeNote">A target-level recovery fraction describes the declared injection grid. It is not a planet probability.</p>
            <a className="textLink" href={`${REPOSITORY}/tree/main/results/nets3_completeness_2026-09-23/figures/targets`}>Open target figures <span aria-hidden="true">↗</span></a>
          </article>
        )}
      </div>
    </section>
  )
}

function CompletenessLab({ data }: { data: LabData["completeness"] }) {
  const queryModel = new URL(window.location.href).searchParams.get("model")
  const initialModel = [...data.models, "delta"].includes(queryModel ?? "") ? queryModel! : "era_activity"
  const [model, setModel] = useState(initialModel)
  const periods = [...new Set(data.population.map((row) => row.period_days))]
  const amplitudes = [...new Set(data.population.map((row) => row.semi_amplitude_mps))]

  function changeModel(next: string) {
    setModel(next)
    updateUrl({ model: next }, "completeness")
  }

  function valueAt(period: number, amplitude: number) {
    if (model === "delta") {
      return data.delta.find((row) => row.period_days === period && row.semi_amplitude_mps === amplitude)?.delta_completeness ?? 0
    }
    return data.population.find((row) => row.model === model && row.period_days === period && row.semi_amplitude_mps === amplitude)?.mean_completeness ?? 0
  }

  const thresholds = data.k_thresholds.filter((row) => row.model === (model === "delta" ? "era_activity" : model))

  return (
    <section className="labModule completenessModule" id="completeness" aria-labelledby="completeness-title">
      <header className="moduleHeader">
        <div>
          <p className="sectionKicker">Completeness laboratory</p>
          <h2 id="completeness-title">Read the sensitivity surface cell by cell.</h2>
        </div>
        <label className="modelSelect"><span>Displayed model</span><select value={model} onChange={(event) => changeModel(event.target.value)}>
          {data.models.map((name) => <option key={name} value={name}>{modelName(name)}</option>)}
          <option value="delta">Δ run+activity − baseline</option>
        </select></label>
      </header>

      <div className="completenessLayout">
        <div className="heatmapWrap" role="region" aria-label={`${modelName(model)} completeness grid`} tabIndex={0}>
          <table className={model === "delta" ? "heatmap deltaHeatmap" : "heatmap"}>
            <caption>{modelName(model)} · values are {model === "delta" ? "change in recovery fraction" : "population mean recovery fraction"}</caption>
            <thead><tr><th scope="col">K / P</th>{periods.map((period) => <th key={period} scope="col">{period} d</th>)}</tr></thead>
            <tbody>
              {amplitudes.map((amplitude) => <tr key={amplitude}>
                <th scope="row">{amplitude} m s⁻¹</th>
                {periods.map((period) => {
                  const value = valueAt(period, amplitude)
                  return <td key={period} className={model === "delta" ? deltaClass(value) : completenessClass(value)}>
                    {model === "delta" && value > 0 ? "+" : ""}{value.toFixed(2)}
                  </td>
                })}
              </tr>)}
            </tbody>
          </table>
        </div>

        <aside className="thresholdPanel">
          <p className="findingNumber">Population threshold</p>
          <h3>{model === "delta" ? "Run + activity K50" : `${modelName(model)} K50`}</h3>
          <div className="thresholdList">
            {thresholds.map((row) => <p key={row.period_days}><span>{row.period_days} d</span><strong>{row.k50_mps === null ? "not reached" : `${row.k50_mps.toFixed(2)} m s⁻¹`}</strong></p>)}
          </div>
          <p className="scopeNote">K90 is not shown as a number because the 0.5–5 m s⁻¹ grid does not bracket 90% population recovery.</p>
        </aside>
      </div>

      <div className="transferStrip" aria-label="Leave-one-era-out signal transfer">
        <div><p className="findingNumber">Held-out-era transfer</p><h3>How much injected amplitude survives nuisance projection?</h3></div>
        {data.leave_one_era_out.map((row) => <div key={row.period_days}>
          <span>{row.period_days} d</span><strong>{(100 * row.median_transfer).toFixed(1)}%</strong><small>worst-phase median {(100 * row.worst_phase_median).toFixed(1)}%</small>
        </div>)}
      </div>
    </section>
  )
}

function LiteratureGate({ records }: { records: LiteratureGate[] }) {
  return (
    <section className="labModule literatureModule" id="literature" aria-labelledby="literature-title">
      <header className="moduleHeader"><div><p className="sectionKicker">Literature gate</p><h2 id="literature-title">The incremental claim is narrower than the dataset.</h2></div><p>Each stream declares what this release adds and what it explicitly does not claim.</p></header>
      <div className="literatureGrid">
        {records.map((record) => <article key={record.stream}>
          <div><span>{record.status}</span><h3>{record.stream}</h3></div>
          <p>{record.increment}</p>
          <p className="excludedClaim"><strong>Excluded claim</strong>{record.excluded_claim}</p>
        </article>)}
      </div>
    </section>
  )
}

function ProvenanceIndex({ records, onInspect }: { records: ProvenanceRecord[]; onInspect: (id: string) => void }) {
  return (
    <section className="labModule provenanceIndex" id="provenance-index" aria-labelledby="provenance-index-title">
      <header className="moduleHeader"><div><p className="sectionKicker">Provenance inspector</p><h2 id="provenance-index-title">Four results, four explicit evidence states.</h2></div><p>Open a record to trace the result to its archive, configuration, software commit and checksum manifest.</p></header>
      <div className="provenanceGrid">
        {records.map((record, index) => <article id={`provenance-${record.id}`} key={record.id}>
          <div className="recordNumber">0{index + 1}</div>
          <p className="findingNumber">{record.claim_label}</p>
          <h3>{record.title}</h3>
          <p>{record.evidence_state}</p>
          <button onClick={() => onInspect(record.id)}>Inspect provenance <span aria-hidden="true">→</span></button>
        </article>)}
      </div>
    </section>
  )
}

export function ProvenanceDialog({ record, onClose }: { record: ProvenanceRecord | null; onClose: () => void }) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (record && !dialog.open) dialog.showModal()
    if (!record && dialog.open) dialog.close()
  }, [record])

  return (
    <dialog className="provenanceDialog" ref={dialogRef} onClose={onClose} aria-labelledby="provenance-dialog-title">
      {record && <>
        <div className="dialogTop"><p>{record.claim_label}</p><button onClick={() => dialogRef.current?.close()} aria-label="Close provenance record">Close</button></div>
        <h2 id="provenance-dialog-title">{record.title}</h2>
        <p className="dialogBoundary">{record.boundary}</p>
        <dl>
          <div><dt>Evidence state</dt><dd>{record.evidence_state}</dd></div>
          <div><dt>Archive</dt><dd>{record.archive}</dd></div>
          <div><dt>Source identity</dt><dd>{record.source_id}</dd></div>
          <div><dt>Generated</dt><dd>{new Date(record.generated_at_utc).toISOString()}</dd></div>
          <div><dt>Science commit</dt><dd><code>{record.software_commit ?? "recorded in archive manifest"}</code></dd></div>
          <div><dt>Configuration / manifest hash</dt><dd><code>{record.configuration_hash}</code></dd></div>
        </dl>
        <div className="dialogLinks">
          <a href={`${REPOSITORY}/blob/main/${record.primary_output}`}>Primary output <span aria-hidden="true">↗</span></a>
          <a href={`${REPOSITORY}/blob/main/${record.checksum_record}`}>Checksum record <span aria-hidden="true">↗</span></a>
        </div>
      </>}
    </dialog>
  )
}

export default function ResearchWorkbench({ data, onInspect }: { data: LabData; onInspect: (id: string) => void }) {
  return (
    <div className="researchWorkbench">
      <section className="workbenchIntro" aria-labelledby="workbench-title">
        <p className="sectionKicker">Research interface / release {data.release}</p>
        <h2 id="workbench-title">Move from the headline to the evidence.</h2>
        <p>The interface below is a read-only view of schema {data.schema_version}, generated from the frozen machine-readable release rather than recalculated in the browser.</p>
      </section>
      <TargetAtlas targets={data.targets} />
      <CompletenessLab data={data.completeness} />
      <LiteratureGate records={data.literature_gates} />
      <ProvenanceIndex records={data.provenance} onInspect={onInspect} />
    </div>
  )
}
