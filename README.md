# Stock Price Analyst [CrewAi]

This project uses [*pipenv*](https://pypi.org/project/pipenv/) to manage packages and track dependencies, use command below to install dependencies in a virtual environment:

```
$ pipenv install
```

OpenAi API is necessary to run this project, add a Secret Key to [secrets.toml](./.streamlit/secrets.toml.example) file in order to access the API.

## How to run

After installing dependencies execute following command:

```
$ streamlit run stocks-crew.py
```