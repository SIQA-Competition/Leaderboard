# SIQA Challenge Leaderboard

Welcome to the official website for the [SIQA Challenge](https://siqa-competition.github.io/)!

👉 [View Full Leaderboard](https://siqa-competition.github.io/Leaderboard/)

## 📤 How to Submit
1. Fork this repo
2. Add your result as `submissions/your_team_name.json` as following template:  
For **SIQA-S** track,
```json
{
  "team": "TeamName",
  "method": "ModelName",
  "track": "S",
  "predictions": [
    {
      "id": 1,
      "perception": 2.1192,
      "knowledge": 1.5401
    },
    "...",
    {
      "id": 1050,
      "perception": 4.2227,
      "knowledge": 4.18
    }
  ]
}
```
For **SIQA-U** track,
```json
{
  "team": "TeamName",
  "method": "ModelName",
  "track": "U",
  "predictions": [
    {
      "id": 1,
      "type": "what",
      "precision": "A"
    },
    "...",
    {
      "id": 1120,
      "type": "what",
      "precision": "D"
    }
  ]
}
```
3. Open a Pull Request to `master`
4. Your result will appear on the leaderboard within minutes!
