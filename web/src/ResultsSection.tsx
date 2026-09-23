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
  nets_completeness?: {
    targets: number
    models: string[]
    mean_delta_completeness: number
    max_absolute_delta_completeness: number
    permutations_per_target_model: number
  }
  tess?: {
    target: string
    control_period_days: number
    test_period_days: number
    control_circular_shift_pvalue: number
    test_circular_shift_pvalue: number
    phase_difference_radians: number
  }
  atmosphere_reproducibility?: {
    target: string
    visits: number
    products: number
    median_absolute_pipeline_difference_ppm: number
    hansolo_extra_scatter_ppm: number
    stark_extra_scatter_ppm: number
  }
  eso_census?: {
    nirps_products: number
    nirps_targets: number
    harps_matches: number
    simultaneous_1h: number
    simultaneous_1d: number
    query_errors: number
  }
}

function Figure({ src, alt, caption, number }: { src: string; alt: string; caption: string; number: string }) {
  return (
    <figure className="evidenceFigure">
      <div className="figureChrome"><span>Figure {number}</span><span>Public-data result</span></div>
      <img src={import.meta.env.BASE_URL + src} alt={alt} loading="lazy" />
      <figcaption>{caption}</figcaption>
    </figure>
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
  const wrmsReduction = 100 * (1 - data.nets3.median_era_demeaned_wrms_mps / data.nets3.median_raw_wrms_mps)

  return (
    <section className="resultsSection" id="results">
      <header className="resultsMasthead">
        <div>
          <p className="sectionKicker">Validated results · {data.snapshot_date}</p>
          <h2>What changed when the assumptions changed?</h2>
        </div>
        <p>
          Three completed public-data experiments. No new-planet claim; every
          number is bounded by an explicit model and provenance record.
        </p>
      </header>

      <div className="snapshotStrip">
        <div><span>Median RV precision</span><strong>{data.nets3.median_internal_error_mps.toFixed(2)} <small>m s⁻¹</small></strong></div>
        <div><span>Median run de-meaning change</span><strong>{wrmsReduction.toFixed(1)}<small>%</small></strong></div>
        <div><span>Atmosphere targets</span><strong>{data.atmosphere.planets}<small> planets</small></strong></div>
        <div><span>Cross-publication spectra</span><strong>{data.atmosphere.multi_publication}<small> targets</small></strong></div>
      </div>

      {data.nets_completeness && (
        <motion.article
          className="leadFinding"
          initial={reduced ? false : { opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
        >
          <div className="findingNarrative">
            <p className="findingNumber">Finding 01 / NETS III</p>
            <h3>Nuisance modelling changes the sensitivity map—not simply the noise floor.</h3>
            <p>
              Across {data.nets_completeness.targets} stars with complete activity rows,
              the era-and-activity model changes mean completeness by only <strong>{data.nets_completeness.mean_delta_completeness.toFixed(3)}</strong> overall.
              That average hides a strongly period-dependent result: short-period recovery improves,
              while the same model absorbs substantial sensitivity near 500 days.
            </p>
            <dl className="findingStats">
              <div><dt>Largest |ΔC| grid cell</dt><dd>{data.nets_completeness.max_absolute_delta_completeness.toFixed(3)}</dd></div>
              <div><dt>Noise models compared</dt><dd>{data.nets_completeness.models.length}</dd></div>
              <div><dt>Permutations / star / model</dt><dd>{data.nets_completeness.permutations_per_target_model}</dd></div>
            </dl>
            <p className="scopeNote">Interpretation: sensitivity measurement from circular injections. A recovered period is not classified as a planet.</p>
          </div>
          <Figure
            number="01"
            src="figures/nets3_population_completeness.png"
            alt="NETS III population completeness heatmaps for baseline and era plus activity nuisance models, with their difference"
            caption="Population recovery fraction under the baseline and era-plus-activity models. The right panel is their difference; red improves recovery and blue reduces it."
          />
        </motion.article>
      )}

      <div className="pairedFindings">
        {data.tess && (
          <article className="secondaryFinding">
            <div className="secondaryCopy">
              <p className="findingNumber">Finding 02 / TESS</p>
              <h3>A strong analytic peak does not survive a time-correlated null.</h3>
              <p>
                {data.tess.target} shows peaks at {data.tess.control_period_days.toFixed(2)} d and {data.tess.test_period_days.toFixed(2)} d.
                Sector-preserving circular shifts give p = {data.tess.control_circular_shift_pvalue.toFixed(3)} for the control and p = {data.tess.test_circular_shift_pvalue.toFixed(3)} for the later test.
              </p>
              <p className="scopeNote">Activity context only: neither a planet confirmation nor a secure stellar-rotation measurement.</p>
            </div>
            <Figure
              number="02"
              src="figures/tess_temporal_context.png"
              alt="HD 10780 TESS control and test light curves with generalized Lomb-Scargle periodograms"
              caption="Control sectors 24–25 and test sectors 85–86. The empirical circular-shift calibration preserves within-sector ordering."
            />
          </article>
        )}

        {data.atmosphere_reproducibility && (
          <article className="secondaryFinding">
            <div className="secondaryCopy">
              <p className="findingNumber">Finding 03 / atmosphere</p>
              <h3>The reduction pipeline is a measurable part of the eclipse result.</h3>
              <p>
                Five public {data.atmosphere_reproducibility.target} visits have a median absolute HANSOLO–stark
                common-band difference of <strong>{data.atmosphere_reproducibility.median_absolute_pipeline_difference_ppm.toFixed(1)} ppm</strong>.
                Fitted inter-visit scatter is {data.atmosphere_reproducibility.hansolo_extra_scatter_ppm.toFixed(1)} ppm and {data.atmosphere_reproducibility.stark_extra_scatter_ppm.toFixed(1)} ppm, respectively.
              </p>
              <p className="scopeNote">The reductions share photons and lack published spectral covariance; no independent-pipeline significance is claimed.</p>
            </div>
            <Figure
              number="03"
              src="figures/atmosphere_reproducibility.png"
              alt="55 Cnc e eclipse depths across five visits for HANSOLO and stark reductions and two broadband wavelengths"
              caption="Alternate reductions of the same NIRCam visits at left; independent broadband visit measurements at right."
            />
          </article>
        )}
      </div>

      {data.eso_census && (
        <section className="censusBand" aria-labelledby="census-heading">
          <div className="censusIntro">
            <p className="findingNumber">Finding 04 / ESO census</p>
            <h3 id="census-heading">The public optical/NIR overlap is large enough for a targeted coherence programme.</h3>
            <p>
              This is an archive-product census, not a homogeneous RV comparison.
              Product-level DRS and PROCSOFT verification remains mandatory before precision-RV use.
            </p>
          </div>
          <dl>
            <div><dt>Public NIRPS products</dt><dd>{data.eso_census.nirps_products.toLocaleString()}</dd></div>
            <div><dt>Archive target identities</dt><dd>{data.eso_census.nirps_targets.toLocaleString()}</dd></div>
            <div><dt>With HARPS products</dt><dd>{data.eso_census.harps_matches.toLocaleString()}</dd></div>
            <div><dt>With a ≤1 h epoch pair</dt><dd>{data.eso_census.simultaneous_1h.toLocaleString()}</dd></div>
          </dl>
          <p className="censusFoot">Complete live TAP run · {data.eso_census.query_errors} query errors · target labels are archive identities, not a deduplicated stellar catalogue.</p>
        </section>
      )}

      <aside className="modelWarning">
        <div><p className="findingNumber">Model-adequacy control</p><h3>HD 190360</h3></div>
        <p>
          A deliberately restricted NEID-only circular fit at {data.hd190360.fixed_period_days.toFixed(2)} d returns
          K = <strong>{data.hd190360.neid_only_k_mps.toFixed(3)} m s⁻¹</strong>, versus
          <strong> {data.hd190360.published_context_k_mps.toFixed(2)} m s⁻¹</strong> in the published multi-instrument context.
          The discrepancy is retained as a warning—not presented as a revised planet amplitude.
        </p>
      </aside>

      <div className="resultTableWrap" role="region" aria-label="Machine-readable result index" tabIndex={0}>
        <table>
          <caption>Machine-readable result index</caption>
          <thead><tr><th>Experiment</th><th>Evidence state</th><th>Primary output</th><th>Claim boundary</th></tr></thead>
          <tbody>
            <tr><td>NETS III</td><td>Measured sensitivity</td><td>target_completeness.csv</td><td>No candidate classification</td></tr>
            <tr><td>TESS / HD 10780</td><td>Temporal activity context</td><td>summary.json</td><td>No planet or rotation claim</td></tr>
            <tr><td>55 Cnc e</td><td>Reproducibility diagnostic</td><td>common_band_visit_means.csv</td><td>No composition claim</td></tr>
            <tr><td>NIRPS × HARPS</td><td>Archive census</td><td>nirps_harps_overlap_summary.csv</td><td>No chromatic RV claim yet</td></tr>
            <tr><td>Gaia DR4 / SPORES-HWO</td><td>Gated</td><td>None emitted</td><td>Required data unavailable</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  )
}
