import { motion, useReducedMotion } from "motion/react"
import { useEffect, useState } from "react"

type ResultsData = {
  snapshot_date: string
  nets3: {
    targets: number
    rv_rows: number
    median_epochs: number
    median_baseline_days: number
    median_internal_error_mps: number
    median_raw_wrms_mps: number
    median_era_demeaned_wrms_mps: number
  }
  hd190360: {
    epochs: number
    baseline_days: number
    fixed_period_days: number
    neid_only_k_mps: number
    published_context_k_mps: number
  }
  atmosphere: {
    spectra: number
    planets: number
    multi_spectrum: number
    multi_publication: number
    multi_instrument: number
  }
}

function Metric({ value, label, note }: { value: string; label: string; note?: string }) {
  return (
    <article className="resultMetric">
      <strong>{value}</strong>
      <h3>{label}</h3>
      {note && <p>{note}</p>}
    </article>
  )
}

export default function ResultsSection() {
  const reduced = useReducedMotion()
  const [data, setData] = useState<ResultsData | null>(null)

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + "data/results.json")
      .then((response) => {
        if (!response.ok) throw new Error("Results snapshot unavailable")
        return response.json()
      })
      .then(setData)
      .catch(() => setData(null))
  }, [])

  if (!data) return null
  const reduction =
    100 * (1 - data.nets3.median_era_demeaned_wrms_mps / data.nets3.median_raw_wrms_mps)

  return (
    <section className="contentSection resultsSection" id="results">
      <div className="sectionHeader">
        <div>
          <p className="sectionKicker">Measured public-data snapshot · {data.snapshot_date}</p>
          <h2>What the current archive run contains</h2>
        </div>
        <p className="resultsCaveat">
          Descriptive and baseline-model results only. No new-planet claim is made.
        </p>
      </div>

      <div className="resultGrid">
        <Metric
          value={data.nets3.targets.toString()}
          label="NETS III stars"
          note={data.nets3.rv_rows.toLocaleString() + " public RV measurements"}
        />
        <Metric
          value={data.nets3.median_epochs.toFixed(0)}
          label="Median RV epochs"
          note={"median baseline " + data.nets3.median_baseline_days.toFixed(0) + " d"}
        />
        <Metric
          value={data.nets3.median_internal_error_mps.toFixed(2) + " m s⁻¹"}
          label="Median quoted internal uncertainty"
          note="NETS III public time series"
        />
        <Metric
          value={reduction.toFixed(1) + "%"}
          label="Median WRMS change after run de-meaning"
          note={data.nets3.median_raw_wrms_mps.toFixed(2) + " → " + data.nets3.median_era_demeaned_wrms_mps.toFixed(2) + " m s⁻¹"}
        />
        <Metric
          value={data.atmosphere.spectra.toLocaleString()}
          label="Atmospheric spectrum records"
          note={data.atmosphere.planets + " unique planets"}
        />
        <Metric
          value={data.atmosphere.multi_instrument.toString()}
          label="Multi-instrument atmosphere targets"
          note={data.atmosphere.multi_publication + " span multiple publications"}
        />
      </div>

      <motion.article
        className="stressTest"
        initial={reduced ? false : { opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
      >
        <div>
          <p className="sectionKicker">Model-adequacy stress test</p>
          <h3>HD 190360 · fixed 88.69 d NEID-only control</h3>
        </div>
        <div className="stressNumbers">
          <div><small>simple model</small><strong>{data.hd190360.neid_only_k_mps.toFixed(3)} m s⁻¹</strong></div>
          <div><small>published context</small><strong>{data.hd190360.published_context_k_mps.toFixed(2)} m s⁻¹</strong></div>
        </div>
        <p>
          The deliberately restricted circular NEID-only fit does not reproduce the
          published multi-instrument/multi-planet amplitude. That difference is retained
          as a model-adequacy warning: a precise-looking fit can remain incomplete when
          long-baseline structure and additional signals are omitted.
        </p>
      </motion.article>
    </section>
  )
}
