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
  atmosphere_retrieval?: {
    hansolo_mean_temperature_k: number
    stark_mean_temperature_k: number
    median_same_visit_temperature_difference_k: number
    hansolo_extra_inter_visit_scatter_k: number
    stark_extra_inter_visit_scatter_k: number
    maximum_leave_one_visit_out_predictive_z: number
    blackbody_preferred_spectra: number
    spectral_retrievals: number
  }
  eso_census?: {
    nirps_products: number
    nirps_targets: number
    harps_matches: number
    simultaneous_1h: number
    simultaneous_1d: number
    query_errors: number
  }
  spores_hwo?: {
    catalog_targets: number
    raw_rv_rows: number
    control_targets: number
    control_nightly_rvs: number
    published_middle_hz_median_m50_earth: number
    median_reference_k50_mps: number
    eccentric_to_circular_k50_ratio: number
    global_to_instrument_correlated_k50_ratio: number
    leave_dominant_to_full_k50_ratio: number
    null_permutations_per_model: number
    orbital_draws_per_amplitude: number
    nasa_confirmed_planet_context_targets: number
  }
  spores_tess?: {
    all_catalog_matches: number
    control_matches: number
    control_resolved_tic_ids: number
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

export default function ResultsSection({ onInspect }: { onInspect: (id: string) => void }) {
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

  return (
    <section className="resultsSection" id="results">
      <header className="resultsMasthead">
        <div>
          <p className="sectionKicker">Validated results · {data.snapshot_date}</p>
          <h2>What changed when the assumptions changed?</h2>
        </div>
        <p>
          Five completed public-data experiments. No new-planet claim; every
          number is bounded by an explicit model and provenance record.
        </p>
      </header>

      <div className="snapshotStrip">
        <div><span>SPORES-HWO raw RVs</span><strong>{data.spores_hwo?.raw_rv_rows.toLocaleString() ?? "—"}</strong></div>
        <div><span>SPORES control sample</span><strong>{data.spores_hwo?.control_targets ?? "—"}<small> stars</small></strong></div>
        <div><span>Atmosphere targets</span><strong>{data.atmosphere.planets}<small> planets</small></strong></div>
        <div><span>Cross-publication spectra</span><strong>{data.atmosphere.multi_publication}<small> targets</small></strong></div>
      </div>

      {data.spores_hwo && (
        <motion.article
          className="leadFinding"
          initial={reduced ? false : { opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
        >
          <div className="findingNarrative">
            <p className="findingNumber">Finding 01 / SPORES-HWO II</p>
            <h3>Habitable-zone sensitivity moves when the noise and instrument assumptions move.</h3>
            <p>
              A pre-declared {data.spores_hwo.control_targets}-star control sample contributes {data.spores_hwo.control_nightly_rvs.toLocaleString()} valid nightly RV epochs.
              Under instrument offsets and a correlation-preserving null, the median middle-HZ K50 is <strong>{data.spores_hwo.median_reference_k50_mps.toFixed(2)} m s⁻¹</strong>.
              Eccentric injections change that threshold by a median factor of {data.spores_hwo.eccentric_to_circular_k50_ratio.toFixed(2)}, while removing the dominant instrument changes it by {data.spores_hwo.leave_dominant_to_full_k50_ratio.toFixed(2)}.
            </p>
            <dl className="findingStats">
              <div><dt>Empirical null permutations</dt><dd>{data.spores_hwo.null_permutations_per_model}</dd></div>
              <div><dt>Orbital geometries / amplitude</dt><dd>{data.spores_hwo.orbital_draws_per_amplitude}</dd></div>
              <div><dt>Catalogued median middle-HZ M50</dt><dd>{data.spores_hwo.published_middle_hz_median_m50_earth.toFixed(1)} M⊕</dd></div>
              {data.spores_tess && <div><dt>Control stars in TESS-SVC</dt><dd>{data.spores_tess.control_matches} / {data.spores_tess.control_resolved_tic_ids}</dd></div>}
            </dl>
            <p className="scopeNote">Sensitivity analysis only. The control sample excludes SPORES table-6 signals but is not planet-free: {data.spores_hwo.nasa_confirmed_planet_context_targets} stars have NASA confirmed-planet context. No companion candidate is emitted; TESS-SVC matches are not rotation labels.</p>
            <button className="provenanceTrigger" onClick={() => onInspect("spores-hwo-robustness")}>Inspect provenance <span aria-hidden="true">→</span></button>
          </div>
          <Figure
            number="01"
            src="figures/spores_k50_assumption_robustness.png"
            alt="Per-target middle-habitable-zone K50 ratios across global, instrument-aware, correlated-noise, eccentric, and dominant-instrument-removal models"
            caption="Each line is one pre-declared control star. Ratios are referenced to the instrument-aware circular model with a correlation-preserving empirical null."
          />
        </motion.article>
      )}

      {data.nets_completeness && (
        <motion.article
          className="leadFinding"
          initial={reduced ? false : { opacity: 0, y: 14 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
        >
          <div className="findingNarrative">
            <p className="findingNumber">Finding 02 / NETS III</p>
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
            <button className="provenanceTrigger" onClick={() => onInspect("nets3-completeness")}>Inspect provenance <span aria-hidden="true">→</span></button>
          </div>
          <Figure
            number="02"
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
              <p className="findingNumber">Finding 03 / TESS</p>
              <h3>A strong analytic peak does not survive a time-correlated null.</h3>
              <p>
                {data.tess.target} shows peaks at {data.tess.control_period_days.toFixed(2)} d and {data.tess.test_period_days.toFixed(2)} d.
                Sector-preserving circular shifts give p = {data.tess.control_circular_shift_pvalue.toFixed(3)} for the control and p = {data.tess.test_circular_shift_pvalue.toFixed(3)} for the later test.
              </p>
              <p className="scopeNote">Activity context only: neither a planet confirmation nor a secure stellar-rotation measurement.</p>
              <button className="provenanceTrigger" onClick={() => onInspect("tess-hd10780")}>Inspect provenance <span aria-hidden="true">→</span></button>
            </div>
            <Figure
              number="03"
              src="figures/tess_temporal_context.png"
              alt="HD 10780 TESS control and test light curves with generalized Lomb-Scargle periodograms"
              caption="Control sectors 24–25 and test sectors 85–86. The empirical circular-shift calibration preserves within-sector ordering."
            />
          </article>
        )}

        {data.atmosphere_reproducibility && data.atmosphere_retrieval && (
          <article className="secondaryFinding">
            <div className="secondaryCopy">
              <p className="findingNumber">Finding 04 / atmosphere</p>
              <h3>The thermal retrieval changes materially with reduction and visit.</h3>
              <p>
                Five public {data.atmosphere_reproducibility.target} visits have a median absolute HANSOLO–stark
                common-band difference of <strong>{data.atmosphere_reproducibility.median_absolute_pipeline_difference_ppm.toFixed(1)} ppm</strong>.
                Their blackbody fits differ by a median <strong>{Math.abs(data.atmosphere_retrieval.median_same_visit_temperature_difference_k).toFixed(0)} K</strong> for the same visits;
                random-effects fits require {data.atmosphere_retrieval.hansolo_extra_inter_visit_scatter_k.toFixed(0)} K and {data.atmosphere_retrieval.stark_extra_inter_visit_scatter_k.toFixed(0)} K of extra visit scatter.
              </p>
              <dl className="findingStats compactStats">
                <div><dt>HANSOLO mean brightness T</dt><dd>{data.atmosphere_retrieval.hansolo_mean_temperature_k.toFixed(0)} K</dd></div>
                <div><dt>stark mean brightness T</dt><dd>{data.atmosphere_retrieval.stark_mean_temperature_k.toFixed(0)} K</dd></div>
                <div><dt>Blackbody BIC preference</dt><dd>{data.atmosphere_retrieval.blackbody_preferred_spectra} / {data.atmosphere_retrieval.spectral_retrievals}</dd></div>
                <div><dt>Max leave-one-visit-out |z|</dt><dd>{data.atmosphere_retrieval.maximum_leave_one_visit_out_predictive_z.toFixed(2)}</dd></div>
              </dl>
              <p className="scopeNote">Brightness-temperature and model-adequacy test only. The reductions share photons and the narrow band lacks published spectral covariance, so no molecular-abundance or unique-composition posterior is reported.</p>
              <button className="provenanceTrigger" onClick={() => onInspect("atmosphere-55cnce")}>Inspect provenance <span aria-hidden="true">→</span></button>
            </div>
            <Figure
              number="04"
              src="figures/atmosphere_retrieval_validation.png"
              alt="55 Cnc e blackbody brightness temperatures and model-comparison BIC differences across five visits and two reductions"
              caption="Visit-level blackbody fits from the same photons shift with reduction. Negative BIC differences favour a blackbody over a constant spectrum, but do not identify composition."
            />
          </article>
        )}
      </div>

      {data.eso_census && (
        <section className="censusBand" aria-labelledby="census-heading">
          <div className="censusIntro">
            <p className="findingNumber">Finding 05 / ESO census</p>
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
          <button className="provenanceTrigger" onClick={() => onInspect("eso-nirps-harps")}>Inspect provenance <span aria-hidden="true">→</span></button>
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
            <tr><td>SPORES-HWO II</td><td>Measured sensitivity robustness</td><td>target_k50_k90.csv</td><td>No companion classification</td></tr>
            <tr><td>SPORES × TESS-SVC</td><td>Exact-identity variability context</td><td>control_sample_tess_context.csv</td><td>No rotation or quiet-star label</td></tr>
            <tr><td>NETS III</td><td>Measured sensitivity</td><td>target_completeness.csv</td><td>No candidate classification</td></tr>
            <tr><td>TESS / HD 10780</td><td>Temporal activity context</td><td>summary.json</td><td>No planet or rotation claim</td></tr>
            <tr><td>55 Cnc e</td><td>Bounded thermal retrieval</td><td>visit_thermal_retrievals.csv</td><td>No abundance or unique-composition claim</td></tr>
            <tr><td>NIRPS × HARPS</td><td>Archive census</td><td>nirps_harps_overlap_summary.csv</td><td>No chromatic RV claim yet</td></tr>
            <tr><td>Gaia DR4</td><td>Gated</td><td>None emitted</td><td>Required data unavailable</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  )
}
