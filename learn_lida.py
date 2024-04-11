#%%
import lida
import os
from lida import llm, Manager
openai_api_key =os.getenv('OPENAI_API_KEY')
lida = Manager(text_gen = llm("openai", api_key=openai_api_key)) # !! api key
summary = lida.summarize("data/cities_for_map.csv")
goals = lida.goals(summary, n=2)# exploratory data analysis
charts = lida.visualize(summary=summary, goal = goals[0])

#%%
