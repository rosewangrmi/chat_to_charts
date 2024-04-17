#%%
import json
import time
from openai import OpenAI
import os

   
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

# pretty printing helper
def show_json(obj):
    display(json.loads(obj.model_dump_json()))

def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()
#%%
city_data = client.files.create(
    file=open(
        "data/cities_for_map.csv",
        "rb",
    ),
    purpose="assistants",
)

city_data_catalogue = client.files.create(
    file=open(
        "data/catalogue.csv",
        "rb",
    ),
    purpose="assistants",
)

assistant = client.beta.assistants.create(
    name="Data Visualization Developer",
    instructions= "You are professional data visualization developer. Please generate code that answers users questions on data. \
     You will create only python code that generates plots and tables that can be executed to answer users questions.",
    model="gpt-3.5-turbo",
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
    file_ids=[city_data.id],
)
show_json(assistant)
# %%
catalgoue = pd.read_csv('data/catalogue.csv')

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(assistant.id, thread, user_input)
    return thread, run

thread, run = create_thread_and_run(
    "You were given a data file cities_for_map.csv that describe emissoins of cities from different kinds of wastes. \
        The column description is available in {catalogue}.\
                Please generate python code that can make an interactive map using 2022 emissions data. Each bubble on the map represents one city. The size of  \
        the bubble is proportional to the total emissions for the city. When users click on the ciy, it will\
             show the emissions for each type of waste as a pie chart. Please generate only the python code for visualization. "
)
run = wait_on_run(run, thread)
pretty_print(get_response(thread))
# %%
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
data = pd.read_csv('data/cities_for_map.csv')

# Create the bubble map
fig = px.scatter_geo(data, 
                     lat='Latitude', 
                     lon='Longitude',
                     size='Total_emissions', 
                     hover_name='City',
                     color='Total_emissions',
                     color_continuous_scale=px.colors.sequential.Plasma,
                     projection="natural earth")

# Create pie charts for each waste type
for city in data['City']:
    city_data = data[data['City'] == city]
    labels = city_data.columns[3:]
    values = city_data.iloc[0, 3:].tolist()
    
    fig.add_trace(go.Pie(labels=labels, values=values, name=city, visible=False))

# Update layout to include pie charts
updatemenu = []
buttons = []
for index, city in enumerate(data['City']):
    buttons.append(dict(method='update',
                        args=[{'visible': [False] * len(data['City'])},
                              {'title': f'{city} Waste Emissions Pie Chart'}],
                        label=city))

updatemenu = []
updatemenu.append(dict(type='buttons', showactive=True, buttons=buttons)
                 )

fig.update_layout(updatemenus=updatemenu)

# Display the interactive map
fig.show()
# %%
