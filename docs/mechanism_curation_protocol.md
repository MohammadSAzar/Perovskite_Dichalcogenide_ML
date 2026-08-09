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

## Explicit versus inferred labels

The distinction between an author-explicit mechanism and a curator-inferred mechanism must be preserved.

### Author-explicit

Use when the paper directly identifies the mechanism, for example:

- Z-scheme
- S-scheme
- Type-II
- Schottky
- p-n heterojunction

In these cases:

```text
claim_explicit = true


