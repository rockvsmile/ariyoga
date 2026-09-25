#!/usr/bin/env python3
"""Kiểm tra template hoặc workflow có hợp lệ với danh mục node không.

    python tools/kiem_tra_mau.py thu-vien/mau-workflow/<ten>.json
    python tools/kiem_tra_mau.py du-an/<id>/workflow.json
    python tools/kiem_tra_mau.py --tat-ca            kiểm tra mọi template

Báo: loại node lạ, nhà cung cấp không hợp với node, tham số lạ, cổng không tồn tại,
nối sai kiểu (ảnh vào video…), cổng đơn bị nối nhiều dây, vòng lặp, id trùng.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from workflow import registry  # noqa: E402


def check(path: Path) -> list:
    reg = registry()
    types = reg["_by_id"]
    d = json.loads(path.read_text(encoding="utf-8"))
    errs = []
    ids = [n.get("id") for n in d.get("nodes", [])]
    if len(ids) != len(set(ids)):
        errs.append("Trùng id node")
    nodes = {n["id"]: n for n in d.get("nodes", [])}
    for n in d.get("nodes", []):
        t = types.get(n.get("type"))
        if not t:
            errs.append(f"{n['id']}: loại node lạ «{n.get('type')}»")
            continue
        if n.get("provider") and n["provider"] not in (t.get("nha_cung_cap") or []):
            errs.append(f"{n['id']} ({t['ten']}): nhà cung cấp «{n['provider']}» không dùng được cho node này")
        known = {p["key"] for p in t["tham_so"]}
        for k in (n.get("params") or {}):
            if k not in known:
                errs.append(f"{n['id']} ({t['ten']}): tham số lạ «{k}»")
    count = {}
    for e in d.get("edges", []):
        a, b = nodes.get(e["tu"]["node"]), nodes.get(e["den"]["node"])
        if not a or not b:
            errs.append(f"Dây {e.get('id')}: nối tới node không tồn tại")
            continue
        o = [p for p in types.get(a["type"], {}).get("ra", []) if p["id"] == e["tu"]["cong"]]
        i = [p for p in types.get(b["type"], {}).get("vao", []) if p["id"] == e["den"]["cong"]]
        if not o or not i:
            errs.append(f"Dây {e.get('id')}: cổng không tồn tại ({a['id']}.{e['tu']['cong']} → {b['id']}.{e['den']['cong']})")
            continue
        if not (o[0]["kieu"] == i[0]["kieu"] or "any" in (o[0]["kieu"], i[0]["kieu"])):
            errs.append(f"Dây {e.get('id')}: sai kiểu {o[0]['kieu']} → {i[0]['kieu']} ({a['id']} → {b['id']})")
        key = (b["id"], e["den"]["cong"])
        count[key] = count.get(key, 0) + 1
        if count[key] > 1 and not i[0].get("nhieu"):
            errs.append(f"{b['id']}.{e['den']['cong']}: cổng chỉ nhận một dây nhưng có {count[key]}")
    # vòng lặp
    adj = {}
    for e in d.get("edges", []):
        adj.setdefault(e["tu"]["node"], []).append(e["den"]["node"])
    state = {}

    def dfs(u):
        state[u] = 1
        for v in adj.get(u, []):
            if state.get(v) == 1 or (state.get(v) is None and dfs(v)):
                return True
        state[u] = 2
        return False
    if any(state.get(u) is None and dfs(u) for u in nodes):
        errs.append("Workflow có vòng lặp")
    return errs


def main():
    paths = sorted((ROOT / "thu-vien" / "mau-workflow").glob("*.json")) if "--tat-ca" in sys.argv else [Path(a) for a in sys.argv[1:]]
    if not paths:
        sys.exit(__doc__)
    bad = 0
    for p in paths:
        errs = check(p)
        bad += len(errs)
        print(("OK   " if not errs else "LỖI ") + str(p))
        for e in errs:
            print("   - " + e)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
