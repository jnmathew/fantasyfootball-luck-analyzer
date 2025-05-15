from matplotlib import cm
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from analysis import calculate_scheduling_luck

def save_luck_indices_to_file_v3(league_data, luck_indices, output_file=None):
    """
    Save the luck indices of all teams to a file using the luck indices
    calculated from the league data.
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

def generate_opponent_underperformance_chart(luck_indices_df, output_file=None):
    """
    Generate a bar chart for the Luck Index of each team, sorted from worst luck to best luck.
    The chart will show the Luck Index for each team, with positive values indicating good luck
    and negative values indicating bad luck.

    Parameters:
    - luck_indices_df (pd.DataFrame): DataFrame containing team names and luck indices.
    - output_file (str): Optional. Filepath to save the plot.
    """
    
    # Sort data by Luck Index
    luck_indices_df = luck_indices_df.sort_values("Luck Index")

    # Create a bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        luck_indices_df["Team Name"], 
        luck_indices_df["Luck Index"], 
        color=["green" if x > 0 else "red" for x in luck_indices_df["Luck Index"]]
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
    plt.title("Opponent Underperformance: Luck Index by Team", fontsize=16)
    plt.xlabel("Team Name", fontsize=12)
    plt.ylabel("Luck Index", fontsize=12)
    plt.xticks(rotation=45, ha="right")  # Rotate team names for readability
    plt.tight_layout()

    # Save to file if specified
    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Chart saved to {output_file}")

    return plt

def create_scheduling_luck_dataframe(league_data):
    """
    Generate a DataFrame showing each team's hypothetical record if they had every 
    other team's schedule, based on simulated matchup results.

    Parameters:
        league_data (dict): Dictionary containing league information, including:
            - 'teams' (list): Each team is a dict with:
                - 'id' (int): Unique team identifier.
                - 'name' (str): Team name.

    Returns:
        pandas.DataFrame: A square DataFrame where both rows and columns are team names.
        Each cell contains a string like "wins-losses", representing how the row team 
        would have performed with the schedule of the column team.
    """
    hypothetical_records = calculate_scheduling_luck(league_data)

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
        fillcolor="red", opacity=0.15, line_width=0,
        name="Unlucky Loss Region"
    )
    fig.add_shape(
        type="path",
        path="M 0 0 L 0 -100 L -100 -100 Z",
        fillcolor="blue", opacity=0.15, line_width=0,
        name="Lucky Win Region"
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
        text="Unlucky Loss",
        showarrow=False,
        font=dict(family="Trebuchet MS", size=20, color="red", variant="small-caps"),
        align="center"
    )
    fig.add_annotation(
        x=-50, y=-90,
        text="Lucky Win",
        showarrow=False,
        font=dict(family="Trebuchet MS", size=20, color="blue", variant="small-caps"),
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