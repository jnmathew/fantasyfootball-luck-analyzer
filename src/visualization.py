from matplotlib import cm
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import csv

from analysis import get_luck_index, get_luck_index_2, simulate_hypothetical_records

def load_data(filename):
    """
    Load the luck index data from a CSV file.
    """
    try:
        data = pd.read_csv(filename)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

def plot_luck_indices(luck_indices, output_file=None):
    """
    Plot the luck indices of Fantasy Football teams.

    Parameters:
    - luck_indices (pd.DataFrame): DataFrame containing team names and luck indices.
    - output_file (str): Optional. Filepath to save the plot.
    """
    
    # Sort data by Luck Index
    luck_indices = luck_indices.sort_values("Luck Index")

    # Create a bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        luck_indices["Team Name"], 
        luck_indices["Luck Index"], 
        color=["green" if x > 0 else "red" for x in luck_indices["Luck Index"]]
    )
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Line at Luck Index = 0

    # Annotate bars with luck index values
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval + (1 if yval > 0 else -1),  # Offset above or below the bar
            round(yval, 2),
            ha='center',
            va='bottom' if yval > 0 else 'top',
            fontsize=10
        )

    # Add titles and labels
    plt.title("Fantasy Football Luck Index by Team", fontsize=16)
    plt.xlabel("Team Name", fontsize=12)
    plt.ylabel("Luck Index", fontsize=12)
    plt.xticks(rotation=45, ha="right")  # Rotate team names for readability
    plt.tight_layout()

    # Save to file if specified
    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Chart saved to {output_file}")
    else:
        plt.show()

    return plt


def generate_luck_index_chart_sorted(league, luck_indices, output_file=None):
    """
    Generate a bar chart for Luck Index directly from the league API, handling missing team IDs dynamically,
    and sorting teams from worst luck to best luck.

    Parameters:
    - league: The league object (e.g., from the ESPN API).
    - luck_indices: List of corresponding luck index values (from get_luck_index_2).
    - output_file: Optional file path to save the chart as an image.
    """
    # Fetch valid teams and their IDs from the league
    teams = [(team.team_id, team.team_name) for team in league.teams]

    # Dynamically filter the luck indices to match the valid team IDs
    filtered_luck_data = []

    for team_id, team_name in teams:
        # Dynamically get the luck index for the valid team_id
        if 0 <= team_id - 1 < len(luck_indices):  # Ensure no out-of-bounds indexing
            filtered_luck_data.append((team_name, luck_indices[team_id - 1]))

    # Sort teams by Luck Index (ascending: worst luck to best luck)
    filtered_luck_data.sort(key=lambda x: x[1])  # Sort by the Luck Index value (second element in tuple)

    # Separate sorted team names and luck indices
    sorted_team_names = [item[0] for item in filtered_luck_data]
    sorted_luck_indices = [item[1] for item in filtered_luck_data]

    # Debugging: Print sorted data
    print(f"Sorted Team Names: {sorted_team_names}")
    print(f"Sorted Luck Indices: {sorted_luck_indices}")

    # Create the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(sorted_team_names, sorted_luck_indices, color=["green" if x > 0 else "red" for x in sorted_luck_indices])
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add a line at 0 for reference
    plt.title("Luck Index by Team (Sorted)", fontsize=16)
    plt.xlabel("Team Name", fontsize=12)
    plt.ylabel("Luck Index (Opponent Underperformance)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Annotate bars with their values
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + (0.2 if yval > 0 else -0.2),
                 f"{yval:.2f}", ha="center", va="bottom" if yval > 0 else "top", fontsize=10)

    # Save the chart to a file if specified
    if output_file:
        plt.savefig(output_file)
        print(f"Chart saved to {output_file}")

    # Show the plot
    plt.show()

def save_and_visualize_pythagorean_luck(pythagorean_luck_data, output_file="out/pythagorean_luck.csv", image_file="out/pythagorean_luck_chart.png"):
    """
    Save and visualize Pythagorean Expectation Luck for all teams, sorted by Luck Index from least lucky to most lucky.

    Parameters:
    - pythagorean_luck_data: List of dictionaries with Pythagorean Luck data.
    - output_file: The file where results will be saved (default="pythagorean_luck.csv").
    - image_file: The file where the visualization will be saved (default="pythagorean_luck_chart.png").
    """

    # Sort by Luck Index (ascending: least lucky to most lucky)
    pythagorean_luck_data_sorted = sorted(pythagorean_luck_data, key=lambda x: x["Luck Index"])

    # Save results to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Actual Wins", "Expected Wins", "Luck Index"])
        writer.writeheader()
        writer.writerows(pythagorean_luck_data_sorted)

    print(f"Pythagorean Expectation Luck saved to {output_file}!")

    # Visualization
    team_names = [t["Team Name"] for t in pythagorean_luck_data_sorted]
    luck_scores = [t["Luck Index"] for t in pythagorean_luck_data_sorted]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(team_names, luck_scores, color=["red" if x < 0 else "green" for x in luck_scores])
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.title("Pythagorean Expectation Luck by Team (Sorted)", fontsize=16)
    plt.xlabel("Team Name", fontsize=12)
    plt.ylabel("Luck Index (Actual Wins - Expected Wins)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Annotate bars with luck scores
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + (0.2 if yval > 0 else -0.2),
                 f"{yval:.2f}", ha="center", va="bottom" if yval > 0 else "top", fontsize=10)

    # Save the plot to a file
    plt.savefig(image_file, dpi=300)
    print(f"Pythagorean Expectation Luck visualization saved to {image_file}!")

    # Show the plot
    plt.show()


