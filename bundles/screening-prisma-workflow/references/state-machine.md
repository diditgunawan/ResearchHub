# Item state machine (per project, per stage)
```
imported ─▶ [dedup stage] ─▶ duplicate (removed, counted) | unique
unique ─▶ TA_pending ─▶ (all required reviewers decided?)
   ├─ all include/maybe-agree ─▶ TA_included ─▶ FT_pending
   ├─ all exclude ─▶ TA_excluded (reason counted)
   └─ mismatch ─▶ TA_conflict ─▶ (resolution) ─▶ TA_included | TA_excluded
FT_pending ─▶ same logic ─▶ FT_included (final included) | FT_excluded (reason counted)
```
Rules: 'maybe' from any reviewer with no resolution keeps item pending; single-reviewer projects (allowed, flagged "single screening") skip conflict logic; stage completion requires zero pending and zero conflicts.
