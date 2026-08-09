# Label Dataset Schema v0.2

**Project:** PSK–TMD ML PhD Project  
**Status:** Accepted working specification for the Corpus Pipeline pilot; v0.2 adds symmetric treatment of PSK and TMD site doping  
**Primary purpose:** Produce experimentally grounded charge-transfer labels for PSK–TMD photocatalytic heterostructures.  
**Primary broad label:** `mediated_recombination` vs `non_mediated_recombination` (with `unknown` retained where necessary).  

## 1. Scope and design principles

### 1.1 Corpus scope
Include publications in which a PSK–TMD heterostructure is used as a photocatalyst or in a photo-assisted catalytic process and the charge-transfer mechanism can be reported, inferred, or assessed from the paper.

Eligible applications are not restricted to photocatalytic water splitting and may include, for example:
- water splitting / H2 evolution / HER-related photocatalysis
- pollutant degradation
- dye degradation
- antibiotic or pharmaceutical degradation
- CO2 photoreduction
- nitrogen fixation
- photoelectrocatalysis
- photo-Fenton or related photo-assisted catalysis
- other photocatalytic or photo-assisted reactions

Application type is contextual metadata, not the primary labeling target.

### 1.2 Core scientific principles
1. The central label unit is the **experimental sample/sample condition**, not merely a paper or nominal formula pair.
2. Preserve the authors' reported values separately from normalized or curated values.
3. Do not discard contradictory mechanism reports for the same nominal PSK–TMD pair.
4. Preserve provenance and uncertainty for extracted and curated information.
5. Use linked tables rather than one oversized flat table.
6. Keep optional fields nullable during the pilot; tighten requirements only after empirical missingness is known.
7. Do not mix later MP/CMR computational features into the Label Dataset.
8. Treat doped/substituted TMDs as first-class TMD compositions, just as doped/substituted PSKs are treated as first-class PSK compositions. For an MX2 TMD, one or more species may occupy the M site and one or more species may occupy the X site. Do not collapse a doped TMD to its undoped parent formula. Preserve the parent formula separately when useful.

## 2. Data-role vocabulary

Each field should conceptually belong to one of the following roles:

- **reported** — directly reported by the publication.
- **normalized** — standardized representation derived from a reported value.
- **curated** — expert interpretation or manual classification.
- **derived** — deterministically calculated from other fields.
- **administrative** — identifiers, timestamps, review state, etc.

## 3. Missingness policy

Use `None`/null for missing values. When scientifically important, preserve a separate missingness reason using controlled values such as:

- `not_reported`
- `not_available`
- `not_applicable`
- `extraction_failed`
- `ambiguous`

Do not use arbitrary strings such as `N/A`, `-`, `unknown?`, or blank strings as data values.

---

# 4. Table: `papers`

One record per publication.

| Field | Type | Required | Role | Unit / Allowed values | Definition / provenance rule |
|---|---|---:|---|---|---|
| `paper_id` | str | yes | administrative | `PPR-######` | Stable internal paper identifier. |
| `doi` | str \| None | no | reported | DOI | DOI exactly as identified; normalize casing/URL prefix separately if needed. |
| `title` | str | yes | reported | — | Publication title. |
| `authors` | list[str] \| None | no | reported | — | Author list in publication order when available. |
| `year` | int | yes | reported | four-digit year | Publication year. |
| `journal` | str \| None | no | reported | — | Journal or venue. |
| `publisher` | str \| None | no | reported | — | Publisher when useful for access/provenance. |
| `document_type` | str \| None | no | normalized | article/review/etc. | Publication type. Reviews are useful for discovery but should not automatically provide experimental sample labels. |
| `access_type` | enum | yes | curated | see below | Lawful access route used for processing. |
| `full_text_available` | bool | yes | administrative | true/false | Whether lawful full text was available to the Corpus Pipeline. |
| `source_url` | str \| None | no | administrative | URL | Retrieval or landing-page location where appropriate. |
| `retrieval_date` | date | yes | administrative | ISO date | Date the source was retrieved/processed. |
| `notes` | str \| None | no | curated | — | Paper-level curation notes. |

