---
description: Get the newest styles - pulls new built-in video, caption and script styles from the plugin into your reel library without touching your own cards
---
Update the user's reel library from this plugin's `skills/reel-edit/library-seed/`:
1. Tell the user to update the plugin itself first if they haven't (it can't update itself from inside a session):
   `claude plugin marketplace update claude-editing-style` then `claude plugin update editing-style@claude-editing-style`,
   then restart Claude Code. (Or `/plugin` → Marketplaces → update.)
2. Compare `library-seed/` with `./reel-library/`: copy every seed card (video-styles, caption-styles, script-styles,
   previews) whose **id doesn't exist yet**. Never overwrite or delete the user's cards; if a built-in card changed
   (same id, different content), save the new one next to it as `<id>.new.md` and say so.
3. Rebuild `reel-library/INDEX.md` (built-ins + the user's own cards) and show what's new (read the plugin's CHANGELOG.md).
