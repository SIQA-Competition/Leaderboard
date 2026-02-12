import json
import glob
import os
from datetime import datetime
from collections import defaultdict
from scipy.stats import spearmanr, pearsonr
import numpy as np

ANSWERS_DIR = "answer"
SUBMISSIONS_DIR = "submissions"
U_GT_PATH = os.path.join(ANSWERS_DIR, "answer-u.json")
S_GT_PATH = os.path.join(ANSWERS_DIR, "answer-s.json")


def load_ground_truth():
    gt = {}
    with open(U_GT_PATH, 'r', encoding='utf-8') as f:
        u_list = json.load(f)["predictions"]
        gt['U'] = {item['id']: item for item in u_list}
    with open(S_GT_PATH, 'r', encoding='utf-8') as f:
        s_list = json.load(f)["predictions"]
        gt['S'] = {item['id']: item for item in s_list}
    return gt


def evaluate_u(preds, gt_dict):
    correct = {"yes-or-no": 0, "what": 0, "how": 0}
    total = {"yes-or-no": 0, "what": 0, "how": 0}
    for p in preds:
        q_id = p.get("id")
        if q_id not in gt_dict:
            continue
        gt = gt_dict[q_id]
        q_type = gt["type"]
        if q_type not in total:
            continue
        gt_ans = str(gt["precision"]).strip().upper()
        pred_ans = str(p.get("precision", "")).strip().upper()
        total[q_type] += 1
        if gt_ans == pred_ans:
            correct[q_type] += 1

    acc = {t: correct[t] / total[t] if total[t] > 0 else 0.0 for t in total}
    score = 0.2 * acc["yes-or-no"] + 0.3 * acc["what"] + 0.5 * acc["how"]

    return {
        "score": round(score * 100, 2),
        "acc_yes/no": round(acc["yes-or-no"] * 100, 2),
        "acc_what": round(acc["what"] * 100, 2),
        "acc_how": round(acc["how"] * 100, 2),
    }


def evaluate_s(preds, gt_dict):
    gt_p, pred_p = [], []
    gt_k, pred_k = [], []
    for p in preds:
        q_id = p.get("id")
        if q_id not in gt_dict:
            continue
        gt_item = gt_dict[q_id]
        p_pred = p.get("perception")
        k_pred = p.get("knowledge")
        if None in [gt_item.get("perception"), gt_item.get("knowledge"), p_pred, k_pred]:
            continue
        try:
            gt_p.append(float(gt_item["perception"]))
            pred_p.append(float(p_pred))
            gt_k.append(float(gt_item["knowledge"]))
            pred_k.append(float(k_pred))
        except (TypeError, ValueError):
            continue

    if len(gt_p) == 0:
        return {
            "score": 0.0,
            "srcc_p": 0.0, "plcc_p": 0.0,
            "srcc_k": 0.0, "plcc_k": 0.0,
        }

    def safe_corr(x, y):
        if len(set(x)) == 1 or len(set(y)) == 1:
            return 0.0
        srcc, _ = spearmanr(x, y)
        plcc, _ = pearsonr(x, y)
        srcc = srcc if not np.isnan(srcc) else 0.0
        plcc = plcc if not np.isnan(plcc) else 0.0
        return max(srcc, 0.0), max(plcc, 0.0)

    srcc_p, plcc_p = safe_corr(gt_p, pred_p)
    srcc_k, plcc_k = safe_corr(gt_k, pred_k)

    score_p = (srcc_p + plcc_p) / 2 * 100
    score_k = (srcc_k + plcc_k) / 2 * 100
    final_score = (score_p + score_k) / 2

    return {
        "score": round(final_score, 2),
        "srcc_p": round(srcc_p, 4),
        "plcc_p": round(plcc_p, 4),
        "srcc_k": round(srcc_k, 4),
        "plcc_k": round(plcc_k, 4),
    }


