# state/ — per-run resumable checkpoint storage

Resumable experiment runners (see `../src/run_study1_replication.py`) write
their checkpoint JSON here. Contents are gitignored except this README.

## Files

- `study1-checkpoint.json` — written by `run_study1_replication.py`.
  Records completed `(paper, model)` cells and any failures.

## Resume semantics

To resume after a quota exhaustion, a crash, or an explicit Ctrl-C, just
re-run the same command. The runner reads the checkpoint, skips any
cell already listed under `completed`, and continues from the first
unfinished cell.

To force a re-run of a specific cell, remove its entry from the
`completed` list (or delete the corresponding output file under
`../data/raw/study1-replication/` and the runner will re-write it on
the next pass — outputs are checked by file existence).

To start completely fresh:

    rm experiments/state/study1-checkpoint.json
    rm -rf experiments/data/raw/study1-replication

## 5-hour reset boundary

The runner's quota retry sleeps until the next 5-hour boundary anchored
at **2026-05-21 03:10 KST** (= 2026-05-20 18:10 UTC). See
`../src/reset_window.py` for the calculation and
`../src/test_reset_window.py` for the validating tests.
