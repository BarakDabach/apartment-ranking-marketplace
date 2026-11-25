"""Practical walking distance on a vector common-area plan (parking / storage levels).

Rasterizes the plan's vector walls (dark wall outlines >= --wall-min-width, near-neutral dark/grey fills
for columns and wall hatch) and runs an 8-connected Dijkstra from a source point (building elevator
lobby) to target points (stall labels / storage doors). Walls are passable at a high per-pixel penalty
because door openings are often drawn closed (thresholds, door leaves, text); the reported distance is
the geometric length of the chosen path, not the penalized cost.

Coordinates are *displayed* page points (after page rotation), i.e. what a rendered image shows.

usage:
  python plan_walk.py PLAN.pdf --scale M_PER_PT --from X,Y --to ID:X,Y [--to ID:X,Y ...] [--png OUT.png]
  python plan_walk.py PLAN.pdf --scale 0.058 --from 1255,705 --to P46:1681,1049 --png route.png
Output: JSON {id: {"walk_m": float|null, "straight_m": float}} on stdout.

Calibrate --scale from on-sheet dimension strings and cross-check with a stall depth (~5.0 m).
"""
import argparse
import heapq
import json
import math

import pymupdf
from PIL import Image, ImageDraw


def wall_mask(page, zoom, wall_min_w):
    M = page.rotation_matrix * pymupdf.Matrix(zoom, zoom)
    w, h = int(page.rect.width * zoom) + 1, int(page.rect.height * zoom) + 1
    m = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(m)
    for d in page.get_drawings():
        col, fill, wd = d.get("color"), d.get("fill"), d.get("width") or 0
        is_fill = fill is not None and max(fill) < 0.65 and max(fill) - min(fill) < 0.05
        is_stroke = col is not None and max(col) < 0.05 and wd >= wall_min_w
        if not (is_fill or is_stroke):
            continue
        lw = max(1, round(wd * zoom))
        polys, poly = [], []
        for it in d["items"]:
            if it[0] == "l":
                pts = [it[1] * M, it[2] * M]
            elif it[0] == "c":
                p0, p1, p2, p3 = it[1:5]
                pts = [(p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3) * M
                       for t in (i / 8 for i in range(9))]
            elif it[0] in ("re", "qu"):
                q = (it[1].quad if it[0] == "re" else it[1]) * M
                pts = [q.ul, q.ur, q.lr, q.ll, q.ul]
            else:
                continue
            xy = [(p.x, p.y) for p in pts]
            dr.line(xy, fill=1, width=lw)
            if it[0] in ("re", "qu"):
                polys.append(xy)
                continue
            if poly and math.hypot(poly[-1][0] - xy[0][0], poly[-1][1] - xy[0][1]) > 0.5:
                polys.append(poly)
                poly = []
            poly += xy if not poly else xy[1:]
        polys.append(poly)
        if d.get("fill") is not None:
            for p in polys:
                if len(p) >= 3:
                    dr.polygon(p, fill=1)
    return w, h, m.tobytes()


def disk(w, h, blocked, x, y, r_px):
    out = []
    for yy in range(max(0, int(y - r_px)), min(h, int(y + r_px) + 1)):
        for xx in range(max(0, int(x - r_px)), min(w, int(x + r_px) + 1)):
            d = math.hypot(xx - x, yy - y)
            if d <= r_px and not blocked[yy * w + xx]:
                out.append((yy * w + xx, d))
    if not out and 0 <= int(x) < w and 0 <= int(y) < h:
        out.append((int(y) * w + int(x), 0.0))
    return out


def walk(w, h, blocked, src, targets, penalty):
    """src: list of (pixel, d0); targets: {id: [(pixel, d_extra)]}. Returns {id: (length_px, end_pixel)}, prev."""
    n = w * h
    cost, length, prev = [math.inf] * n, [0.0] * n, [-1] * n
    pq = []
    for i, d in src:
        cost[i] = length[i] = d
        pq.append((d, i))
    heapq.heapify(pq)
    pending = {i for pix in targets.values() for i, _ in pix}
    s2 = math.sqrt(2)
    nb = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, s2), (1, -1, s2), (-1, 1, s2), (1, 1, s2)]
    while pq and pending:
        c0, i = heapq.heappop(pq)
        if c0 > cost[i]:
            continue
        pending.discard(i)
        y, x = divmod(i, w)
        for dx, dy, c in nb:
            xx, yy = x + dx, y + dy
            if 0 <= xx < w and 0 <= yy < h:
                j = yy * w + xx
                step = c + (penalty if blocked[j] or (dx and dy and blocked[y * w + xx] and blocked[yy * w + x]) else 0)
                if c0 + step < cost[j]:
                    cost[j], length[j], prev[j] = c0 + step, length[i] + c, i
                    heapq.heappush(pq, (c0 + step, j))
    res = {}
    for k, pix in targets.items():
        best = min(((cost[i] + r, length[i] + r, i) for i, r in pix), default=(math.inf, 0, -1))
        res[k] = None if math.isinf(best[0]) else (best[1], best[2])
    return res, prev


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--page", type=int, default=0)
    ap.add_argument("--scale", type=float, required=True, help="metres per displayed PDF point")
    ap.add_argument("--from", dest="src", required=True, help="X,Y of the elevator lobby")
    ap.add_argument("--to", action="append", required=True, help="ID:X,Y (repeatable)")
    ap.add_argument("--zoom", type=float, default=0.7)
    ap.add_argument("--wall-min-width", type=float, default=0.2)
    ap.add_argument("--penalty", type=float, default=15, help="extra cost (px) per wall pixel crossed")
    ap.add_argument("--seed-r", type=float, default=0.8, help="m")
    ap.add_argument("--target-r", type=float, default=1.2, help="m")
    ap.add_argument("--png")
    a = ap.parse_args()

    page = pymupdf.open(a.pdf)[a.page]
    w, h, blocked = wall_mask(page, a.zoom, a.wall_min_width)
    px_per_m = a.zoom / a.scale
    sx, sy = map(float, a.src.split(","))
    tg = {}
    for t in a.to:
        k, xy = t.rsplit(":", 1)
        tg[k] = tuple(map(float, xy.split(",")))
    src = disk(w, h, blocked, sx * a.zoom, sy * a.zoom, a.seed_r * px_per_m)
    tpix = {k: disk(w, h, blocked, x * a.zoom, y * a.zoom, a.target_r * px_per_m) for k, (x, y) in tg.items()}
    res, prev = walk(w, h, blocked, src, tpix, a.penalty)
    out = {k: {"walk_m": None if res[k] is None else round(res[k][0] / px_per_m, 1),
               "straight_m": round(math.dist((sx, sy), tg[k]) * a.scale, 1)} for k in tg}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if a.png:
        im = page.get_pixmap(matrix=pymupdf.Matrix(a.zoom, a.zoom), alpha=False)
        img = Image.frombytes("RGB", (im.width, im.height), im.samples)
        dr = ImageDraw.Draw(img)
        for k, v in res.items():
            if v is None:
                continue
            i, path = v[1], []
            while i >= 0:
                path.append(divmod(i, w)[::-1])
                i = prev[i]
            dr.line(path, fill=(255, 0, 0), width=2)
        img.save(a.png)


if __name__ == "__main__":
    main()
