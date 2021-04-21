import csv #this calls the comma separated values file library
import pandas as pd

df = pd.read_csv("cropmixdata.csv") #this saves it under the name 'df'

import altair as alt

#BCG Matrix maker
chart= alt \
  .Chart(df) \
  .mark_circle(size=200) \
  .encode(#allows me to specify details of the graph
    x = alt.X('Revenue ($/acre):Q', scale = alt.Scale(zero = False), title = 'Revenue ($/acre)'), #data used for x variable
    y = alt.Y('Water Need (mm/year):Q', scale = alt.Scale(zero = False)), #data used for y
    color = 'Land Use', #color codes each data point by company name
) .properties( #makes the chart easier to see in these sizes
    width = 400,
    height = 400
)
