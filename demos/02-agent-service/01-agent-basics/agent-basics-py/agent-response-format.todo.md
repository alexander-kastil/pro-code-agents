# agent-response-format.py – Migration Findings & Follow-up TODO

## Summary

The script was migrated from legacy AgentsClient (threads/runs/messages + response_format on agent) to AIProjectClient + Responses API. We attempted to use `response_format` parameter on `responses.create`, but current SDK rejected it (`TypeError`). We now rely on prompt instructions for JSON-only output and parse the first `output_text` block.

Last execution produced no output at all (likely due to missing/invalid credentials or unset environment variables causing AuthenticationError earlier). Therefore JSON parsing & display is unverified.

## Detected Issues

1. Authentication / Environment: Prior run returned 401; subsequent run produced no console output (potential early exit or missing env vars). Needs validation of `.env` values (`PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT`, Azure Identity context).
2. Missing Explicit JSON Enforcement: Without `response_format`, model might wrap JSON in text or add prose. Risk of parse failure.
3. Output Extraction Fragility: Assumes first content block is `output_text`; may need to handle multiple blocks or different types.
4. Silent Failure Path: If auth fails after prints, we return early; consider ensuring at least diagnostic print before return.
5. No Validation of Parsed Schema: We parse JSON but don't validate expected keys (`name`, `mass_kg`).

## Improvement Plan / TODO

- [ ] Verify environment variables loaded and non-empty; add defensive prints if missing and abort clearly.
- [ ] Add fallback to scan all message content blocks for potential JSON (not just first) and attempt parse on each until success.
- [ ] Implement lightweight schema validation: ensure list of planet objects each with `name` and numeric `mass_kg`.
- [ ] Add retry with simplified prompt if initial parse fails (e.g., enforce: "Respond ONLY with raw JSON array ...").
- [ ] Introduce optional flag `STRICT_JSON=true` to wrap input with system reminder if parse fails.
- [ ] Enhance diagnostics: print length of `response.output`, and types of items encountered when JSON not found.
- [ ] (Optional) Once SDK adds native json response formatting, update call to use official parameter.
- [ ] Document limitations in `migration.md` referencing this script.

## Acceptance Criteria

- Running script prints endpoint/model, status, timing, raw JSON text, parsed JSON, validation summary (planet count).
- Graceful message when JSON parse fails with suggested remediation.
- No unhandled exceptions during missing env or auth failure.

## Notes

Avoid over-engineering: keep demo readable; minimal error handling, following repository standards.
