# Label Dataset Schema v0.2

## 1. Purpose

The Label Dataset stores experimentally grounded information extracted from the
literature for PSK-TMD heterostructures.

Its primary purpose is to provide reliable charge-transfer mechanism labels and
the minimum experimental context required for:

1. mechanism-label curation;
2. mapping experimental materials to computational records from MP and CMR;
3. downstream machine-learning dataset construction;
4. provenance and quality control.

The Label Dataset is not intended to reproduce every experimental detail in a
paper or to function as a complete photocatalysis database.

Extraction should therefore prioritize information that improves:

- mechanism-label reliability;
- material identity and composition;
- MP/CMR mapping;
- ML usefulness;
- provenance;
- dataset quality control.

Detailed information that does not materially serve these purposes should not
be systematically extracted.


## 2. Scope

The literature corpus includes PSK-TMD heterostructures used in photocatalytic,
photo-assisted, photoelectrocatalytic, or electrophotocatalytic systems when a
charge-transfer mechanism can be identified.

Applications may include, but are not limited to:

- photocatalytic hydrogen evolution;
- overall or partial water splitting;
- pollutant degradation;
- dye degradation;
- antibiotic degradation;
- CO2 conversion;
- N2-related photocatalysis;
- photoelectrocatalysis;
- other photo-assisted catalytic applications.

Application type is metadata and is not the primary inclusion criterion.

Non-photocatalytic systems that do not serve the charge-transfer-labeling goal
should normally be excluded during literature search and screening rather than
represented through additional catalyst-mode fields.


## 3. Core Entity Structure

Schema v0.2 uses nine persisted JSON tables:

1. `papers.json`
2. `sample_series.json`
3. `samples.json`
4. `synthesis_records.json`
5. `mechanism_assessments.json`
6. `mechanism_evidence.json`
7. `photocatalytic_tests.json`
8. `extraction_records.json`
9. `disagreement_records.json`

The main relationships are:

```text
PaperRecord
    |
    +---- SampleSeries
    |         |
    |         +---- ExperimentalSample
    |                    |
    |                    +---- SynthesisRecord
    |                    |
    |                    +---- PhotocatalyticTest
    |                    |
    |                    +---- MechanismAssessment
    |                              |
    |                              +---- MechanismEvidence
    |
    +---- ExtractionRecord
    |
    +---- DisagreementRecord

