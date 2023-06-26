import csv
import json

# Cambiar el metodo con el que medimos el peso (Hacerlo mas complejo (?) )
def get_weight(movie1, movie2):
    weight = 0

    # Comparar director
    if movie1['director'] == movie2['director']:
        weight += 1

    # Comparar géneros
    genres1 = set(movie1['genres'].split())
    genres2 = set(movie2['genres'].split())
    weight += len(genres1.intersection(genres2))

    # Comparar keywords
    keywords1 = set(movie1['keywords'].split())
    keywords2 = set(movie2['keywords'].split())
    weight += len(keywords1.intersection(keywords2))

    # Comparar production_companies
    companies1 = {company['name'] for company in json.loads(movie1['production_companies'])}
    companies2 = {company['name'] for company in json.loads(movie2['production_companies'])}
    weight += len(companies1.intersection(companies2))

    return weight

def get_data():
    movies = []
    with open('src\data\dataset.csv', encoding='utf-8') as input_file:
        csv_reader = csv.DictReader(input_file)
        for row in csv_reader:
            movies.append(row)
    return movies

# Leer el archivo 'dataset.csv' y almacenar las películas en una lista
movies = []
with open('src\data\dataset.csv', encoding='utf-8') as input_file:
    csv_reader = csv.DictReader(input_file)
    for row in csv_reader:
        movies.append(row)

def create_graph():
    # Crear el archivo 'graph.csv' con las columnas Source, Target y Weight
    with open('src\data\graph.csv', mode='w', encoding='utf-8', newline='') as output_file:
        fieldnames = ['Source', 'Target', 'Weight']
        csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        csv_writer.writeheader()

        # Calcular el peso de las aristas entre las primeras 2000 películas
        for i in range(len(movies)):
            movie1 = movies[i]
            for j in range(i + 1, len(movies)):
                movie2 = movies[j]

                weight = get_weight(movie1, movie2)

                if weight > 3:
                    csv_writer.writerow({'Source': i + 1, 'Target': j + 1, 'Weight': weight})

