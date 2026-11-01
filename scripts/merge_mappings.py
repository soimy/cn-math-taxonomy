#!/usr/bin/env python3
"""把 data/mappings/*.json 的对照条目合并进 data/topics.json 的 topic.mappings。

对照表是「按版本整理」的贡献文件，运行时只读 topics.json（PWA 预缓存、离线可用），
所以发布前跑一次本脚本。全量重建：先清掉所有 mappings，再按当前对照文件写回，
可以反复运行。合并完记得跑 python3 scripts/validate.py。

用法：python3 scripts/merge_mappings.py [--check]
  --check  只报告会改动多少条，不写文件（有差异时退出码 1）。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS = os.path.join(ROOT, "data", "topics.json")
MAPPINGS_DIR = os.path.join(ROOT, "data", "mappings")
# mappings 插在 standards 后面，保持字段顺序、diff 只有新增行
AFTER = "standards"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_index():
    """topicId -> {edition: 条目}；示例文件（status=example）不参与合并。"""
    index, files = {}, []
    if not os.path.isdir(MAPPINGS_DIR):
        return index, files
    for fn in sorted(os.listdir(MAPPINGS_DIR)):
        if not fn.endswith(".json"):
            continue
        data = load(os.path.join(MAPPINGS_DIR, fn))
        if data.get("status") == "example":
            continue
        edition = data.get("edition")
        for e in data.get("entries") or []:
            tid = e.get("topicId")
            if not tid:
                continue
            entry = {k: v for k, v in e.items() if k != "topicId"}
            index.setdefault(tid, {})[edition] = entry
        files.append("%s(%d)" % (edition, len(data.get("entries") or [])))
    return index, files


def rewrite(topic, maps):
    out = {}
    for k, v in topic.items():
        if k == "mappings":
            continue
        out[k] = v
        if k == AFTER and maps:
            out["mappings"] = maps
    if maps and "mappings" not in out:
        out["mappings"] = maps
    return out


def main():
    check = "--check" in sys.argv[1:]
    index, files = build_index()
    topics = load(TOPICS)
    changed = 0
    out = []
    for t in topics:
        maps = index.get(t.get("id"))
        new = rewrite(t, maps)
        if new != t:
            changed += 1
        out.append(new)
    unknown = sorted(set(index) - {t.get("id") for t in topics})
    print("对照表：%s" % ("、".join(files) if files else "无"))
    print("知识点：%d 个带对照（本次改动 %d 个）" % (len(index), changed))
    if unknown:
        print("跳过不存在的 topicId（%d 个）：%s" % (len(unknown), "、".join(unknown[:10])))
    if check:
        return 1 if changed else 0
    with open(TOPICS, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("已写入 data/topics.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
