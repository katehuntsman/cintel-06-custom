import pandas as pd
import requests
from io import StringIO
import plotly.express as px
from shiny import App, ui, render, reactive
import faicons as fa

# Fetch Titanic dataset from URL
url = "https://raw.githubusercontent.com/katehuntsman/cintel-06-custom/refs/heads/main/dashboard/titanic.csv"

# Fetch the data using requests
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Convert the raw CSV text content into a pandas DataFrame
    df = pd.read_csv(StringIO(response.text))
    
    # Clean column names (remove leading/trailing spaces and convert to lowercase)
    df.columns = df.columns.str.strip().str.lower()
else:
    print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
    df = pd.DataFrame()  # Empty dataframe if failed

# Define Font Awesome icons for the Titanic dataset
ICONS = {
    "ship": fa.icon_svg("ship"),  # Titanic ship icon
    "life-ring": fa.icon_svg("life-ring"),  # Survival related
    "person": fa.icon_svg("user"),  # Gender related
    "ticket": fa.icon_svg("ticket"),  # Pclass related
    "calendar": fa.icon_svg("calendar"),  # Age related
}

# Sidebar Layout using ui.sidebar for filtering options
sidebar = ui.sidebar(
    ui.h5(ui.TagList("Titanic Data Filters ", ICONS['ship'])),

    # Survival Status checkbox group with life-ring icon
    ui.input_checkbox_group(
        "selected_survival", 
        ui.TagList("Survival Status ", ICONS['life-ring']),  
        choices=["Survived", "Did not survive"],  
        inline=True
    ),

    # Pclass Selectize dropdown with ticket icon, adding "Select All" option
    ui.input_selectize(
        "selected_pclass", 
        ui.TagList("Select Pclass ", ICONS['ticket']),  
        choices=["1", "2", "3", "All"],  # Adding "All" as a choice
        selected=["1"],  # Default selection (first class)
        multiple=True  # Allow multiple selections
    ),

    # Gender Selectize dropdown with person icon, adding "Select All" option
    ui.input_selectize(
        "selected_sex", 
        ui.TagList("Select Gender ", ICONS['person']),  
        choices=["male", "female", "All"],  # Adding "All" as a choice
        selected=["male", "female"],  # Default selection (both genders)
        multiple=True  # Allow multiple selections
    ),

    # Age range slider with calendar icon
    ui.input_slider(
        "age_range", 
        ui.TagList("Select Age Range ", ICONS['calendar']),  
        min=0, 
        max=100, 
        value=[20, 50], 
        step=1  
    )
)

# UI Definition using ui.page_sidebar() for main content layout
app_ui = ui.page_sidebar(
    sidebar,  # Sidebar content (previously defined)
    
    # Main content area using ui.page_fluid() for fluid layout
    ui.page_fluid(
        # Card for displaying survival counts as value boxes
        ui.card(
            ui.card_header(ui.TagList("Survival Summary ", ICONS['life-ring'])),
            ui.card_body(
                ui.row(
                    ui.column(6, ui.output_ui("survived_value_box")),  # Survived count box
                    ui.column(6, ui.output_ui("not_survived_value_box"))  # Not Survived count box
                )
            )
        ),
        
        # Row for Plotly chart and Data Table side by side
        ui.row(
            # Plotly chart (Age vs Fare)
            ui.column(6,
                ui.card(
                    ui.card_header(ui.TagList("Age vs. Fare ", ICONS['calendar'])),
                    ui.card_body(ui.output_ui("plot"))
                )
            ),
            
            # Data Table for Titanic Data
            ui.column(6,
                ui.card(
                    ui.card_header(ui.TagList("Titanic Data Table ", ICONS['ship'])),
                    ui.card_body(ui.output_ui("data_grid"))
                )
            )
        ),
        
        # Data Table for all output info
        ui.card(
            ui.card_header(ui.TagList("Full Data Output", ICONS['ship'])),
            ui.card_body(ui.output_ui("data_table"))
        )
    )
)

