# Bootstrap on a new machine

```bash
# 1. Clone each namespace into ~/.ai-skills/
git clone https://github.com/kichinosukey/ai-skills-common.git     ~/.ai-skills/ai-skills-common
git clone https://github.com/kichinosukey/ai-skills-mentalbase.git ~/.ai-skills/ai-skills-mentalbase  # if authorized
git clone https://github.com/kichinosukey/ai-skills-loochs.git     ~/.ai-skills/ai-skills-loochs      # if authorized

# 2. (optional) short aliases — some tooling references these
ln -s ai-skills-common     ~/.ai-skills/_common
ln -s ai-skills-mentalbase ~/.ai-skills/mentalbase
ln -s ai-skills-loochs     ~/.ai-skills/loochs

# 3. Install sync-skills to ~/.local/bin (idempotent)
~/.ai-skills/ai-skills-common/bin/install.sh
# ensure ~/.local/bin is on PATH (e.g. in ~/.zshrc)

# 4. In each project repo with a skills.yaml, run:
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
