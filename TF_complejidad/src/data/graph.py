import csv
import json
from data import create_graph
import pandas as pd

df = pd.read_csv('src\data\dataset.csv')

unique_genres = set()

for genres in df['genres']:
    if isinstance(genres, str):  # only attempt to split if genres is a string
        genres_list = genres.split()
        unique_genres.update(genres_list)

df_genres = pd.DataFrame(list(unique_genres), columns=['Genres'])
df_genres.to_csv('src\data\genres.csv', index=False)

import pandas as pd
import ast

df = pd.read_csv('src\data\dataset.csv')

unique_production_companies = set()

for companies in df['production_companies']:
    if isinstance(companies, str):  
        companies_list = ast.literal_eval(companies)  # convert string to list of dicts
        for company in companies_list:
            unique_production_companies.add(company['name'])

df_production_companies = pd.DataFrame(list(unique_production_companies), columns=['Production Companies'])
df_production_companies.to_csv('src\data\production_companies.csv', index=False)