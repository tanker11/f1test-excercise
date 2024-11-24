from bokeh.plotting import figure, show

# Example data
data = {
    "laps": ["1", "2", "3", "4"],
    "Verstappen": [1, 2, 3, 1],
    "Hamilton": [2, 1, 1, 2],
    "Leclerc": [3, 3, 2],
}

# Create diagram area
p = figure(title="Position of drivers in each laps", x_axis_label="Laps", y_axis_label="Position",
           x_range=data["laps"], y_range=(20, 0), height=400, width=800) #y range is the possible positions

# Add lines
colors = ["blue", "red", "green"]
for i, racer in enumerate(data.keys() - {"laps"}):
    p.line(data["laps"], data[racer], line_width=2, color=colors[i], legend_label=racer)

# Add details
p.legend.title = "Drivers"
p.legend.location = "top_left"
p.yaxis.ticker = list(range(1, len(data) + 1))

show(p)
