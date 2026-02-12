# SIQA Challenge Leaderboard

Welcome to the official leaderboard for the [SIQA Challenge](https://siqa-competition.github.io/)!

👉 **[View Live Leaderboard](https://siqa-competition.github.io/Leaderboard/)**  
*(Updated automatically within minutes of a valid submission)*

---

## 📤 How to Submit Results (For Official Participants)

> ⚠️ This repository is **restricted to registered participants only**.  
> If you're not yet in our organization, please **email us first**.

### Step 1: Get Access
1. Send an email to **[liwenzhe@pjlab.org.cn](mailto:liwenzhe@pjlab.org.cn)** with:
   - Your **team name**
   - All team members’ **GitHub usernames**
   - A brief description of your method (optional)
2. We’ll invite you to the `siqa-competition` GitHub organization.
3. Once accepted, you’ll have **write access to this repository**.

### Step 2: Clone and Prepare
```bash
# Clone the repo (do NOT fork!)
git clone https://github.com/siqa-competition/Leaderboard.git
cd Leaderboard
```
`
### Step 3: Create Your Submission File
Add your result as `submissions/your_team_name.json` as following template:  
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

- Filename must be `submissions/YourTeamName.json` (no spaces/special chars)
- Do not modify any other files (CI will reject your submission)
- Use valid JSON (validate with `python -m json.tool your_file.json`)

### Step 4: Commit and Push

```bash
git add submissions/YourTeamName.json
git commit -m "Add submission: YourTeamName"
git push origin master
```

### Step 5: Wait for Auto-Update

1. Validate your JSON format
2. Check that you only modified submissions/
3. Regenerate the leaderboard
4. Your results will appear on the site within 5 minutes.