### `access_type` initial controlled values
- `open_access`
- `institutional_access`
- `repository`
- `author_manuscript`
- `metadata_only`
- `other`

---

# 5. Table: `samples`

One record per experimentally distinguishable PSK–TMD sample or sample condition that is relevant to labeling.

| Field | Type | Required | Role | Unit / Allowed values | Definition / provenance rule |
|---|---|---:|---|---|---|
| `sample_id` | str | yes | administrative | `SMP-######` | Stable internal sample identifier. |
| `paper_id` | str | yes | administrative | FK → `papers.paper_id` | Parent publication. |
| `sample_name_reported` | str \| None | no | reported | — | Sample designation used by the authors. |
| `psk_formula_reported` | str | yes | reported | — | PSK composition exactly as reported. |
| `tmd_formula_reported` | str | yes | reported | — | TMD composition exactly as reported. |
| `psk_formula_normalized` | str \| None | no | normalized | — | Standardized PSK composition; parser rules postponed. |
| `tmd_formula_normalized` | str \| None | no | normalized | — | Standardized TMD composition; parser rules postponed. |
| `pair_id` | str \| None | no | derived/administrative | `PAIR-######` | Groups samples by nominal normalized PSK–TMD pair; not a unique material identity. |
| `psk_fraction` | float \| None | no | normalized | depends on `fraction_basis` | PSK fraction when quantitatively recoverable. |
| `tmd_fraction` | float \| None | no | normalized | depends on `fraction_basis` | TMD fraction when quantitatively recoverable. |
| `fraction_basis` | enum \| None | no | normalized | wt_fraction/mol_fraction/etc. | Basis used for component fraction. |
| `component_ratio_reported` | str \| None | no | reported | — | Original author notation for component ratio/loading. |
| `is_reference_sample` | bool | yes | curated | true/false | Marks pure components or reference/control samples. Primary heterostructure label rows will normally be false. |
| `sample_notes` | str \| None | no | curated | — | Sample-level notes and unresolved details. |

### Initial `fraction_basis` values
- `weight_fraction`
- `mole_fraction`
- `mass_ratio`
- `molar_ratio`
- `loading_percent`
- `other`
- `unknown`

## 5.1 PSK experimental description fields embedded in `samples`

| Field | Type | Required | Role | Definition |
|---|---|---:|---|---|
| `psk_parent_formula` | str \| None | no | curated | Parent perovskite composition when scientifically meaningful. |
| `psk_a_site_elements` | list[str] \| None | no | normalized/curated | A-site elements; automated assignment postponed. |
| `psk_b_site_elements` | list[str] \| None | no | normalized/curated | B-site elements; automated assignment postponed. |
| `psk_anion_elements` | list[str] \| None | no | normalized/curated | Anion-site elements, with O expected as main anion for project scope. |
| `psk_phase_reported` | str \| None | no | reported | Phase/crystal-system description stated by authors. |
| `psk_space_group_reported` | str \| None | no | reported | Space group if reported. |
| `psk_morphology` | str \| None | no | reported/normalized | Morphology description. |
| `psk_particle_size_nm` | float \| None | no | normalized | Characteristic size only when a meaningful scalar can be extracted. |
| `psk_defects_reported` | list[str] \| None | no | reported/normalized | Reported vacancies/defects. |
| `psk_doping_description` | str \| None | no | reported | Doping/substitution description. |
| `psk_commercial` | bool \| None | no | reported/curated | Whether PSK was commercially sourced. |

## 5.2 TMD experimental description fields embedded in `samples`

TMDs are treated symmetrically with PSKs with respect to substitution/doping. A TMD is represented conceptually as an `MX2`-type composition, where the M site may contain one or multiple transition-metal species and the X site may contain one or multiple chalcogen species. Doped/substituted TMDs remain distinct compositions and must not be collapsed to an undoped parent.

