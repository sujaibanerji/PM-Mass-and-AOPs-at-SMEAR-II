# Scientific figure audit

The original 18 October scan covered 6,210 source candidates. The 19 October author-requested revision adds the exact manuscript flowchart and explicitly excludes backscattering content, including mixed figures. There are 130 retained scientific figures and 281 assets: 17 current figures and 113 historical figures with 151 companion exports.

`scope_revision.json` identifies all 62 removed figures and 115 removed assets, the reviewed evidence, manuscript image identity and revised archive hashes. `selection_decisions.json` records explicit `out_of_scope` decisions, so removed scientific content is not mislabelled as a duplicate or non-scientific artifact. `../figure_exclusions.csv` lists these decisions. PDF page mappings retain excluded IDs separately for provenance, with only retained IDs active.

The fixed-artwork change is recorded in `renderer_artwork.diff`. Figure 1 is copied exactly from the supplied manuscript ZIP. Numerical calculations and numerical data/reference tables are unchanged. The registered code archive contains no backscattering-specific Python or Julia routines. Historical script paths in provenance are references, not shipped code or validated regeneration registrations.

Retained historical images preserve their original bytes and scientific conventions, including sphere-surface versus projected-area distinctions and mass-selection cohorts. They remain labelled archived images. Older audit and acceptance records describe their explicitly versioned earlier deliveries.
