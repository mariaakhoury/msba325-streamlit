# Lebanon FDI, 1990-2022 - Interactive Streamlit App

MSBA 325 - Interactive Visualizations with Streamlit

**Live app:** https://msba325-app-jhehwocxh2agtsqxmy8tyy.streamlit.app/

## What this is

An interactive page built around Foreign Direct Investment in Lebanon between 1990 and 2022.
It reuses the dataset and two of the charts from the earlier Plotly assignment: a line chart of
inflows against outflows over time, and a bar chart of the net position per year.

## The two linked controls

1. **Period slider** - choose a range of years. Both charts redraw for that range only.
2. **Year picker** - choose a single year *from within the period selected above*. The options in
   this dropdown come from the slider, so narrowing the period narrows the list. The chosen year is
   marked on the line chart and highlighted in the bar chart, and its figures appear at the top.

The second control depends on the first, so the page supports drilling down into a period rather
than filtering two things independently.

## Data

Foreign Direct Investment, Lebanon, 1990-2022. Downloaded from the AUB Linked Data Portal
(linked.aub.edu.lb), originally sourced from FAOSTAT. Values in millions of US dollars.
The file arrives in long format (one row per year per flow type) and is pivoted to wide format
inside the app.

## Files

- `app.py` - the Streamlit app
- `fdi.csv` - the dataset, as downloaded from the portal
- `requirements.txt` - dependencies

## Running it locally

```
pip install -r requirements.txt
python -m streamlit run app.py
```
