# Canonical-layout fixture source review before replacement workflows

27 October 2026, Europe/Paris. The independent verification agent inspected the exact diff from `02_verify_causality_before.py` to `03_verify_causality_after.py` under the root's prospective `INPUT_LAYOUT_CORRECTION_PLAN.md`.

Reviewed corrected worker SHA256: `b46df7ed7e3dec9677a7d855ca6b082c872a7c15ce645eaf15f5246f475cdc83`.

Finding: initial and prefix `order="K"` copies preserve the canonical source element-order layout. Synthetic append explicitly allocates F order for an F-only source and C order otherwise, then assigns the same prescribed values. Metadata additions record shape, strides, dtype and contiguity without entering candidate decisions. No candidate, scorer, perturbation values, scenario, protected mask, tolerance or accounting change was found.

The reviewer approved execution of the same39 C06 scenarios in replacement directories and use of the frozen corrected worker for the still-unexecuted C09 profile. Root had already authorized those executions after independent review. Original packets and failures remain unchanged. Source review is not an executed numerical pass; exact historical reproduction and protected-output equality remain required.
