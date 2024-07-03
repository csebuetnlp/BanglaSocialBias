sort_order = {
    "Communal": 3,
    "Communal+Occupation": 7,
    "Outlook+Occupation": 6,
    "Personality+Occupation": 4,
    "Outlook": 2,
    "Personality": 1,
    "Ideology+Occupation": 5,
    "Ideology": 0,
}

import json 

with open('./template_results.json', 'r') as f:
    data = json.load(f) 

# Models and categories
models = list(data.keys())
categories = ["Gender", "Religion"]

# Define the colors for different categories
# colors = {
#     "Communal": "#8AC926",  # Greenish
#     "Occupation+Communal": "#1982C4",  # Blue
#     "Outlook+Occupation": "#FFCA3A",  # Yellow
#     "Personality+Occupation": "#FF595E",  # Red
#     "Outlook": "#6A4C93",  # Purple
#     "Personality": "#4CC9F0",  # Light Blue
#     "Ideology": "#00AFB9",  # Cyan
#     "Ideology+Occupation": "#F15BB5",  # Pink
# }

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the seaborn style
sns.set(style="whitegrid")

# Colors for each model
model_colors = {
    "GPT - 3.5": sns.color_palette("muted")[0],  # Blue
    "GPT - 4o": sns.color_palette("muted")[2],  # Red
    "Llama - 3": sns.color_palette("muted")[3],  # Green
}

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 7))

# Define the width of a single bar
bar_width = 0.2

# Prepare data for plotting
all_gender_categories = list(
    set().union(*(data[model]["Gender"].keys() for model in models))
)
all_gender_categories.sort(key=lambda x: sort_order.get(x, float("inf")))

# Create positions for the groups
num_models = len(models)
num_categories = len(all_gender_categories)
positions = np.arange(num_categories) * (bar_width * (num_models + 1))

# Plot data
for i, model in enumerate(models):
    category = "Gender"
    category_data = data[model][category]

    # Filter out None values
    filtered_values = {k: v for k, v in category_data.items() if v is not None}

    # Bar heights
    heights = [filtered_values.get(cat, 0) for cat in all_gender_categories]

    # Plot bars
    ax.bar(
        positions + i * bar_width,
        heights,
        bar_width,
        label=model,
        color=model_colors[model],
        edgecolor="black",  # Add borders
    )

# Customize the plot
ax.set_ylabel("DI score", fontsize=18, fontweight="bold")
# ax.set_yticklabels(fontsize=16)
ax.set_ylim(0, 3)
ax.set_xticks(positions + (num_models - 1) * bar_width / 2)
ax.set_xticklabels(all_gender_categories, rotation=30, ha="right", fontsize=18)
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.15),
    fontsize=18,
    ncol=num_models,
    frameon=True,
)

# Remove vertical gridlines and keep horizontal gridlines
ax.grid(axis="y", linestyle="--", linewidth=0.7)
ax.grid(axis="x", visible=False)

# Make the horizontal line at y=1 bold
ax.axhline(y=1, color="cyan", linewidth=2)

# Tight layout for better spacing
plt.tight_layout()

# Show the plot
plt.show()
