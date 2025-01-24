import pandas as pd
import matplotlib.pyplot as plt

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

def plot_luck_indices(data, output_file=None):
    """
    Plot the luck indices of Fantasy Football teams.

    Parameters:
    - data (DataFrame): The DataFrame containing team names and luck indices.
    - output_file (str): Optional. Filepath to save the plot.
    """
    # Sort data by Luck Index
    data = data.sort_values("Luck Index")

    # Create a bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(
        data["Team Name"], 
        data["Luck Index"], 
        color=["green" if x > 0 else "red" for x in data["Luck Index"]]
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

def main():
    """
    Main function to load data, plot, and save visualization.
    """
    # Input CSV file
    input_file = "luck_indices.csv"
    
    # Output image file
    output_file = "luck_index_chart.png"

    # Load data
    data = load_data(input_file)
    if data is None:
        return

    # Plot luck indices
    plot_luck_indices(data, output_file=output_file)

if __name__ == "__main__":
    main()