| Field | Type | Required | Role | Definition |
|---|---|---:|---|---|
| `tmd_parent_formula` | str \| None | no | curated | Undoped or conceptual parent TMD composition when scientifically meaningful; never used to replace the actual reported/normalized doped composition. |
| `tmd_m_site_elements` | list[str] \| None | no | normalized/curated | All elements assigned to the transition-metal M site, including host element(s) and one or more M-site dopants/substituents. Automated assignment postponed. |
| `tmd_x_site_elements` | list[str] \| None | no | normalized/curated | All elements assigned to the chalcogen X site, including host chalcogen(s) and one or more X-site dopants/substituents. Automated assignment postponed. |
| `tmd_m_site_dopants` | list[str] \| None | no | curated | M-site elements identified as dopants/substituents relative to a stated or curated parent composition. |
| `tmd_x_site_dopants` | list[str] \| None | no | curated | X-site elements identified as dopants/substituents relative to a stated or curated parent composition. |
| `tmd_phase_reported` | str \| None | no | reported | 2H/1T/1T′/mixed/etc. when reported. |
| `tmd_layer_description` | str \| None | no | reported/normalized | Monolayer/few-layer/bulk/etc. |
| `tmd_morphology` | str \| None | no | reported/normalized | Morphology description. |
| `tmd_particle_size_nm` | float \| None | no | normalized | Characteristic size if meaningful. |
| `tmd_defects_reported` | list[str] \| None | no | reported/normalized | Reported defects/vacancies, including metal- or chalcogen-site vacancies where relevant. |
| `tmd_doping_description` | str \| None | no | reported | Original author-reported doping/substitution description, preserved even when site-specific normalized fields are populated. |
| `tmd_commercial` | bool \| None | no | reported/curated | Whether TMD was commercially sourced. |

## 5.3 Heterostructure/interface description fields embedded in `samples`

| Field | Type | Required | Role | Definition |
|---|---|---:|---|---|
| `heterostructure_type_reported` | str \| None | no | reported | Authors' description of heterostructure type/architecture. Do not use as the normalized mechanism label automatically. |
| `interface_description` | str \| None | no | reported/curated | Interface/contact description. |
| `contact_type` | str \| None | no | normalized | Direct contact/deposited/coated/etc.; controlled enum postponed. |
| `preferred_facet_reported` | str \| None | no | reported | Facet/interface orientation where stated. |
| `heterostructure_morphology` | str \| None | no | reported/normalized | 0D/2D, 2D/2D, nanoparticles-on-sheets, etc. |
| `cocatalyst_present` | bool \| None | no | reported | Whether an additional cocatalyst is present. |
| `cocatalyst` | list[str] \| None | no | reported/normalized | Cocatalyst identity, e.g. Pt. |
| `mediator_present` | bool \| None | no | reported | Whether an explicit redox/solid mediator is present. |
| `mediator` | list[str] \| None | no | reported/normalized | Mediator identity. |
| `interface_notes` | str \| None | no | curated | Interface-related curation notes. |

---

# 6. Table: `synthesis_steps`

One sample may have zero, one, or many synthesis/integration records. This table preserves process order and allows one-pot, two-stage, three-stage, and commercial-component routes without forcing them into fixed columns.

