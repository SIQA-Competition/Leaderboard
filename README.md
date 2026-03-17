# SIQA Challenge Leaderboard

Welcome to the official leaderboard for the [SIQA Challenge](https://siqa-competition.github.io/)!

👉 **[View Live Leaderboard](https://siqa-competition.github.io/Leaderboard/)**  
*(Updated automatically within minutes of a valid submission)*

---

## 📤 How to Submit Results (For Official Participants)

> ⚠️ This repository is **restricted to registered participants only**.  
> If you're not yet in our organization, please **email us first**.

Here is the updated `README.md` content, incorporating your new submission guidelines, evaluation schedule (every Wednesday), and fairness policies while maintaining the original structure and tone.

```markdown
# SIQA Challenge Leaderboard

Welcome to the official leaderboard for the [SIQA Challenge](https://siqa-competition.github.io/)!

👉 **[View Live Leaderboard](https://siqa-competition.github.io/Leaderboard/)**  
*(Updated weekly based on committee evaluation)*

---

## 📤 Submission Guidelines

To ensure a **fair evaluation process** and prevent data leakage, the testing phase is now conducted **centrally by the organizing committee**. Direct push access to the repository has been disabled. Please follow these steps to submit your results:

### Step 1: Format Your Output
Generate predictions for the `test.jsonl` file. Your output file must strictly adhere to the official format specification.

📄 **Format Reference & Examples:** [GitHub Repository](https://github.com/SIQA-Competition/Leaderboard)  
*(Note: Submissions that do not match the required JSON/JSONL structure may be rejected.)*

**Example Format (SIQA-S):**
```json
{
  "team": "TeamName",
  "method": "ModelName",
  "track": "S",
  "predictions": [
    { "id": 1, "perception": 2.1192, "knowledge": 1.5401 },
    "...",
    { "id": 1050, "perception": 4.2227, "knowledge": 4.18 }
  ]
}
```

**Example Format (SIQA-U):**
```json
{
  "team": "TeamName",
  "method": "ModelName",
  "track": "U",
  "predictions": [
    { "id": 1, "type": "what", "precision": "A" },
    "...",
    { "id": 1120, "type": "what", "precision": "D" }
  ]
}
```

### Step 2: Send via Email
Once your prediction file is ready, please email it directly to the committee.

*   **Recipient:** [liwenzhe@pjlab.org.cn](mailto:liwenzhe@pjlab.org.cn)
*   **Email Subject Line:** `[SIQA Submission] <Team_Name> - <Model_Name>`
*   **Email Body:** Please briefly include your team name, a short model description, and any specific remarks regarding your submission.

---

## 🏆 Evaluation & Leaderboard Updates

*   **Processing:** Upon receipt, our team will run your predictions against the hidden ground truth labels locally.
*   **Updates:** The calculated metrics will be updated on the official Leaderboard for public viewing.
*   **Frequency:** We perform evaluations **every Wednesday**. All submissions received during the week will be processed on this day, and the leaderboard will be updated shortly thereafter.

---

## ⚠️ Important Rules

1.  **Submission Limits:** Each team is allowed a maximum of **2 submissions per week**.
2.  **Data Integrity:** Do not attempt to infer or recover the hidden labels for the test set using external resources. Violation of this rule will result in immediate disqualification.
3.  **Fairness:** To protect intellectual property, your raw submission files are **not** made public. Only the final scores appear on the leaderboard.
4.  **Deadline:** The final deadline for submissions is **April 25th**.

---

We look forward to seeing your innovative solutions and high-performing models. If you encounter any issues with data access or formatting, please reply to our email or open an issue on this GitHub repository.

**Best of luck in the competition!**

Sincerely,  
**The SIQA Competition Organizing Committee**
```
