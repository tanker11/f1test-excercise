import pandas as pd
from bokeh.plotting import figure, show

# Example data in a pandas DataFrame
data = {
    "events": ["1", "2", "3", "4"],
    "1": [1, 2, 3, 1],
    "44": [2, 1, 1, 2],
    "16": [3, 3, 2, None],  # Pad missing values with None or NaN
}

df = pd.DataFrame(data)

print(df)

# Create diagram area
p = figure(title="Position of drivers", x_axis_label="Events", y_axis_label="Position",
           x_range=df["events"], y_range=(20, 0), height=400, width=800)  # y_range is the possible positions

# Add lines
colors = ["blue", "red", "green"]
for i, racer in enumerate(df.columns[1:]):  # Skip the "events" column
    p.line(df["events"], df[racer], line_width=2, color=colors[i], legend_label=racer)

# Add details
p.legend.title = "Drivers"
p.legend.location = "top_left"
p.yaxis.ticker = list(range(1, 21))

show(p)
