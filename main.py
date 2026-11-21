import os, sys, json, urllib.request as U

ENV = os.environ.get("MAKEFUN_ENV_URL", "http://127.0.0.1:8080").rstrip("/")
V = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}
F = "abcdefgh"
CTR = {s: 20 for s in ("d4", "e4", "d5", "e5")} | {s: 10 for s in ("c4", "f4", "c5", "f5")}
K_DIRS = ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1))

def post(path, body):
    req = U.Request(ENV + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    with U.urlopen(req) as res: return json.load(res)

def board_of(fen):
    b = {}
    for i, r in enumerate(fen.split()[0].split("/")):
        f = 0
        for c in r:
            if c.isdigit(): f += int(c)
            else: b[F[f] + str(8 - i)] = c; f += 1
    return b

find_king = lambda b, w: next((s for s, p in b.items() if p == ("K" if w else "k")), None)

def is_attacked(b, sq, by_white):
    if not sq: return False
    fi, r = F.index(sq[0]), int(sq[1])
    pawn, knight, king = ("P", "N", "K") if by_white else ("p", "n", "k")
    pr = r - 1 if by_white else r + 1
    if 1 <= pr <= 8 and any(0 <= fi + df < 8 and b.get(F[fi + df] + str(pr)) == pawn for df in (-1, 1)):
        return True
    if any(0 <= fi + d[0] < 8 and 1 <= r + d[1] <= 8 and b.get(F[fi + d[0]] + str(r + d[1])) == knight for d in K_DIRS):
        return True
    rq, bq = (("R", "Q") if by_white else ("r", "q")), (("B", "Q") if by_white else ("b", "q"))
    for dirs, pcs in ((((1, 0), (-1, 0), (0, 1), (0, -1)), rq), (((1, 1), (1, -1), (-1, 1), (-1, -1)), bq)):
        for df, dr in dirs:
            for s in range(1, 8):
                nf, nr = fi + df * s, r + dr * s
                if not (0 <= nf < 8 and 1 <= nr <= 8): break
                pc = b.get(F[nf] + str(nr))
                if pc:
                    if (s == 1 and pc == king) or pc in pcs: return True
                    break
    return False

def max_opp_capture(b, us_white):
    them, max_g = not us_white, 0
    for sq, pc in b.items():
        if (pc.isupper() if us_white else pc.islower()):
            val = V.get(pc.lower(), 0)
            if val < 20000 and is_attacked(b, sq, them):
                max_g = max(max_g, val if not is_attacked(b, sq, us_white) else max(0, val - 100))
    return max_g

def evaluate_move(b, us_white, mv):
    fr, to, promo = mv[:2], mv[2:4], mv[4:5]
    mover, victim = b[fr], b.get(to)
    gain = V.get(victim.lower(), 0) if victim else (100 if mover.lower() == "p" and fr[0] != to[0] else 0)
    if promo: gain += V.get(promo.lower(), 900) - 100
    nb = dict(b)
    nb[to] = promo.upper() if (mover.isupper() and promo) else (promo.lower() if promo else mover)
    del nb[fr]
    if mover.lower() == "p" and fr[0] != to[0] and not victim: nb.pop(to[0] + fr[1], None)
    if is_attacked(nb, find_king(nb, us_white), not us_white): return -999999
    score = (gain - max_opp_capture(nb, us_white)) * 10 + CTR.get(to, 0)
    ml = mover.lower()
    if ml == "k" and abs(F.index(fr[0]) - F.index(to[0])) == 2: score += 50
    if ml in "nb" and fr[1] in "18": score += 20
    if ml == "p":
        adv = int(to[1]) - int(fr[1]) if us_white else int(fr[1]) - int(to[1])
        score += adv * 4
    return score

def choose(fen, legal):
    if not legal: return ""
    if len(legal) == 1: return legal[0]
    try:
        white, b = (fen.split()[1] == "w"), board_of(fen)
        return max(legal, key=lambda mv: evaluate_move(b, white, mv))
    except Exception: return legal[0]

def play_all():
    while True:
        try: g = post("/game", {})
        except Exception: break
        if g.get("status") == "done": break
        while g.get("status") == "your_move":
            legal = g.get("legal_moves") or []
            mv = choose(g.get("fen", ""), legal) if legal else ""
            if not mv: break
            try: g = post("/move", {"game": g["game"], "move": mv})
            except Exception: break
        print(f"game {g.get('game')}: {g.get('outcome')} by {g.get('reason')}", file=sys.stderr)

if __name__ == "__main__":
    play_all()
