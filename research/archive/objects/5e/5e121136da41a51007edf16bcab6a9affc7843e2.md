# Publication and evidence preservation

The policy and experiment sources are frozen. The overlay wave completed successfully; the conditionally admitted joint completed successfully. No further parameters or candidate runs are included.

## Required synthetic arrays

Include the following 14 compressed synthetic replay archives explicitly. They may be excluded by a generic ignore-based Git inventory, but they are part of the recorded output evidence. All archives passed full ZIP CRC checks; see synthetic_archive_integrity.json. They contain forecasts, actual targets, virtual targets and scorer rows for every base, altered-future, prefix and repeated-session case. Total size is 3953835 bytes.

| Repository path | Bytes | SHA256 |
|---|---:|---|
| evidence/v2_score_overlay_20261028/e2e_001/VTvar/replay_arrays.npz | 301533 | `b0f1b6b25d958b7e3ac409e7ebb44df3f2610ee6e5f01b028ef5f6de31f50fb9` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvar_future_mutated/replay_arrays.npz | 301596 | `fb77fcfb555f7df6a0f9fdd8a77f7282b9519643469809b3bcefd2cc62998b44` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvar_prefix361/replay_arrays.npz | 212399 | `44bb6927e30c8c749c77d6c9a7fbc2d789b3026e94dc4a48ed266c8e0015c5e4` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvar_repeat_after_other_histories/replay_arrays.npz | 301542 | `008e1a52a8cd1a4e135c2319f81d5db321ebd983d94fe38ff8f1e7346165eb5a` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvol/replay_arrays.npz | 301555 | `ab2d081d40bfc5a06fe76272a5609f02cc8e213fb181031e7be8ae3b2bf937ff` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvol_future_mutated/replay_arrays.npz | 301596 | `046f6c2f6dae1be23fcd1f8b6c38207e87076ffd0e8ba8367acd9ad1dc02b637` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvol_prefix361/replay_arrays.npz | 212400 | `aaf811f054a53001e638a479d635be24a7de77a610036418d79953d0ed1aaffb` |
| evidence/v2_score_overlay_20261028/e2e_001/VTvol_repeat_after_other_histories/replay_arrays.npz | 301564 | `a50c52a06732124742bd1f0b6ff9bc4385614fb0e9f12fc1f21f5061c243cc74` |
| evidence/v2_score_overlay_20261028/e2e_001/fixed_one/replay_arrays.npz | 301156 | `9e383ab8e8307f4d0e15267c4ea12d03a39d6eff6be79fb5be91231b3916f5a6` |
| evidence/v2_score_joint_20261028/e2e_001/fixed_one/replay_arrays.npz | 301204 | `02c1093bb1af0864bc64bf7dc48e52a58aa866730b610267f7e66331055d6669` |
| evidence/v2_score_joint_20261028/e2e_001/joint_F2_VTvol/replay_arrays.npz | 301586 | `5ac1f0b8dfa46f85118603865fa93af1953ea3489bcb377f85c310c80351f237` |
| evidence/v2_score_joint_20261028/e2e_001/joint_F2_VTvol_future_mutated/replay_arrays.npz | 301656 | `e596d0925cb9f1712f65fec30efb0f69cd093634eb5382dcc8b34b4f636967cb` |
| evidence/v2_score_joint_20261028/e2e_001/joint_F2_VTvol_prefix361/replay_arrays.npz | 212459 | `ad00e55a095dae990d659cecfd9f0ae71200855b6964d798474d8c588333a493` |
| evidence/v2_score_joint_20261028/e2e_001/joint_F2_VTvol_repeat_after_other_histories/replay_arrays.npz | 301589 | `1a2c23b030786c21e168f409f2d112cebb9f64e2b3f2e2e9a53f779892fc296b` |

## Other required files

Preserve both packets' PLAN, source reviews, preimplementation/red records, original pre-review files where present, exact commands, execution records, source manifests, copied source, stdout/stderr, complete daily/decision CSVs, result JSONs and array hashes. Preserve failed red logs as expected failures rather than replacing them. Outcome reports are written after execution; the original plans remain byte-for-byte frozen.

Actual baseline target arrays used by the independent stock-level accountant are owned by the forecast packet; its repaired verified F2 arrays and valid V2 reference must be preserved according to that packet's manifest. These packets retain exact full virtual/actual target hashes and scalar multiplier/gross scales, allowing the accountant to reconstruct actual targets from the matching base arrays. No post-hoc saved-array lookup enters a strategy decision.

Current prototype programs are instrumented research artifacts. They preserve the original production package and original scorer. Claude can use the parent handoff to perform later production integration; this packet does not claim a completed production or century-runtime release.