def save_luck_indices_to_file(league, output_file="luck_indices.csv"):
    """
    Calculate and save the luck indices of all teams to a file.
    """
    # Initialize a list to store team luck index data
    team_luck_data = []

    teams = league.teams

    # Iterate over all teams in the league
    for team in teams:
        team_id = team.team_id
        team_name = team.team_name

        # Calculate the team's luck index
        luck_index = get_luck_index(league, team_id)
        print(f"Team: {team_name}, Luck Index: {luck_index}")

        # Add the result to the list
        team_luck_data.append({
            "Team Name": team_name,
            "Team ID": team_id,
            "Luck Index": luck_index
        })

    # Save results to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Luck Index"])
        writer.writeheader()
        writer.writerows(team_luck_data)

    print(f"Luck indices saved to {output_file}!")



def save_luck_indices_to_file_2(league, output_file="luck_indices_2.csv"):
    """
    Calculate and save the luck indices of all teams to a file using the optimized `get_luck_index_2`.
    """
    # Initialize a list to store team luck index data
    team_luck_data = []

    # Calculate the luck indices for all teams using the optimized approach
    luck_indices = get_luck_index_2(league)

    # Iterate over all teams in the league to match luck indices to team names
    for team in league.teams:
        team_id = team.team_id
        team_name = team.team_name

        # Get the corresponding luck index for this team
        luck_index = luck_indices[team_id - 1]  # Adjust for 0-based indexing
        print(f"Team: {team_name}, Luck Index: {luck_index}")

        # Add the result to the list
        team_luck_data.append({
            "Team Name": team_name,
            "Team ID": team_id,
            "Luck Index": luck_index
        })

    # Save results to a CSV file
    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Team Name", "Team ID", "Luck Index"])
        writer.writeheader()
        writer.writerows(team_luck_data)

    print(f"Luck indices saved to {output_file}!")


def save_luck_indices_to_file_3(league_data, luck_indices, output_file=None):
    """
    Save the luck indices of all teams to a file using the provided luck indices list.
    If output_file is None, return a DataFrame instead.
    """
    # Initialize a list to store team luck index data
    team_luck_data = []

    # Iterate over the teams and their corresponding luck indices
    for team in league_data['teams']:
        team_id = team['id']
        team_name = team['name']

        # Ensure the team_id matches the index in luck_indices
        if 0 <= team_id < len(luck_indices):
            luck_index = luck_indices[team_id]
            print(f"Team: {team_name}, Luck Index: {luck_index}")

            # Add the result to the list
            team_luck_data.append({
                "Team Name": team_name,
                "Team ID": team_id,
                "Luck Index": luck_index
            })

    # Convert the list to a DataFrame
    df = pd.DataFrame(team_luck_data)

    # Save results to a CSV file if specified
    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Luck indices saved to {output_file}!")
    
    return df


def create_scheduling_luck_dataframe(league_data):
    hypothetical_records = simulate_hypothetical_records(league_data)

    teams = [team['name'] for team in league_data['teams']]
    df = pd.DataFrame(index=teams, columns=teams)

    for team in league_data['teams']:
        team_id = team['id']
        team_name = team['name']

        for opponent_team in league_data['teams']:
            opponent_id = opponent_team['id']
            opponent_name = opponent_team['name']

            record = hypothetical_records[team_id][opponent_id]
            df.at[team_name, opponent_name] = f"{record['wins']}-{record['losses']}"

    return df


