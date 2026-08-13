# A-004-T01 Scenario-Rename Validator Owner Research

Date: 2026-08-13

## Question and Boundary

Determine whether strict OpenSpec delta validation's rejection of a scenario-title
rename is owned by repository-local policy or by the installed OpenSpec CLI. This
is a read-only investigation of the installed CLI package and first-party package
materials. It does not inspect or modify `deerflow/`, application code, specs,
repository validators/configuration, todos, or the progressive plan.

## Conclusion

**Owner: the installed upstream OpenSpec CLI package, `@fission-ai/openspec@1.8.0`,
published by OpenSpec Contributors (Fission-AI/OpenSpec).**

The `openspec validate <change> --strict` command instantiates the package's
`Validator`, which compares each `MODIFIED` requirement with the corresponding
current main-spec block. That check treats scenario headings as identity strings
and reports every old heading absent from the new block. The packaged schema defines
only `RENAMED Requirements` at the requirement level; no scenario-rename delta
operation or stable scenario identifier is implemented. The same missing-scenario
function is invoked by archive/apply, so bypassing the authoring validation would
not make a title-only rename archive-safe.

**Disposition: keep A-004-T01 as an upstream OpenSpec tooling change.** Do not
rename the two `research-run-experience` scenario headings in a normal repository
delta until a compatible OpenSpec release implements an explicit scenario identity
and rename operation, with a red validator/archival test. A later, separately scoped
spec-maintenance change may then rename the headings. This is not owned by
`deep_research_harness/`, repository governance scripts, or `deerflow/`.

## Evidence

### Installed package identity

Commands run from `/Users/bowhead/ai_deerflow_deep_research_v2`:

```text
$ command -v openspec
/Users/bowhead/.nvm/versions/node/v22.23.1/bin/openspec

$ readlink /Users/bowhead/.nvm/versions/node/v22.23.1/bin/openspec
../lib/node_modules/@fission-ai/openspec/bin/openspec.js

$ openspec --version
1.8.0

$ npm ls -g --depth=0 @fission-ai/openspec
/Users/bowhead/.nvm/versions/node/v22.23.1/lib
└── @fission-ai/openspec@1.8.0

$ npm view @fission-ai/openspec@1.8.0 version dist.tarball repository --json
{
  "version": "1.8.0",
  "dist.tarball": "https://registry.npmjs.org/@fission-ai/openspec/-/openspec-1.8.0.tgz",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/Fission-AI/OpenSpec.git"
  }
}
```

The installed package metadata at
`/Users/bowhead/.nvm/versions/node/v22.23.1/lib/node_modules/@fission-ai/openspec/package.json`
names the package `@fission-ai/openspec`, version `1.8.0`, author `OpenSpec
Contributors`, homepage `https://github.com/Fission-AI/OpenSpec`, and CLI bin
`openspec: ./bin/openspec.js`.

### CLI validation calls the package Validator

In installed source
`dist/commands/validate.js`, lines 3 and 143-149 import `Validator` from
`../core/validation/validator.js`, construct `new Validator(opts.strict)`, and
call `validator.validateChangeDeltaSpecs(changeDir, { mainSpecsDir: root.specsDir })`.
Therefore `--strict` is executed by the installed package validation surface,
against the repository's main-spec path, rather than by a repository-local validator.

`dist/core/validation/validator.js`, lines 256-262, sends each parsed modified
block and main spec into `findScenarioLossIssues`. Lines 467-475 call
`findMissingCurrentScenarios(current, block)` and produce an `ERROR` stating that
the modified requirement omits scenario(s) held by the current spec. Lines 609-611
then make a strict report valid only when it has neither errors nor warnings.

### Scenario comparison preserves title strings, not an independent identity

In installed source `dist/core/parsers/requirement-blocks.js`:

- Lines 261-267 document that a `MODIFIED` block replaces the entire requirement
  block and its scenario-loss check is shared by validation and archive.