| Field | Type | Required | Role | Unit / Allowed values | Definition |
|---|---|---:|---|---|---|
| `synthesis_step_id` | str | yes | administrative | internal ID | Unique synthesis-step record. |
| `sample_id` | str | yes | administrative | FK → `samples.sample_id` | Parent sample. |
| `step_order` | int | yes | curated | positive integer | Chronological/logical order within preparation route. |
| `step_role` | enum | yes | curated | see below | Role of the step in producing PSK/TMD/heterostructure. |
| `method_reported` | str \| None | no | reported | — | Author-reported method name. |
| `method_normalized` | str \| None | no | normalized | Standardized method category; taxonomy postponed. |
| `precursors` | list[str] \| None | no | reported | — | Precursors/reagents when useful. Structured chemistry parsing postponed. |
| `temperature_c` | float \| None | no | normalized | °C | Main processing temperature when meaningful. |
| `time_h` | float \| None | no | normalized | h | Main processing duration. |
| `pressure` | float \| None | no | normalized | unit must be stored explicitly if used | Pressure if reported. Final representation postponed. |
| `atmosphere` | str \| None | no | reported/normalized | — | Air/Ar/N2/vacuum/etc. |
| `solvent` | list[str] \| None | no | reported | — | Solvent(s) where relevant. |
| `ph` | float \| None | no | normalized | — | pH when reported. |
| `calcination_temperature_c` | float \| None | no | normalized | °C | Post-synthesis calcination temperature. |
| `calcination_time_h` | float \| None | no | normalized | h | Post-synthesis calcination time. |
| `raw_description` | str \| None | no | reported | — | Short source-derived process description, subject to copyright-safe storage rules. |
| `source_location` | str \| None | no | administrative | page/section/table | Location of source evidence. |
| `notes` | str \| None | no | curated | — | Curator notes. |

### `step_role` initial values
- `psk_synthesis`
- `tmd_synthesis`
- `integration`
- `simultaneous_psk_formation_integration`
- `simultaneous_tmd_formation_integration`
- `one_pot`
- `post_treatment`
- `other`

### Sample-level synthesis topology
A derived/curated topology field may later be added to `samples` or a
dedicated preparation summary table. Planned values include:
- `three_stage`
- `psk_first_two_stage`
- `tmd_first_two_stage`
- `one_pot`
- `commercial_component_variant`
- `other`
- `unknown`

Implementation of topology-classification logic is postponed until pilot routes are observed.

---

# 7. Table: `mechanism_assessments`

This table separates what authors claim from the normalized mechanism and from the broad ML target.

| Field | Type | Required | Role | Unit / Allowed values | Definition |
|---|---|---:|---|---|---|
| `mechanism_assessment_id` | str | yes | administrative | internal ID | Unique mechanism assessment. |
| `sample_id` | str | yes | administrative | FK → `samples.sample_id` | Parent sample. |
| `mechanism_reported` | str \| None | no | reported | — | Mechanism wording used by authors. |
| `mechanism_normalized` | enum | yes | normalized/curated | `MechanismLabel` | Controlled detailed mechanism label. |
| `charge_transfer_class` | enum | yes | curated/derived | `ChargeTransferClass` | Broad ML target. |
| `claim_explicit` | bool | yes | curated | true/false | Whether the paper explicitly states the mechanism rather than requiring inference. |
| `assessment_confidence` | float \| None | no | curated | 0–1 | Confidence in our normalized assessment. |
| `label_status` | enum | yes | curated | see below | Whether the record is currently eligible as a training label. |
| `manual_review_status` | enum | yes | administrative | see below | Review state. |
| `reviewer_notes` | str \| None | no | curated | — | Concise scientific reasoning or unresolved issues. |

### Existing `MechanismLabel` values
- `z_scheme`
- `s_scheme`
- `type_ii`
- `other`
- `unknown`

The detailed enum will be expanded only when pilot evidence justifies additional recurring mechanisms
(e.g. Schottky, p–n, conventional Type-I, etc.).

### Existing `ChargeTransferClass` values
- `mediated_recombination`
- `non_mediated_recombination`
- `unknown`

### Initial `label_status` values
- `accepted`
- `uncertain`
- `excluded`
- `pending_review`

### Initial `manual_review_status` values
- `not_reviewed`
- `reviewed`
- `needs_second_review`

**Important:** the exact rule mapping detailed mechanisms to the broad binary target is a
postponed scientific decision and must be documented before ML training. It must not be
silently encoded from names alone.

---

# 8. Table: `mechanism_evidence`

One mechanism assessment may have zero or many evidence records.

