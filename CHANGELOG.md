# Changelog

## 1.3.1

- center `om_context` and `om_search` excerpts around the query term so exact shared-memory matches are visible in Hermes results

## 1.3.0

- align the standalone plugin with current Hermes user-installed memory provider discovery
- mark the manifest as `kind: exclusive`
- bump the supported `observational-memory` line to `>=0.6.3,<0.7`
- add best-effort OM Cluster pull-before-context when `sync_before_context` is enabled
- make `om_remember` write OM Cluster observation records when cluster mode is active
- remove the old source-tree symlink workaround from install docs

## 1.2.0

- bump the supported `observational-memory` line to `>=0.5.0,<0.6.0`
- refresh install and after-install docs for the 0.5.0 release line
- document OM 0.5.0 search/runtime improvements that matter for shared Hermes memory setups, including QMD 2.1 support and `om status` / `om doctor` troubleshooting

## 1.1.0

- bump observational-memory dependency to >=0.4.0 for Hermes transcript parser support
- om 0.4.1 adds `transcripts/hermes.py` which properly parses Hermes v0.7.0 JSONL session logs, filtering to user/assistant prose and summarizing tool calls as one-liners (19x noise reduction on typical sessions)
- om 0.4.1 adds `observe_hermes_transcript()` and `observe_all_hermes()` for cron-based session observation

## 1.0.0

- initial standalone release of the Hermes Observational Memory directory plugin
- tracks the reviewed provider implementation from the upstream Hermes integration work
- includes standalone tests and install docs for Git-based plugin installs