- Lines 269-290 build a multiplicity-aware map from incoming scenario `name` and
  report every current scenario `name` not present in that map.
- Lines 292-310 parse a scenario name only from the Markdown heading
  `#### Scenario: <name>`.

The following package-level, no-write reproduction calls that exported comparison
function directly:

```text
$ node --input-type=module <<'NODE'
... findMissingCurrentScenarios(currentWithLegacyTitle, modifiedWithCorrectedTitle) ...
... findMissingCurrentScenarios(currentWithLegacyTitle, modifiedWithLegacyTitle) ...
NODE
{"renamed":["Legacy title"],"unchanged":[]}
```

The two blocks have identical requirement text and WHEN/THEN body; only
`#### Scenario:` changes from `Legacy title` to `Corrected title`. The installed
logic reports the original title as missing. Keeping the title leaves no missing
scenario. This reproduces the title-rename result without changing repository specs.

### No packaged scenario-rename syntax

The package's first-party spec-driven schema at
`schemas/spec-driven/schema.yaml`, lines 73-84, lists exactly four delta operations:
`ADDED`, `MODIFIED`, `REMOVED`, and `RENAMED Requirements`; it describes the latter
as a requirement-name change using `FROM:/TO:`. Lines 96-100 instruct authors to
copy the entire existing requirement block, including all scenarios, into a
`MODIFIED` block.

The parser corroborates that boundary:

- `dist/core/parsers/requirement-blocks.js`, lines 102-130 recognizes only the four
  requirement sections, and lines 235-258 parse `FROM:/TO:` only when each side
  matches `### Requirement:`.
- `dist/core/parsers/change-parser.js`, lines 124-160 parses `RENAMED` only as
  requirement pairs matching the same `### Requirement:` form.

No installed schema, parser, or validator evidence was found for a scenario-level
`FROM:/TO:` form, a scenario ID, or a mapping from an old scenario title to a new
one.

### Archive uses the same rule

The installed archive/apply implementation imports the same
`findMissingCurrentScenarios` function in `dist/core/specs-apply.js` line 11. At
lines 320-345, before replacing a `MODIFIED` requirement block, it calls the
function and throws when any current scenario is absent. The validator source also
states at lines 392-395 that validation reports only loss that archive would refuse.

Consequently, an alternative local invocation that merely avoids `--strict` would
not solve the A-004-T01 data-loss guard at archive time.

### Repository-local boundary check

`openspec/config.yaml` defines authoring context, project rules, and commands to
run, but contains no replacement scenario validator or scenario-rename syntax.
The repository's `openspec/governance/check_project_specs.py`, lines 7-13, expressly
states that it does not check delta specs and delegates them to `OpenSpec
validate/archive`. This rules out the local governance checker as the owner of this
behavior.

## Limits

- This establishes ownership for the installed `1.8.0` CLI, not the exact source
  commit, release history, or behavior of future OpenSpec versions.
- The package metadata and npm registry record identify the published package and
  repository, but this investigation did not clone, inspect, or modify that upstream
  repository.
- The direct function reproduction proves the installed comparison algorithm. It is
  not an end-to-end new-change test and deliberately does not modify an A-004 delta,
  main spec, or archive.
- The inspection establishes that repository governance does not supply this delta
  check. It does not prove no other local tool could impose additional constraints.
- No `deerflow/` path was searched, read, or modified; its ownership is irrelevant
  to this CLI behavior.

## Recommended Next Authorized Work

Create an upstream OpenSpec proposal/issue or a separately authorized tooling change
against `Fission-AI/OpenSpec`, starting with a red test that distinguishes a true
scenario deletion from an explicit title rename. The design must introduce an
unambiguous, archive-consumable mapping or stable scenario identifier; title matching
alone cannot preserve review identity when labels change. Keep the current legacy
titles and their already-correct operative bodies until that upstream capability is
available.
