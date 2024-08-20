# Stock Price Analyst [CrewAi]

This project has a Python Jupyter Notebook (`stocks-crew.ipynb`) and uses [CrewAI framework](https://www.crewai.com/) to simulates a Stock Analyst.
It gets price variation from a year and last news about stock ticket informed and gives a 
report about que stock.

This project uses [*python poetry*](https://python-poetry.org/) to manage packages and track dependencies, use command below to install dependencies in a virtual environment:
```
poetry install
```

OpenAi API is necessary to run this project, add a Secret Key to [secrets.toml](./.streamlit/secrets.toml.example) file in order to access the API.
