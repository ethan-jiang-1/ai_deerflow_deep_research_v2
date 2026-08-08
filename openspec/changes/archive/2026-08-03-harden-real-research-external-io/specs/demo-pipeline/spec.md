> req: DPL-009

## ADDED Requirements

### Requirement: Configured real-demo web reads have bounded transient recovery

When a standalone real-demo recipe exposes configured `web_search` or `web_fetch`,
each Tavily-backed search or extraction SHALL be treated as an idempotent read with a
60-second maximum duration for each attempt. The direct demo tool boundary SHALL make
at most three total attempts for one read. It SHALL retry only a direct timeout,
transport/protocol failure, Tavily usage-limit error, HTTP 429, or an HTTP status in
the inclusive range 500-599; its cancellable backoff SHALL be one second before
attempt two and two seconds before attempt three. A successful retry SHALL return the
normal bounded tool payload and preserve the existing same-run search-to-fetch
provenance rule.

Authentication, malformed input, non-429 HTTP 4xx, unknown exceptions, and
cancellation SHALL not receive another attempt. Cancellation SHALL propagate rather
than becoming an unavailable result. A terminally failed read SHALL return only the
existing bounded redacted unavailable payload for its tool name; it SHALL not expose
credentials, provider response data, exception text, or a new lifecycle/graph outcome.
The demo tool boundary SHALL not create a second worker or lifecycle retry controller.
(`DPL-009`)

#### Scenario: A transient search failure recovers within the read bound
- **WHEN** the first direct `web_search` attempt receives a timeout, transport failure,
  Tavily usage-limit error, HTTP 429, or HTTP 500-599 response and its second attempt succeeds
- **THEN** the tool makes exactly two attempts with the one-second cancellable backoff
  and returns the normal bounded search payload

#### Scenario: A transient fetch failure exhausts the read bound
- **WHEN** three direct `web_fetch` attempts each receive a retry-eligible transient
  failure
- **THEN** the tool makes exactly three attempts with only the one- and two-second
  backoffs, returns the bounded `web_fetch_unavailable` payload, and does not alter
  the existing worker or lifecycle outcome itself

#### Scenario: Non-transient failure does not consume retry budget
- **WHEN** a direct search or fetch attempt receives authentication, malformed input, a
  non-429 HTTP 4xx, or an unknown exception
- **THEN** the tool returns its bounded unavailable payload after that one attempt and
  does not schedule a backoff or another provider call

#### Scenario: Cancellation remains an outer control signal
- **WHEN** the standalone run is cancelled during a direct web-read attempt or its
  configured backoff
- **THEN** cancellation propagates, no later attempt starts, and the tool does not
  return an unavailable payload as if the read completed