# Server function: where all the interactivity happens
def server(input, output, session):

    # Reactive calculation to simulate data updates or filtering based on inputs
    @reactive.Calc
    def filtered_data():
        # Get the inputs correctly
        selected_survival = input.selected_survival()  # Get survival status
        selected_pclass = input.selected_pclass()  # Get passenger class
        selected_sex = input.selected_sex()  # Get gender
        age_range = input.age_range()  # Get age range

        # Filter data based on inputs
        filtered_df = df.copy()

        # Apply survival status filter
        if "Survived" in selected_survival:
            filtered_df = filtered_df[filtered_df['survived'] == 1]
        if "Did not survive" in selected_survival:
            filtered_df = filtered_df[filtered_df['survived'] == 0]
        
        # Handle "Select All" logic for passenger class and gender filters
        if "All" in selected_pclass:
            selected_pclass = ["1", "2", "3"]  # Treat "All" as all classes
        if "All" in selected_sex:
            selected_sex = ["male", "female"]  # Treat "All" as all genders
        
        # Apply passenger class filter (ensure the input is iterable)
        if selected_pclass:
            filtered_df = filtered_df[filtered_df['pclass'].isin(map(int, selected_pclass))]
        
        # Apply gender filter (ensure the input is iterable)
        if selected_sex:
            filtered_df = filtered_df[filtered_df['sex'].isin(selected_sex)]
        
        # Apply age range filter
        if age_range:
            filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

        return filtered_df

    # Render the Plotly chart
    @output
    @render.ui
    def plot():
        filtered_df = filtered_data()  # Directly call the reactive filtered data
        fig = px.scatter(filtered_df, x='age', y='fare', color='survived', title='Age vs Fare by Survival Status')
        return ui.HTML(fig.to_html(full_html=False))  # Render Plotly figure as HTML

    # Render the data grid (without row index)
    @output
    @render.ui
    def data_grid():
        filtered_df = filtered_data()  # Directly call the reactive filtered data
        # Make sure the filtered dataframe has data before rendering
        if filtered_df.empty:
            return ui.markdown("No data to display with the selected filters.")
        
        # Render the filtered data table, excluding the index
        return ui.HTML(filtered_df.to_html(classes='table table-striped table-bordered', index=False))  # Exclude the row index

    # Render the survived count value box (green)
    @output
    @render.ui
    def survived_value_box():
        filtered_df = filtered_data()  # Directly call the reactive filtered data
        survived_count = len(filtered_df[filtered_df["survived"] == 1])
        return ui.HTML(f'<div style="background-color: #4CAF50; color: white; padding: 20px; border-radius: 8px; text-align: center;">'
                       f'<strong>Survived</strong><br>{survived_count}</div>')  # Green box for survived

    # Render the not survived count value box (red)
    @output
    @render.ui
    def not_survived_value_box():
        filtered_df = filtered_data()  # Directly call the reactive filtered data
        not_survived_count = len(filtered_df[filtered_df["survived"] == 0])
        return ui.HTML(f'<div style="background-color: #F44336; color: white; padding: 20px; border-radius: 8px; text-align: center;">'
                       f'<strong>Not Survived</strong><br>{not_survived_count}</div>')  # Red box for not survived

    # Render the full data table with all the output info (filtered data + summary)
    @output
    @render.ui
    def data_table():
        filtered_df = filtered_data()  # Directly call the reactive filtered data
        # Prepare summary stats for display
        survival_summary = filtered_df['survived'].value_counts().to_frame().reset_index()
        survival_summary.columns = ['Survival Status', 'Count']
        
        # Add survival summary to filtered dataframe
        filtered_df_with_summary = pd.concat([filtered_df, survival_summary], axis=1)
        
        # Render the full data table
        return ui.HTML(filtered_df_with_summary.to_html(classes='table table-striped table-bordered', escape=False)) 

# Create the app object
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()