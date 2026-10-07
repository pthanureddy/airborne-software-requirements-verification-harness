# DO-178C Learning Notes and Evidence Boundary

This project studies selected airborne-software assurance concepts. It is not a
DO-178C-compliant development, certification package, safety assessment, qualified
tool, or aircraft implementation.

## Software levels

An aircraft/system safety process assigns software levels based on the potential
effect of anomalous software behavior. The commonly used progression is Level A
for catastrophic effects, Level B for hazardous or severe-major effects, Level C
for major effects, Level D for minor effects, and Level E for no safety effect.
The level determines the applicable lifecycle objectives and the independence and
verification rigor needed to satisfy them. This repository labels its exercise as
Level C only to make the configuration explicit; no system safety assessment was
performed, so the label has no certification meaning.

## Concepts exercised

- high- and low-level requirement identifiers with parent relationships;
- requirements-based deterministic normal, robustness, and boundary tests;
- bidirectional requirement-to-test visibility in a generated CSV matrix;
- source/configuration/test baselines identified with SHA-256 hashes;
- repeatable CI checks for formatting, static typing, tests, branch coverage, build,
  and evidence generation;
- explicit reporting of failures and evidence limitations.

Branch coverage is used only as a repository development metric. The project does
not claim DO-178C structural coverage, MC/DC, object-code coverage, verification
independence, target-hardware execution, tool qualification, or certification credit.

## Public reference

FAA Advisory Circular 20-115D recognizes DO-178C as an acceptable means of
compliance and describes lifecycle planning, development, verification,
configuration management, quality assurance, certification liaison, and evidence
objectives: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-115D.pdf

