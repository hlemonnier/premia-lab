# Source register and current evidence

Date: 26 October 2026. User-facing times use Europe/Paris.

## Authoritative task sources

| Source | Observed evidence | Use and limit |
|---|---|---|
| [Shared assignment folder](https://drive.google.com/drive/folders/1S2hAfhRHxvkUA7CPyq3IAozF787yu67c) | Shared by Arseniy Banayev, Continual Research; notification 26 Oct 2026 at 14:12 Paris | Confirms assignment provenance and file inventory |
| [Assignment README](https://drive.google.com/file/d/1AsSkH5mIiO4nB0paZ9vZscKZfp1nhHdV/view?usp=drivesdk) | Full text fetched and read; matches attachment text after removing trailing newlines | Objective, timing, constraints, dependencies, submission and assessment criteria |
| [Scorer](https://drive.google.com/file/d/174Nk_W_yZ8pyWHG6onTrf-lLfShABN6p/view?usp=drivesdk) | The attached score.py was read in full; Drive metadata name and byte size agree | Exact local scoring semantics. Remote script bytes were not independently compared |
| [Latest relevant email](https://mail.google.com/mail/u/?authuser=hugo.lemonnier01%40gmail.com#all/1a17856778a5c809) | Arseniy confirmed sending the assessment via Google on 26 Oct at 14:11 Paris | Confirms progression to the assessment; does not add technical requirements |
| [Earlier scheduling exchange](https://mail.google.com/mail/u/?authuser=hugo.lemonnier01%40gmail.com#all/1a15f2bc67e8d54e) | 21 Oct exchange: proposed Monday start to finish Wednesday; reply agreed to send Monday at 18:00 Paris | Operational target Wednesday 28 October; exact final deadline/hour not explicitly confirmed |
| Uploaded ZIP | 136,015,226 bytes; SHA-256 ba49564fb0d8888124fdc0b680f88c843c17359a089129f1fe28e0b94e003dd6 | Frozen data/code inputs; all 12 original members were independently SHA-256 compared with extracted files |

All eight root file names and byte sizes agree between the Drive folder and the uploaded archive. The metadata response did not expose remote checksums. No claim is made that the CSVs were byte-compared with Drive. The local extracted originals were compared with the decompressed ZIP members and remain unchanged.

## Executed preflight evidence

- `evidence/preflight_001/`: failed inventory check before any data analysis. The harness counted incidental working-directory artifacts rather than original ZIP membership. Historical evidence was kept; the correction and a not-yet-executed deterministic reproduction procedure are documented.
- `evidence/preflight_002/`: corrected archive-scoped inventory, full structural census, and original equal-weight CSV/load/replay/report workflow on rows 0:504. Exit 0, 24 checks passed within the stated scope.
- `reviews/preflight_review.md`: independent review of source identity, artifact hashes, data-access scope, ordered alignment and saved replay results.

Verified structure: 3,780 return days × 1,000 stocks; 3,780,000 characteristic rows × 13 features; 1,000 stock costs. Ordered keys agree exactly. All supplied numeric values are finite and all costs are nonnegative. Full-file inspection was limited to input hygiene; outcome metrics were calculated only on the first 504 rows.

The smoke workflow returned 250 scored rows, Python indices253..502 / CSV days254..503. Repeated economic outputs were identical; timing differed as expected. Equal-weight net beta was 0.9999892124, so the example intentionally fails the assignment's beta condition. These results establish only source/input and basic execution readiness.

No candidate has been implemented, trained, or evaluated. No model selection or protected-period outcome analysis has occurred. Full-sample supplied figures have not been opened.

## Environment observed

Python 3.12.14; NumPy 2.3.5; pandas 2.2.3; SciPy 1.17.0; scikit-learn 1.8.0. CVXPY and LightGBM are not installed locally at this phase; both are promised in the evaluator by the brief. The smoke process was pinned to one CPU with numerical-library thread limits set to one. This is not a benchmark of a final candidate or proof of its long-horizon runtime.

## Claim status vocabulary

`source-reviewed` means established by reading source, not an executed test. `executed/pass` and `executed/fail` refer to saved evidence. `planned`, `not run`, and `blocked` never mean passed. Scientific hypotheses remain hypotheses until tested under the frozen protocol.