def main():
    gt = load_ground_truth()
    teams = defaultdict(lambda: {
        "U": None,
        "S": None,
        "method": ""
    })

    for file_path in sorted(glob.glob(os.path.join(SUBMISSIONS_DIR, "*.json"))):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not all(k in data for k in ["team", "track", "predictions"]):
                print(f"⚠️ 跳过 {file_path}: 缺少必要字段")
                continue
            team = data["team"].strip()
            track = data["track"].upper()
            method = data.get("method", "").strip()
            preds = data["predictions"]
            if track == "U":
                result = evaluate_u(preds, gt["U"])
                teams[team]["U"] = result
                if method:
                    teams[team]["method"] = method
            elif track == "S":
                result = evaluate_s(preds, gt["S"])
                teams[team]["S"] = result
                if method:
                    teams[team]["method"] = method
            else:
                print(f"⚠️ 未知 track: {track}")
        except Exception as e:
            print(f"❌ 处理失败 {file_path}: {e}")

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # --- 计算 Overall 排名 ---
    overall_list = []
    for team, scores in teams.items():
        u_score = scores["U"]["score"] if scores["U"] else 0.0
        s_score = scores["S"]["score"] if scores["S"] else 0.0
        combined = (u_score + s_score) / 2 if (u_score > 0 or s_score > 0) else 0.0
        overall_list.append({
            "team": team,
            "method": scores["method"] or "-",
            "U": u_score,
            "S": s_score,
            "Combined": round(combined, 2)
        })
    overall_list.sort(key=lambda x: x["Combined"], reverse=True)

    # --- 提取 U 和 S 榜单 ---
    u_teams = [
        {"team": team, "method": data["method"] or "-", **data["U"]}
        for team, data in teams.items() if data["U"]
    ]
    u_teams.sort(key=lambda x: x["score"], reverse=True)

    s_teams = [
        {"team": team, "method": data["method"] or "-", **data["S"]}
        for team, data in teams.items() if data["S"]
    ]
    s_teams.sort(key=lambda x: x["score"], reverse=True)

    # --- 生成单一页面 Markdown ---
    md_lines = [
        "---",
        "layout: leaderboard",
        "title: SIQA Leaderboard",
        "permalink: /",
        "---",
        "",
        "# 🏆 SIQA Competition Leaderboard",
        "",
        "> **SIQA-U Weighting**: Yes/No (20%), What (30%), How (50%)  \n"
        "> **SIQA-S Score**: Average of Perception and Knowledge (each: mean of SRCC & PLCC)",
        "",
    ]

    # === Overall ===
    md_lines.extend([
        "## 🥇 Overall Ranking (Average of U and S)",
        "| Rank | Team | Method | SIQA-U | SIQA-S | Combined |",
        "|:----:|:-----|:-------|:------:|:------:|:--------:|"
    ])
    for i, e in enumerate(overall_list, 1):
        u_str = f"{e['U']:.2f}" if e['U'] > 0 else "-"
        s_str = f"{e['S']:.2f}" if e['S'] > 0 else "-"
        comb_str = f"{e['Combined']:.2f}" if e['Combined'] > 0 else "-"
        md_lines.append(f"| {i} | {e['team']} | {e['method']} | {u_str} | {s_str} | {comb_str} |")
    md_lines.append("")

    # === SIQA-U ===
    md_lines.extend([
        "## 💡 SIQA-U Leaderboard (Understanding)",
        "| Rank | Team | Method | Yes/No ACC | What ACC | How ACC | Final Score |",
        "|:----:|:-----|:-------|:----------:|:--------:|:-------:|:-----------:|"
    ])
    for i, e in enumerate(u_teams, 1):
        md_lines.append(
            f"| {i} | {e['team']} | {e['method']} | "
            f"{e['acc_yes/no']:.2f} | {e['acc_what']:.2f} | {e['acc_how']:.2f} | "
            f"{e['score']:.2f} |"
        )
    md_lines.append("")

    # === SIQA-S ===
    md_lines.extend([
        "## 📈 SIQA-S Leaderboard (Scoring)",
        "| Rank | Team | Method | Perception (SRCC / PLCC) | Knowledge (SRCC / PLCC) | Final Score |",
        "|:----:|:-----|:-------|:------------------------:|:-----------------------:|:-----------:|"
    ])
    for i, e in enumerate(s_teams, 1):
        perc = f"{e['srcc_p']:.4f} / {e['plcc_p']:.4f}"
        know = f"{e['srcc_k']:.4f} / {e['plcc_k']:.4f}"
        md_lines.append(f"| {i} | {e['team']} | {e['method']} | {perc} | {know} | {e['score']:.2f} |")
    md_lines.append("")

    md_lines.append(f"> 🕒 Last updated: {timestamp}")

    # 写入 index.md
    with open("index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("✅ Leaderboard generated: index.md")


if __name__ == "__main__":
    main()