| Field | Type | Required | Role | Unit / Allowed values | Definition |
|---|---|---:|---|---|---|
| `evidence_id` | str | yes | administrative | internal ID | Unique evidence record. |
| `mechanism_assessment_id` | str | yes | administrative | FK → assessment | Parent mechanism assessment. |
| `evidence_type` | str | yes | normalized | provisional taxonomy | Measurement/calculation class supporting mechanism assessment. |
| `evidence_subtype` | str \| None | no | normalized | — | More specific subtype if useful. |
| `supports_mechanism` | enum | yes | curated | `supports`/`contradicts`/`ambiguous`/`context_only` | Relationship of evidence to claimed mechanism. |
| `evidence_strength` | enum \| None | no | curated | strong/moderate/weak/unknown | Curated evidential strength; rubric postponed. |
| `reported_result` | str \| None | no | reported/normalized | — | Concise copyright-safe summary of relevant result. |
| `source_location` | str \| None | no | administrative | page/figure/table/section | Where evidence occurs. |
| `notes` | str \| None | no | curated | — | Curator interpretation. |

### Provisional evidence types
- `xps`
- `ups`
- `pl`
- `time_resolved_pl`
- `esr_epr`
- `radical_trapping`
- `mott_schottky`
- `photocurrent`
- `eis`
- `cv`
- `work_function`
- `kelvin_probe`
- `photodeposition`
- `band_alignment`
- `dft`
- `optical_absorption`
- `other`

Do not freeze this taxonomy before the pilot.

---

# 9. Table: `photocatalytic_tests`

Generalized reaction/test table. Water-splitting/H2 fields are optional specializations, not corpus inclusion criteria.

| Field | Type | Required | Role | Unit / Allowed values | Definition |
|---|---|---:|---|---|---|
| `test_id` | str | yes | administrative | internal ID | Unique test/condition record. |
| `sample_id` | str | yes | administrative | FK → `samples.sample_id` | Tested sample. |
| `application_type` | str | yes | normalized | taxonomy postponed | Broad application category. |
| `reaction_type_reported` | str \| None | no | reported | — | Author wording for reaction/process. |
| `target_species` | list[str] \| None | no | reported/normalized | — | Reactant/pollutant/product of interest. |
| `light_source` | str \| None | no | reported | — | Lamp/LED/solar simulator/etc. |
| `wavelength_nm` | float \| None | no | normalized | nm | Single characteristic wavelength when appropriate. |
| `wavelength_range_nm` | str \| None | no | normalized | nm | Preserve ranges/cutoffs not reducible to one value. |
| `light_intensity` | float \| None | no | normalized | unit required | Intensity where reported. Final unit representation postponed. |
| `visible_light_only` | bool \| None | no | curated | true/false | Whether authors' setup is explicitly visible-light constrained. |
| `catalyst_mass_mg` | float \| None | no | normalized | mg | Catalyst amount. |
| `solution_volume_ml` | float \| None | no | normalized | mL | Reaction volume. |
| `reaction_medium` | str \| None | no | reported/normalized | — | Solvent/electrolyte/solution description. |
| `ph` | float \| None | no | normalized | — | Reaction pH. |
| `sacrificial_agent` | list[str] \| None | no | reported/normalized | — | Sacrificial donor/acceptor if used. |
| `cocatalyst` | list[str] \| None | no | reported/normalized | — | Cocatalyst used specifically in the catalytic test. |
| `test_duration_h` | float \| None | no | normalized | h | Test duration. |
| `performance_metric_name` | str \| None | no | reported/normalized | — | General metric, e.g. degradation efficiency, rate constant, H2 evolution rate. |
| `performance_metric_value` | float \| None | no | normalized | see unit | Numerical value. |
| `performance_metric_unit` | str \| None | no | reported/normalized | — | Explicit unit. |
| `performance_value_reported` | str \| None | no | reported | — | Original value/unit expression when useful for audit. |
| `cycles` | int \| None | no | normalized | count | Stability/recycling cycles. |
| `performance_notes` | str \| None | no | curated | — | Contextual notes. |
| `source_location` | str \| None | no | administrative | page/figure/table | Provenance location. |

