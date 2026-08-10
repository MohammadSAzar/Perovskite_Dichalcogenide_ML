# Mechanism Curation Protocol

## Purpose

This document defines how charge-transfer mechanisms are assigned in the PSK-TMD Label Dataset.

The mechanism label must be based on the scientific evidence presented in the paper, not only on keyword occurrence.

A mechanism may be explicitly named by the authors or inferred from figures, band diagrams, carrier-transfer arrows,
and supporting experimental evidence.

## Mechanism-reading hierarchy

Mechanism assessment should follow this order:

1. Explicit mechanism statement in the main text
2. Explicit mechanism label in a figure, scheme, or caption
3. Mechanism inferred from carrier-transfer arrows in a figure or scheme
4. Mechanism inferred from band alignment together with charge-transfer direction
5. Mechanism inferred from experimental evidence supporting a particular transfer pathway
6. Unresolved if the available evidence is insufficient


## Conventional band-alignment mechanisms

Band alignment and carrier-transfer mechanism must not be inferred from
terminology alone. Figures, band diagrams, arrows, captions, and supporting
text must be inspected.

### Type-I heterojunction

Type-I corresponds to a straddling-gap alignment.

Both the conduction-band minimum and valence-band maximum of one component
lie within the band gap of the other component. Under the conventional
Type-I carrier-transfer picture, photogenerated electrons and holes tend to
accumulate in the same component.

Typical clues include:

- straddling band alignment;
- both electron and hole transfer toward the same component;
- a figure showing both retained carrier populations in one semiconductor.

### Type-II heterojunction

Type-II corresponds to a staggered-gap alignment.

Under the conventional Type-II carrier-transfer picture, photogenerated
electrons preferentially accumulate in the component with the lower
conduction-band edge, while holes accumulate in the component with the
higher valence-band edge.

Typical clues include:

- staggered band alignment;
- electrons and holes spatially separated into different components;
- carrier-transfer arrows consistent with conventional Type-II transfer.

### Type-III heterojunction

Type-III corresponds to a broken-gap alignment.

The band gap of one component does not overlap conventionally with that of
the other, producing a broken-gap configuration. Type-III assignments
should be made conservatively and require clear band-position or figure
evidence.

### Z-scheme and S-scheme mechanisms

Z-scheme and S-scheme mechanisms must remain distinct from conventional
Type-II mechanisms even when the isolated-component band positions resemble
a staggered alignment.

Their defining feature for this project is selective interfacial
recombination of the weaker redox carriers while preserving the electrons
and holes with stronger reduction and oxidation capabilities.

Therefore, band positions alone are not sufficient to distinguish
conventional Type-II from Z-/S-scheme carrier transfer.

## Explicit versus inferred labels

The distinction between an author-explicit mechanism and a curator-inferred mechanism must be preserved.

### Author-explicit

Use when the paper directly identifies the mechanism, for example:

- Z-scheme
- S-scheme
- Type-II
- Type-I
- Type-III
- Schottky
- p-n heterojunction

In these cases:

```text
claim_explicit = true

