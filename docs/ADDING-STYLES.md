# Adding a new style to the plugin (maintainers)

1. **Train it** in any project: `/editing-style:build <link or description>` → it becomes `style-NN` / `cap-NN` /
   `script-NN` in that project's `reel-library/` with a preview PNG.
2. **Promote it** into this repo:
   - card → `skills/reel-edit/library-seed/<kind>/<id>.md` (give it a short unique name + a command name)
   - preview → `skills/reel-edit/styles/<id>.png`
   - new CSS / template parts → `skills/reel-edit/templates/` (keep the origin header)
   - a command → `commands/<name>.md` (copy `commands/folio.md`, change the style)
   - `reel_lib.py` → add it to `STYLES` and `STYLE_NAMES` (or `CAPTION_NAMES`)
   - `STYLES.md`, `library-seed/INDEX.md`, README tables
3. **Release:** bump `version` in `.claude-plugin/plugin.json`, add a CHANGELOG entry, `claude plugin validate .`,
   commit, push to `main`, tag with `claude plugin tag .`. Users get it with
   `claude plugin marketplace update claude-editing-style` → `claude plugin update editing-style@claude-editing-style` →
   `/editing-style:update`.

---
Created by Tejas — https://github.com/Tejas-pr/claude-editing-style