def create_scatterplot_luck_figure(df, selected_team=None):
    """
    Create a Plotly scatterplot for matchup luck visualization.
    
    Parameters:
    - df (pd.DataFrame): DataFrame with columns:
        - "Points For" (relative to league average)
        - "Points Against" (relative to league average)
        - "Result" ("Win" or "Loss")
        - "Week" (week number)
        - "Opponent" (opponent team name)
    - selected_team (str): Optional. The name of the team to filter the scatter plot.
    
    Returns:
    - fig: A Plotly figure object ready for Streamlit.
    """
    # Add color column for visualization
    df["Color"] = df["Result"].apply(lambda x: "blue" if x == "Win" else "red")
    
    # Filter by selected team if provided
    if selected_team:
        df = df[df["Team Name"] == selected_team]

    # Create the figure
    fig = go.Figure()

    # Add scatter points
    for i, row in df.iterrows():
        # Conditional text based on coordinates
        if row["Points For"] > 0:
            pf_cond = "pts over avg"
        else:
            pf_cond = "pts under avg"
        if row["Points Against"] > 0:
            pa_cond = "pts over avg"
        else:
            pa_cond = "pts under avg"

        fig.add_trace(go.Scatter(
            x=[row["Points For"]],
            y=[row["Points Against"]],
            mode="markers",
            marker=dict(
                color=row["Color"],
                size=12
            ),
            name=row["Result"],
            hovertemplate=(
                f"Week {row['Week']} vs. {row['Opponent']}<br>"
                f"Team: {abs(round(row['Points For'], 2))} {pf_cond}<br>"
                f"Opponent: {abs(round(row['Points Against'], 2))} {pa_cond}<br>"
            )
        ))

    # Add diagonal reference line (y = x)
    fig.add_trace(go.Scatter(
        x=[-100, 100],
        y=[-100, 100],
        mode="lines",
        line=dict(color="white", dash="dot"),
        name="Reference Line"
    ))

    # Highlight "Lucky Win" and "Unlucky Loss" regions
    fig.add_shape(
        type="path",
        path="M 0 0 L 100 0 L 100 100 Z",
        fillcolor="blue", opacity=0.15, line_width=0,
        name="Lucky Win Region"
    )
    fig.add_shape(
        type="path",
        path="M 0 0 L 0 100 L 100 100 Z",
        fillcolor="red", opacity=0.15, line_width=0,
        name="Unlucky Loss Region"
    )
    fig.add_shape(
        type="path",
        path="M 0 0 L -100 0 L -100 -100 Z",
        fillcolor="blue", opacity=0.15, line_width=0,
        name="Lucky Win Region"
    )
    fig.add_shape(
        type="path",
        path="M 0 0 L 0 -100 L -100 -100 Z",
        fillcolor="red", opacity=0.15, line_width=0,
        name="Unlucky Loss Region"
    )

    # Add annotations for the regions
    fig.add_annotation(
        x=85, y=45,
        text="Lucky Win",
        showarrow=False,
        font=dict(family="Trebuchet MS", size=20, color="blue", variant="small-caps"),
        align="center"
    )
    fig.add_annotation(
        x=50, y=90,
        text="Unlucky Loss",
        showarrow=False,
        font=dict(family="Trebuchet MS", size=20, color="red", variant="small-caps"),
        align="center"
    )
    fig.add_annotation(
        x=-85, y=-45,
        text="Lucky Win",
        showarrow=False,
        font=dict(family="Trebuchet MS", size=20, color="blue", variant="small-caps"),
        align="center"
    )
    fig.add_annotation(
        x=-50, y=-90,
        text="Unlucky Loss",
        showarrow=False,
        font=dict(family="Trebuchet MS", size=20, color="red", variant="small-caps"),
        align="center"
    )

    # Update layout
    fig.update_layout(
        title="Points For vs. Points Against (Relative to League Average)",
        xaxis_title="Points For (Relative to League Average)",
        yaxis_title="Points Against (Relative to League Average)",
        template="plotly_white",
        xaxis=dict(
            range=[-100, 100],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            showline=True,
            linewidth=2,
            linecolor='black'
        ),
        yaxis=dict(
            range=[-100, 100],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            showline=True,
            linewidth=2,
            linecolor='black'
        ),
        showlegend=False  # Hide the legend
    )
    
    return fig

def plot_pythagorean_expectation_luck(pythagorean_luck_data):
    """
    Plot Pythagorean Expectation Luck for all teams.

    Parameters:
    - pythagorean_luck_data: List of dictionaries with Team Name, Actual Wins, Expected Wins, and Luck Index.

    Returns:
    - fig: A Matplotlib figure object.
    """
    # Sort teams by luck index (best luck on top)
    pythagorean_luck_data.sort(key=lambda x: x['Luck Index'], reverse=True)
    fig, ax = plt.subplots()
    teams = [team['Team Name'] for team in pythagorean_luck_data]
    luck_index = [team['Luck Index'] for team in pythagorean_luck_data]

    # Create a color gradient
    norm = plt.Normalize(min(luck_index), max(luck_index))
    colors = cm.RdYlGn(norm(luck_index))

    bars = ax.barh(teams, luck_index, color=colors)

    # Add labels inside the bars
    for bar, value in zip(bars, luck_index):
        ax.text(
            bar.get_width() / 2,
            bar.get_y() + bar.get_height() / 2,
            f'{value:.2f}',
            ha='center',
            va='center',
            color='black'
        )

    ax.set_xlabel('Luck Index (Actual Wins - Expected Wins)')
    ax.set_title('Pythagorean Expectation Luck')
    ax.invert_yaxis()  # Invert y-axis to have the best luck on top
    
    return fig