## 9.1 Optional water-splitting / H2-specific fields

| Field | Type | Unit | Role |
|---|---|---|---|
| `hydrogen_amount_umol` | float \| None | µmol | normalized |
| `hydrogen_rate_reported_value` | float \| None | reported unit | reported |
| `hydrogen_rate_reported_unit` | str \| None | — | reported |
| `hydrogen_rate_umol_g_h` | float \| None | µmol g⁻¹ h⁻¹ | derived/normalized |
| `oxygen_amount_umol` | float \| None | µmol | normalized |
| `sth_percent` | float \| None | % | reported/normalized |
| `apparent_quantum_yield_percent` | float \| None | % | reported/normalized |

Do not require or search exclusively for these fields during corpus discovery.

---

# 10. Table: `extraction_records`

Audit/provenance table for machine- and manually extracted values. Exact granularity will be tested in the pilot.

| Field | Type | Required | Role | Definition |
|---|---|---:|---|---|
| `extraction_id` | str | yes | administrative | Unique extraction record. |
| `paper_id` | str | yes | administrative | Source paper. |
| `sample_id` | str \| None | no | administrative | Associated sample if resolved. |
| `target_table` | str | yes | administrative | Table/entity being populated. |
| `target_field` | str | yes | administrative | Field being populated. |
| `extractor_type` | enum | yes | administrative | manual/regex/nlp/llm/derived. |
| `extractor_name` | str \| None | no | administrative | Tool/model/method name. |
| `extractor_version` | str \| None | no | administrative | Version when relevant. |
| `extraction_date` | date | yes | administrative | Extraction date. |
| `source_location` | str \| None | no | administrative | Page/section/table/figure. |
| `raw_value` | str \| None | no | reported | Candidate/source-derived value, stored copyright-safely. |
| `normalized_value` | str \| None | no | normalized | Standardized value when serialized. |
| `confidence` | float \| None | no | curated/model | 0–1 extraction confidence. |
| `manual_verified` | bool | yes | administrative | Whether a human checked it. |
| `reviewer` | str \| None | no | administrative | Reviewer identifier/name if needed. |
| `notes` | str \| None | no | curated | Audit notes. |

### `extractor_type`
- `manual`
- `regex`
- `nlp`
- `llm`
- `derived`
- `other`

---

# 11. Planned table: `disagreement_records`

**Status: postponed; do not implement in the first core models.**

Purpose: preserve and classify contradictory mechanism assignments across samples/publications sharing the same nominal PSK–TMD pair or sufficiently comparable material context.

Candidate fields:
- `disagreement_id`
- `pair_id`
- linked `sample_id` / `mechanism_assessment_id` values
- `disagreement_class`
- `comparison_basis`
- `confidence`
- `reviewer_notes`

Provisional disagreement classes:
- `context_dependent`
- `structural_state_difference`
- `synthesis_state_difference`
- `experimental_condition_difference`
- `evidence_interpretation_difference`
- `insufficient_evidence`
- `probable_reporting_inconsistency`
- `unresolved`

The first priorities are genuine context-dependent differences and structural/synthesis-state differences.

---

# 12. Minimum viable records for pilot

## 12.1 Minimum paper record
Required:
- `paper_id`
- `title`
- `year`
- `access_type`
- `full_text_available`
- `retrieval_date`

## 12.2 Minimum sample record
Required:
- `sample_id`
- `paper_id`
- `psk_formula_reported`
- `tmd_formula_reported`
- `is_reference_sample`

## 12.3 Minimum mechanism assessment
Required:
- `mechanism_assessment_id`
- `sample_id`
- `mechanism_normalized`
- `charge_transfer_class`
- `claim_explicit`
- `label_status`
- `manual_review_status`

