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


def escape_html(text):
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))


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
            "team": escape_html(team),
            "method": escape_html(scores["method"] or "–"),
            "U": u_score,
            "S": s_score,
            "Combined": round(combined, 2)
        })
    overall_list.sort(key=lambda x: x["Combined"], reverse=True)

    u_teams = [
        {"team": escape_html(team), "method": escape_html(data["method"] or "–"), **data["U"]}
        for team, data in teams.items() if data["U"]
    ]
    u_teams.sort(key=lambda x: x["score"], reverse=True)

    s_teams = [
        {"team": escape_html(team), "method": escape_html(data["method"] or "–"), **data["S"]}
        for team, data in teams.items() if data["S"]
    ]
    s_teams.sort(key=lambda x: x["score"], reverse=True)

    # --- CSS 样式（与你提供的完全一致）---
    css = '''
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #24292e;
      background-color: #ffffff;
      max-width: 1000px;
      margin: 0 auto;
      padding: 30px 15px;
    }

    h1, h2 {
      margin-top: 1.2em;
      margin-bottom: 0.8em;
      font-weight: 600;
      color: #24292e;
      border-bottom: 1px solid #eaecef;
      padding-bottom: 0.3em;
    }

    h1 {
      font-size: 2em;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    blockquote {
      margin: 1.2em 0;
      padding: 0 1em;
      color: #6a737d;
      border-left: 0.25em solid #dfe2e5;
      font-style: italic;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 1.4em 0;
      display: block;
      overflow-x: auto;
      background-color: white;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    th, td {
      padding: 10px 12px;
      text-align: left;
      border: 1px solid #d0d7de;
    }

    th {
      background-color: #f6f8fa;
      font-weight: 600;
      text-align: center;
    }

    @media (max-width: 600px) {
      body {
        padding: 15px 8px;
      }
      h1 {
        font-size: 1.6em;
      }
      table {
        font-size: 0.9em;
      }
    }

    footer {
      margin-top: 2em;
      color: #6a737d;
      font-size: 0.95em;
    }
    '''

    # --- 构建 HTML ---
    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>',
        '  <title>SIQA Leaderboard</title>',
        '  <style>',
        css,
        '  </style>',
        '</head>',
        '<body>',
        '',
        '  <h1>🏆 SIQA Competition Leaderboard</h1>',
        '',
        '  <blockquote>',
        '    <p><strong>SIQA-U Weighting</strong>: Yes/No (20%), What (30%), How (50%)<br />',
        '    <strong>SIQA-S Score</strong>: Average of Perception and Knowledge (each: mean of SRCC &amp; PLCC)</p>',
        '  </blockquote>',
        ''
    ]

    # === Overall ===
    html_lines.extend([
        '  <h2>🥇 Overall Ranking (Average of U and S)</h2>',
        '  <table>',
        '    <thead>',
        '      <tr><th>Rank</th><th>Team</th><th>Method</th><th>SIQA-U</th><th>SIQA-S</th><th>Combined</th></tr>',
        '    </thead>',
        '    <tbody>'
    ])
    for i, e in enumerate(overall_list, 1):
        u_str = f"{e['U']:.2f}" if e['U'] > 0 else "–"
        s_str = f"{e['S']:.2f}" if e['S'] > 0 else "–"
        comb_str = f"{e['Combined']:.2f}" if e['Combined'] > 0 else "–"
        html_lines.append(f'      <tr><td>{i}</td><td>{e["team"]}</td><td>{e["method"]}</td><td>{u_str}</td><td>{s_str}</td><td>{comb_str}</td></tr>')
    html_lines.extend([
        '    </tbody>',
        '  </table>',
        ''
    ])

    # === SIQA-U ===
    html_lines.extend([
        '  <h2>🧠 SIQA-U Leaderboard (Understanding)</h2>',
        '  <table>',
        '    <thead>',
        '      <tr><th>Rank</th><th>Team</th><th>Method</th><th>Yes/No ACC</th><th>What ACC</th><th>How ACC</th><th>Final Score</th></tr>',
        '    </thead>',
        '    <tbody>'
    ])
    for i, e in enumerate(u_teams, 1):
        html_lines.append(
            f'      <tr><td>{i}</td><td>{e["team"]}</td><td>{e["method"]}</td>'
            f'<td>{e["acc_yes/no"]:.2f}</td><td>{e["acc_what"]:.2f}</td><td>{e["acc_how"]:.2f}</td>'
            f'<td>{e["score"]:.2f}</td></tr>'
        )
    html_lines.extend([
        '    </tbody>',
        '  </table>',
        ''
    ])

    # === SIQA-S ===
    html_lines.extend([
        '  <h2>📊 SIQA-S Leaderboard (Scoring)</h2>',
        '  <table>',
        '    <thead>',
        '      <tr><th>Rank</th><th>Team</th><th>Method</th><th>Perception (SRCC / PLCC)</th><th>Knowledge (SRCC / PLCC)</th><th>Final Score</th></tr>',
        '    </thead>',
        '    <tbody>'
    ])
    for i, e in enumerate(s_teams, 1):
        perc = f"{e['srcc_p']:.4f} / {e['plcc_p']:.4f}"
        know = f"{e['srcc_k']:.4f} / {e['plcc_k']:.4f}"
        html_lines.append(f'      <tr><td>{i}</td><td>{e["team"]}</td><td>{e["method"]}</td><td>{perc}</td><td>{know}</td><td>{e["score"]:.2f}</td></tr>')
    html_lines.extend([
        '    </tbody>',
        '  </table>',
        '',
        f'  <blockquote>',
        f'    <p>🕒 Last updated: {timestamp}</p>',
        f'  </blockquote>',
        '',
        '  <footer>',
        '    Built with ❤️ for the SIQA Challenge',
        '  </footer>',
        '</body>',
        '</html>'
    ])

    # 写入 index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    print("✅ Leaderboard generated: index.html")


if __name__ == "__main__":
    main()