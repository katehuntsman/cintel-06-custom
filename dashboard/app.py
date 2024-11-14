import shiny
import pandas as pd
import plotly.express as px
from shiny import ui, render, reactive

# Load the dataset
df = pd.read_csv('/Users/katehuntsman/Downloads/exercise.csv')

# Define the reactive filter function
@reactive.Calc
def filtered_data(exercise_type, gender, day_of_week):
    filtered_df = df.copy()
    
    if exercise_type != 'All':
        filtered_df = filtered_df[filtered_df['exercise'] == exercise_type]
    
    if gender != 'All':
        filtered_df = filtered_df[filtered_df['sex'] == gender]
        
    if day_of_week != 'All':
        filtered_df = filtered_df[filtered_df['day'] == day_of_week]
    
    return filtered_df

# Define the UI with input options and output areas
sidebar = ui.sidebarLayout(
    ui.sidebarPanel(
        ui.input_select("exercise_type", "Choose Exercise Type", choices=["All", "Running", "Yoga", "Cycling"]),
        ui.input_select("gender", "Choose Gender", choices=["All", "Male", "Female"]),
        ui.input_select("day", "Choose Day", choices=["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    ),
    ui.mainPanel(
        ui.output_text("selected_filters"),
        ui.output_table("filtered_table"),
        ui.output_plot("exercise_plot")
    )
)

# Define the server logic for rendering output
def server(input, output, session):
    # Display selected filters as text
    @output.text
    def selected_filters():
        return f"Filters applied: Exercise - {input.exercise_type()}, Gender - {input.gender()}, Day - {input.day()}"
    
    # Display the filtered data as a table
    @output.table
    def filtered_table():
        return filtered_data(input.exercise_type(), input.gender(), input.day())
    
    # Display the filtered data as a Plotly chart
    @output.plot
    def exercise_plot():  # <-- Corrected: added parentheses here
        filtered_df = filtered_data(input.exercise_type(), input.gender(), input.day())
        
        # Create the Plotly chart
        fig = px.box(filtered_df, x="exercise", y="minutes", color="sex", 
                     title="Exercise Minutes Distribution by Type and Gender")
        return fig

# Create the Shiny app by combining the UI and server logic
app = shiny.App(ui=sidebar, server=server)

# Run the app
app.run()