This permits `unknown` mechanism/charge-transfer values without inventing information.

---

# 13. Relationship summary

```text
papers (1)
  |
  +----< samples (many)
          |
          +----< synthesis_steps (many)
          |
          +----< mechanism_assessments (many)
          |        |
          |        +----< mechanism_evidence (many)
          |
          +----< photocatalytic_tests (many)

extraction_records -> can point to paper/sample/table/field provenance

pair_id -> later enables cross-paper disagreement analysis
```

---

# 14. Explicitly postponed decisions / backlog

These items are intentionally deferred, not forgotten. Each must be revisited at the appropriate phase.

## Corpus / Label Dataset
1. Exact PSK composition parser and A/B/O-site assignment rules, including multi-site doping and O-site substitution/nonstoichiometry.
2. Exact TMD composition parser and M/X-site assignment rules, including one or multiple M-site dopants/substituents, one or multiple X-site dopants/substituents, mixed-site compositions, plus phase/layer parsing. Doped TMDs must remain distinct from their parent compositions throughout Corpus, Materials, Mapping, Integrated Dataset, Feature Engineering, and ML.
3. Controlled vocabulary for morphology and interface/contact types.
4. Controlled vocabulary for synthesis methods and automatic synthesis-topology classification.
5. Evidence-strength scoring rubric.
6. Final evidence-type taxonomy.
7. Exact mapping rule from detailed mechanism labels to broad `mediated_recombination` / `non_mediated_recombination` classes.
8. Treatment of Schottky, p–n, Type-I, hybrid/mixed, ambiguous, and author-specific mechanism terminology.
9. Weak/silver labels: keep separate; use only later if needed; experimentally supported labels remain the primary evaluation set.
10. `DisagreementRecord` implementation and disagreement-classification logic.
11. Quantitative missingness analysis after the 20–30 paper pilot and consequent required/optional-field revision.
12. Copyright/TDM-safe limits for storing source-derived snippets in `raw_description`, `reported_result`, and extraction provenance.
13. Corpus discovery/search taxonomy covering all PSK–TMD photocatalytic/photo-assisted applications, not only H2/HER/water splitting.

## Materials / Mapping
14. Verified exact MP/CMR feature inventory, API field names, units, provenance, and missingness.
15. Cross-database MP↔CMR structural matching strategy and confidence/evidence fields.
16. Label sample → MP/CMR candidate mapping implementation and mapping-confidence rubric.
17. Policy when one experimental sample maps to multiple plausible computational records: preserve all, representative selection, prediction aggregation, or explicit uncertainty modeling.
18. Structure-family identity logic; formula must never be treated as unique material identity.

## ML
19. Final Modeling Dataset construction rules.
20. Leakage-safe grouping strategy for repeated nominal pairs/related variants.
21. Nested/grouped validation strategy appropriate to dataset size.
22. Feature selection/engineering after verified MP/CMR availability.
23. Small-data contingencies: binary target, interpretable/Bayesian/physics-informed models, weak-label calibration, or ranking if sample count is insufficient.

---

# 15. Versioning rule

This document is **Schema v0.2**. During the pilot, schema changes should be explicit and documented. Do not silently repurpose existing field meanings. Material changes should produce v0.3 or later and include a short changelog.

## Changelog — v0.2
- Added project-wide symmetric treatment of doped/substituted TMDs and doped/substituted PSKs.
- Replaced singular TMD composition concepts (`tmd_metal`, `tmd_chalcogen`) with site-aware lists (`tmd_m_site_elements`, `tmd_x_site_elements`).
- Added `tmd_parent_formula`, `tmd_m_site_dopants`, and `tmd_x_site_dopants`.
- Explicitly prohibited collapsing doped TMDs to undoped parent compositions in Corpus, Materials, Mapping, Integrated Dataset, Feature Engineering, or ML stages.
- Expanded the postponed TMD parser requirement to include multi-dopant M-site and X-site assignment.



