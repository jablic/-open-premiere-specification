# Developer Reference Style Guide

This guide defines how developer-facing Premiere Pro reference pages must be written.

## Primary rule

Document API contracts, not only API descriptions.

A method page must answer:

- What does this call do?
- What objects does it read?
- What objects does it mutate?
- What objects does it create?
- What does it explicitly not mutate?
- What preconditions must be true?
- What postconditions are expected?
- What failure modes are known?
- Which Premiere versions were verified?
- Which evidence supports the claims?

## Object reference page structure

Use this order for object chapters:

1. Overview.
2. Developer surface.
3. Object identity.
4. Lifetime.
5. Ownership and references.
6. State machine.
7. Properties.
8. Methods.
9. Mutation rules.
10. Serialization mapping.
11. Cross-surface mapping: ExtendScript / UXP / CEP / QE / SDK.
12. Known issues.
13. Version matrix.
14. Reverse engineering notes.
15. Production notes.
16. Examples.
17. See also.

## Method reference page structure

Use this order for method pages:

1. Purpose.
2. Surface and status.
3. Syntax.
4. Parameters.
5. Return value.
6. Reads.
7. Mutates.
8. Creates.
9. Does not mutate.
10. Preconditions.
11. Postconditions.
12. Failure modes.
13. Side effects.
14. Threading / blocking behaviour.
15. Performance notes.
16. Version matrix.
17. Evidence.
18. Examples.
19. Production notes.
20. Related APIs.

## Language rules

- Use `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` only for contract-level statements.
- Do not mix official facts with reverse-engineered observations.
- Mark undocumented APIs explicitly.
- Never imply QE stability unless evidence exists.
- Avoid vague phrases such as "probably", "usually", or "it seems" unless the statement is explicitly marked as hypothesis.

## Code examples

Examples must state:

- target runtime;
- tested Premiere version if known;
- expected result;
- side effects;
- known limitations.

