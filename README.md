# tiny-chess-engine

[![Make.fun Bounty](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![Live Rank](https://make.fun/badge/tiny-chess-01/sparkleebabi168-max/tiny-chess-engine/rank.svg)](https://make.fun/bounty/tiny-chess-01)
[![Live Reward](https://make.fun/badge/tiny-chess-01/sparkleebabi168-max/tiny-chess-engine/reward.svg)](https://make.fun/bounty/tiny-chess-01)

Strongest chess engine in 4 KB of Python for Make.fun bounty.

## Engine Features
- Compact, deterministic single-file Python chess engine in `main.py` (< 4,096 bytes).
- Standard UCI protocol support (`uci`, `isready`, `position`, `go`, `quit`).
- Automated `MAKEFUN_ENV_URL` driver for automated game trials against house gauntlets.
- Fast 0x88 board representation with negamax search and alpha-beta pruning.
