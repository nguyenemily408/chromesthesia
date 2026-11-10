# Working on The Sound of Color

Always explain changes in plain English. The project owner is not a software engineer.

## Coordination

Read README.md, AGENT-WORK.md, and the latest handoff before editing. Record your task, the files or renderer blocks you own, and your status in AGENT-WORK.md. Read files again immediately before editing because another session may have changed them.

Only one agent integrates changes to index.html at a time. Prefer separate Git branches and working folders for simultaneous tasks. When sessions share a folder, agree on separate files or named renderer blocks and preserve all other changes.

## Roles

- Codex coordinates requests, integrates completed work, checks the app, maintains the agent record, and uploads approved project files to GitHub.
- The Claude visual session owns its assigned renderer blocks. Its latest assignment is the WC watercolor renderer. Write results and verification limits in claude-handoff.md.
- The Claude Creator MCP session generates animation assets using the real LottieFiles tools and builds the separate creator-lab.html demo. Own creator-lab-prefixed assets. Coordinate any small navigation link in index.html with the integrator.
- A review session, when requested, checks completed work and reports findings before making edits.

## Verification and handoff

Check JavaScript syntax. Check the actual app in a visible browser, including animation playback and controls. State whether testing used music, synthetic inputs, or still frames. Record failures and remaining work honestly. Do not label planned or running work as complete.

Update AGENT-WORK.md when starting, finishing, or encountering a blocker. Include the date, changed files, tests run, result, and next step. Include a short change summary in each Git commit.

Upload project files and intentional assets only. Keep credentials, account details, recordings, support chats, and unrelated workspace files outside the repository.
