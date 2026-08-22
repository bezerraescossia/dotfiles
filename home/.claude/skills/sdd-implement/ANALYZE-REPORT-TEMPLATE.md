# Cross-Artifact Analysis Report Template

Output a Markdown report (no file writes):

```markdown
## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements... | Merge phrasing; keep the clearer version |

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**
- Total Requirements / Total Tasks / Coverage % (requirements with ≥1 task)
- Ambiguity Count / Duplication Count / Critical Issues Count
```

Generate stable finding IDs prefixed by category initial (A through H, see SKILL.md Step 5's Detection Passes). Re-running on unchanged artifacts should produce consistent IDs and counts.
