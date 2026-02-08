# Research Findings: Advanced - Recurring Tasks & Due Dates

**Feature**: Advanced - Recurring Tasks & Due Dates
**Created**: 2026-01-15

## R01: Timezone Handling Best Practices

**Decision**: Use UTC for storage, convert to user's local timezone for display
**Rationale**: UTC storage prevents issues with daylight saving time changes and allows for consistent calculations across all users. The frontend will handle conversion to the user's local timezone using JavaScript's Intl API.
**Alternatives considered**:
- Storing in user's local timezone (problematic with DST changes)
- Storing both UTC and local (unnecessary complexity)

## R02: Due Date/Time Detection Logic Placement

**Decision**: Server-side calculation with client-side display
**Rationale**: Server provides authoritative status that's consistent across all clients. The API will return computed status fields (is_overdue, is_due_soon, is_due_today) that the frontend can display immediately without additional computation.
**Alternatives considered**:
- Pure client-side (timezone inconsistencies, inaccurate calculations)
- Pure server-side without status fields (requires client to duplicate logic)

## R03: Recurrence Chain Failure Handling

**Decision**: Graceful degradation with error logging
**Rationale**: If recurrence creation fails, the system should continue operating. The failure should be logged for monitoring, but the user's task completion should succeed. A background job could handle retries if needed.
**Alternatives considered**:
- Fail entire operation (too disruptive to user experience)
- Silent failure (no visibility into problems)

## R04: Date/Time Picker Component Selection

**Decision**: Use react-datepicker or similar well-maintained library
**Rationale**: Leverages community-tested component rather than building custom. Should support both date and time selection with good accessibility.
**Alternatives considered**:
- Building custom component (time-intensive, reinventing wheel)
- Using native HTML input (limited functionality, inconsistent UX)

## R05: Relative Time Calculation Library

**Decision**: Use date-fns for frontend relative time calculations
**Rationale**: Lightweight, well-maintained library with excellent internationalization support. Provides functions like `formatDistanceToNow` for relative time strings.
**Alternatives considered**:
- moment.js (larger bundle size, mostly in maintenance mode)
- dayjs (also good, but date-fns has better relative time formatting)

## R06: Recurrence Rule Storage Format

**Decision**: Simple string enum (daily/weekly/monthly/yearly)
**Rationale**: Simple to implement and understand. Sufficient for the specified requirements. Can be extended later if more complex recurrence patterns are needed.
**Alternatives considered**:
- RFC 5545 RRULE format (overly complex for basic needs)
- Interval-based integers (less readable)

## R07: Database Index Strategy

**Decision**: Add indexes on due_datetime and recurrence_rule fields
**Rationale**: Queries filtering by due date status (overdue, due soon) will be common and need to be performant. Indexes will speed up these operations.
**Alternatives considered**:
- No indexes (performance issues with larger datasets)
- Complex composite indexes (over-engineering for current needs)