# TaskDesk API — Lab 5 variant

This is a copy of `src/ticket-api`, extended for **Lab 5: Generating Test Data &
Building a Test Harness**. It is a separate app on purpose so Lab 4 (`src/ticket-api`)
keeps working unmodified — this copy is where Lab 5 gets its own entities and rules.

New in this variant:

- `Category` and `Comment` entities.
- A ticket **status workflow** (`open -> in_progress -> resolved -> closed`, plus
  `in_progress -> open` and `resolved -> in_progress`) enforced server-side.
- A "resolution note" rule: a ticket can't move to `resolved` without at least one
  comment.
- Paginated, oldest-first `GET /tickets/`.
- `legacy_data/taskdesk_classic_export.csv` — a messy export from the fictional
  "TaskDesk Classic '03" system, used in the migration-day task.

See [`docs/lab5.md`](../../docs/lab5.md) for the full lab instructions. The original
`src/ticket-api` is untouched.
