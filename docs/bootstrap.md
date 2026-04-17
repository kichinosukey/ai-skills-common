# Bootstrap on a new machine

```bash
# 1. Clone each namespace into ~/.ai-skills/
git clone <common-remote>     ~/.ai-skills/_common
git clone <mentalbase-remote> ~/.ai-skills/mentalbase   # if authorized
git clone <loochs-remote>     ~/.ai-skills/loochs       # if authorized

# 2. Put sync-skills on PATH
mkdir -p ~/.local/bin
ln -s ~/.ai-skills/_common/bin/sync-skills ~/.local/bin/sync-skills
# ensure ~/.local/bin is on PATH (e.g. in ~/.zshrc)

# 3. In each project repo with a skills.yaml, run:
cd ~/projects/<repo>
sync-skills
```

Verify:

```bash
ls -la .agents/skills/     # entries should be symlinks into ~/.ai-skills/
sync-skills --dry-run      # should report no changes on a second run
```

## Updating skills

Edit the skill inside `~/.ai-skills/<namespace>/<skill>/` and commit to the namespace repo. No per-project changes needed — agents resolve via the symlink.
