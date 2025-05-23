# Fantasy Football Luck Analyzer

The **Fantasy Football Luck Analyzer** is a web-based tool built with Streamlit that helps you analyze how "lucky" or "unlucky" you've been in your ESPN Fantasy Football league. By leveraging advanced metrics and visualizations, this app provides insights into how factors like opponent performance, scheduling, and scoring expectations have influenced your team's success.

---

## Features

### 1. Opponent Underperformance
- Visualizes how much your opponents underperformed or overperformed compared to their projected scores.
- Positive values indicate opponents scored less than expected, while negative values indicate they scored more than expected.
- **Example**: If your opponent was projected to score 100 points but only scored 80, your luck index is +20.

### 2. Pythagorean Expectation
- Compares your actual wins to your expected wins based on the Pythagorean Expectation formula.
- Teams with a positive Luck Index have won more games than expected.
- Teams with a negative Luck Index have won fewer games than expected.

### 3. Scatterplot Luck
- A scatterplot visualizing your team's performance relative to the league average.
  - **X-axis**: Points scored (relative to league average)
  - **Y-axis**: Points allowed (relative to league average)
  - Blue dots represent wins, red dots represent losses
  - Highlights "Lucky Wins" and "Unlucky Losses" regions

### 4. Scheduling Luck
- A table showing how each team would have performed if they had played every other team's schedule.
- Helps you understand how much your record was influenced by your schedule rather than your team's strength.

---

## Access the App

You can access the app at the following URL: https://fantasyfootball-luck-analyzer.streamlit.app/.

**NOTE: First load may take a few seconds — app spins up on demand.**

---

## Usage

1. **Log In:**
   - Enter your **League ID**, **SWID**, and **ESPN_S2** credentials in the login form.
   - Follow the instructions in the app to locate your `SWID` and `ESPN_S2` tokens from your browser cookies for `espn.com`.

2. **Explore Visualizations:**
   - Use the buttons on the main page to view different metrics:
     - **Opponent Underperformance**: See how your opponents performed compared to their projections.
     - **Pythagorean Expectation**: Compare your actual wins to your expected wins.
     - **Scatterplot Luck**: Visualize your team's performance relative to the league average.
     - **Scheduling Luck**: Analyze how your record might have changed with a different schedule.

3. **Analyze Your Luck:**
   - Use the visualizations and tables to gain insights into how luck has influenced your fantasy football season.

---

## Screenshots

Opponent Underperformance
<div style="text-align: left;">
    <img src="readme_assets/opp_underperformance.png" alt="Opponent Underperformance" width="600">
    <p><em>Bar chart of opponent underperformance luck.</em></p>
</div>

Scatterplot
<div style="text-align: left;">
    <img src="readme_assets/scatterplot_readme.png" alt="Scatterplot Luck" width="600">
    <p><em>Scatterplot of all teams in an example league.</em></p>
</div>

Pythagorean Expectation
<div style="text-align: left;">
    <img src="readme_assets/pythagorean_expectation.png" alt="Pythagorean Expectation" width="600">
    <p><em>Chart comparing actual wins to expected wins based on the Pythagorean Expectation formula.</em></p>
</div>

Scheduling
<div style="text-align: left;">
    <img src="readme_assets/scheduling_readme.png" alt="Scheduling Luck" width="600">
    <p><em>Table showing how each (row) team's record would change with all other teams' (columns) respective schedule.</em></p>
</div>

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for bug fixes, new features, or enhancements.

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

- Built with the assistance of the [espn-api](https://github.com/cwendt94/espn-api) library.
- Inspired by the pain of losing to the highest scorer every week 😭 (or so it seems!).