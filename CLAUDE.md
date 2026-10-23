# PyRevit Development Conventions

Shared setup for KCA.extension and Bimming.extension (Máximo Cubero). This
file is meant to be identical in both repos. Extension-specific details
(exact transaction prefix, specific subfolder names, per-script notes)
belong in each repo's own additions to this file, not here.

## Environment

- pyRevit extensions using IronPython, targeting Revit versions declared per
  script via `__min_revit_ver__` / `__max_revit_ver__` (currently 2021-2026).
- Standard script header: `__title__`, `__doc__` (ending with `Author:
  Máximo Cubero`), `__min_revit_ver__`, `__max_revit_ver__`.

## Script structure

- Scripts execute at module level - do **not** wrap the logic in `def
  main()`.
- Standard section comments, each followed by a `#===...` divider line:
  `# CONSTANTS`, `# IMPORTS`, `# VARIABLES`, `# HELPERS` (when needed),
  `# MAIN`.
- Standard variables: `doc = __revit__.ActiveUIDocument.Document`, `uidoc =
  __revit__.ActiveUIDocument`, `app = __revit__.Application` (only declare
  `app` if the script actually uses it).
- Import the extension's `Snippets._bimcore_*` helper modules (e.g.
  `_bimcore_functions`, `_bimcore_complex_def`, `_bimcore_import`,
  `_bimcore_pyrevit`) instead of reimplementing shared logic.
- Use `from pyrevit import forms, script` for alerts and the output window;
  `output = script.get_output()` when the script needs `print_md` /
  `linkify`.

## Shared parameters

- Custom shared parameters use the `_KCASP` suffix (e.g. `Usage_KCASP`,
  `Unit ID_KCASP`).
- Read parameters defensively. Standard pattern is a helper like
  `get_param_as_string(param)` that branches on `StorageType` and returns
  `None` for missing/empty values - never assume a parameter exists.

## Worksharing

- Only call `param.Set(value)` when the new value actually differs from the
  current one. Calling `.Set()` unconditionally takes element ownership in
  a workshared model even when nothing changes, which blocks other users
  unnecessarily.

## Project folder resolution (server paths)

- Root: `TARGET_PATH = r"Z:\\"`.
- Project number: read from `doc.ProjectInformation.Number` (the internal
  Project Number) - **not** from Project Info's "File Name" field, which
  holds a different, CDE-style project number.
- Resolve the project's folder name via
  `create_folder_dictionary(TARGET_PATH)[project_number]`.
- Standard subpath once you have the project name:
  `{project_name}\03 Technical\01 BIM\01 Revit\10 Resources\{SubfolderName}`
  (e.g. "Excel Type Parameter Tables" for the Excel-driven type parameter
  workflow, "KCA pyRevit Databases" for KCA's script-generated databases).

## Output style

- Keep console output minimal - surface errors/issues, not verbose success
  logs. One summary line is enough for a clean run.
- Use `output.print_md('## ...')` headers only for sections reporting a
  real problem.
- Use `output.linkify(element.Id)` when reporting problem elements, so the
  person can jump straight to them from the output window.

## Transactions

- Transaction name pattern: `"{ExtensionPrefix}-{Script Name}"` - use
  `"KCA-"` in KCA.extension, `"Bimming-"` in Bimming.extension.

## Bimming.extension notes

Extension-specific details. The sections above are shared with KCA.extension.
These notes were recovered on 23 Oct 2026 from the XPS chats.

- Personal extension. It is published to
  `Y:\BIM\Revit AddIns\PyRevit Bimming Extension\Bimming.extension` with KCAdev's
  "Publish Bimming". Transactions use the `Bimming-` prefix.
- 12–13 Aug 2026: added "Presentation Mode ON/OFF" (Views panel; separate buttons
  for on and off; the user adds the icons) and a dark/light mode switch (Misc).
- 21 Aug 2026: "Create Workset Views Set" was renamed to `Audit\nWorksets`.
- 30 Sep 2026: Revit 2026 compatibility pass. `.IntegerValue` was replaced with
  `get_elementid_value(...)` and `ElementId(int)` with `get_elementid_from_value(...)`
  (both work in 2021-2026). `Buildup` and `Type Parameter Updated` were deleted from
  `WIP2.Panel OFF`.
