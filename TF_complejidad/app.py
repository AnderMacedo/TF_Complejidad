# def get Generos y Año
# Si son iguales continue
# -------------------- IMPORTACIONES --------------------
import copy
import tkinter as tk
import csv
import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from PIL import ImageTk, Image
from ttkthemes import ThemedStyle
from tkinter import scrolledtext
# -------------------------------------------------------
#Declarar la variable global
entry = None
result_text = None
entry_number = None
selected_category = None
selected_year = None
# ---------------------- FUNCIONES ----------------------
def generate_graph():
    # Crear un grafo vacío
    graph = nx.Graph()

    # Cargar los nodos del archivo id_label.csv
    with open('src\data\id_label.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            node_id = row['ID']
            label = row['Label']
            graph.add_node(node_id, label=label)

    # Cargar las aristas del archivo graph.csv
    with open('src\data\graph.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            source = row['Source']
            target = row['Target']
            weight = row['Weight']

            # Ignorar las aristas con Source o Target mayores a 2000
            if int(source) > 2000 or int(target) > 2000:
                continue

            graph.add_edge(source, target, weight=weight)

    return graph
# -------------------------------------------------------
def show_graph(edges):
    G = nx.Graph()

    for edge in edges:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])

    pos = nx.spring_layout(G)  # positions for all nodes

    nx.draw_networkx_nodes(G, pos, node_size=700)

    nx.draw_networkx_edges(G, pos, width=6)

    nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    plt.show()
# -------------------------------------------------------
def convert_graph(graph):
    return {str(node): {str(neighbour): graph.edges[node, neighbour]['weight'] for neighbour in graph[node]} for node in graph.nodes}
# -------------------------------------------------------
def get_movie_info_genres_year(movie_id):
    # Abrir el archivo CSV con la información adicional
    try:
        with open('src/data/dataset.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Buscar la película en el archivo CSV
            for row in reader:
                if int(movie_id) - 1 == int(row['index']):
                    # obtener los géneros y el año de lanzamiento
                    genres = [genre.strip() for genre in row['genres'].split(',')]
                    release_date = row['release_date']
                    # obtener solo el año de la fecha de lanzamiento
                    year = release_date.split('-')[0]

                    return genres, year
    except Exception as e:
        print(f"Error al abrir el archivo: {e}")

    return None
# -------------------------------------------------------
def bfs(graph, source, visited=set(), category=None, year=None):
    visited.add(source)  # ensure the source node is marked as visited
    queue = [source]
    while queue:
        node = queue.pop(0)

        if node not in visited:
            visited.add(node)
            queue.extend(set(graph[node]) - visited)

    return visited
# -------------------------------------------------------
def dijkstra(graph, source):
    global entry_number
    global selected_category
    global selected_year

    try:
        num_nodes = int(entry_number.get())
    except ValueError:
        print("El número introducido no es válido. Debe ser un número entero.")
        return [], []

    if source not in graph:
        print("El nodo inicial no se encuentra en el grafo.")
        return [], []

    heaviest_nodes = []
    heaviest_edges = []

    selected_category = str(selected_category)
    selected_year = str(selected_year)

    neighbor_weights = copy.deepcopy(graph[source])

    while len(heaviest_nodes) < num_nodes and neighbor_weights:
        max_node = max(neighbor_weights, key=neighbor_weights.get)

        # Obtenemos la información de genero y año del nodo
        genres_year_info = get_movie_info_genres_year(max_node)
        
        # Verificamos si se ha seleccionado una categoría o año
        if (selected_category is None or selected_category not in genres_year_info[0][0].split()) and (selected_year is None or selected_year != genres_year_info[1]):
            heaviest_nodes.append(max_node)
            heaviest_edges.append({'source': source, 'target': max_node, 'weight': neighbor_weights[max_node]})

        del neighbor_weights[max_node]

    if len(heaviest_nodes) < num_nodes:  # if not enough nodes found
        visited = bfs(graph, source, visited=set(heaviest_nodes), category=selected_category, year=selected_year)

        for node in visited:
            if len(heaviest_nodes) >= num_nodes:  # if we've found enough nodes
                break

            # Do not add the source node to the list of heaviest nodes
            if node != source and node not in heaviest_nodes:

                heaviest_nodes.append(node)
                # Add an edge with a dummy weight, as we don't have weight information in BFS
                heaviest_edges.append({'source': source, 'target': node, 'weight': 3})

    return heaviest_nodes, heaviest_edges
# -------------------------------------------------------
def get_movie_info(movie_id):
    # Abrir el archivo CSV con la información adicional
    with open('src\data\dataset.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        # Buscar la película en el archivo CSV
        for row in reader:
            if int(movie_id)-1 == int(row['index']):
                original_title = row['original_title']
                release_date = row['release_date']
                director = row['director']
                production_companies = json.loads(row['production_companies'])
                keywords = row['genres'].split()
                cast = row['cast'].split()

                # Formatear los datos de producción
                production_names = [company['name'] for company in production_companies]

                if len(cast) % 2 != 0:
                    cast.append('')
                # Formatear los datos de los actores
                cast_formatted = ', '.join([f"{cast[i]} {cast[i+1]}" for i in range(0, len(cast), 2)])

                return original_title, release_date, director, production_names, keywords, cast_formatted

    return None
# -------------------------------------------------------
def search_movie():
    global entry 
    global result_text

    result_text.configure(state='normal') 
    result_text.delete("1.0", "end")

    # Obtener el nombre de la película ingresado por el usuario
    movie_name = entry.get()

    # Eliminar los caracteres especiales y convertir todo a minúsculas
    movie_name = movie_name.lower().replace('"', '').replace(':', '').replace('.', '')

    # Abrir el archivo CSV
    with open('src\data\id_label.csv', 'r') as file:
        reader = csv.DictReader(file)

        # Buscar la película en el archivo CSV
        for row in reader:
            if movie_name == row['Label'].lower().replace('"', '').replace(':', '').replace('.', ''):
                movie_id = row['ID']
                movie_label = row['Label']
                break
        else:
            movie_id = None
            movie_label = None

    # Obtener información adicional de la película si se encontró su ID
    if movie_id:
        movie_info = get_movie_info(movie_id)

        nodes, edges = dijkstra(graph, movie_id)
        nodes_info = []

        for node in nodes:
            node_info = get_movie_info(node)
            if node_info:
                nodes_info.append(node_info)

        if movie_info:
            original_title, release_date, director, production_names, keywords, cast_formatted = movie_info
            result_text.insert('end', f"Nombre de la película: {original_title}\n"
                                    f"Fecha de salida: {release_date}\n"
                                    f"Director: {director}\n"
                                    f"Producciones: {', '.join(production_names)}\n"
                                    f"Géneros: {' '.join(keywords)}\n"
                                    f"Actores: {cast_formatted}")

            for node_info in nodes_info:
                original_title, release_date, director, production_names, keywords, cast_formatted = node_info
                # Agrega la información de cada nodo a result_text
                result_text.insert('end', "\n\n" + 
                                f"Nombre de la película: {original_title}\n"
                                f"Fecha de salida: {release_date}\n"
                                f"Director: {director}\n"
                                f"Producciones: {', '.join(production_names)}\n"
                                f"Géneros: {' '.join(keywords)}\n"
                                f"Actores: {cast_formatted}")

        else:
            result_text.insert(text="Información adicional no disponible")
        
        show_graph(edges)
    else:
        result_text.insert(text="La película no fue encontrada")

    result_text.configure(state='disabled')  # Deshabilitar la edición del texto
# -------------------------------------------------------
def show_code_window():
    global entry  # Indicar que se utilizará la variable global
    global entry_number  # Variable global para la entrada de número de películas
    global result_text
    global selected_category  # Variable global para almacenar la categoría seleccionada
    global selected_year  # Variable global para almacenar el año seleccionado

    window = tk.Toplevel()
    window.title("Mi Aplicación")
    
    window.geometry("736x1104")

    # Cargar la imagen de fondo
    background_image = Image.open("peli.jpeg")
    result_image=Image.open("rec.jpeg")
    
    result_image = result_image.resize((650, 750), Image.ANTIALIAS)
    background_photo = ImageTk.PhotoImage(background_image)
    result_photo=ImageTk.PhotoImage(result_image)
    
    # Crear un widget de etiqueta para mostrar la imagen de fondo
    background_label = tk.Label(window, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Crear un widget de entrada de texto para "Pelicula de referencia"
    ref_movie_label = tk.Label(window, text="Pelicula de referencia", fg="white", bg="black")
    ref_movie_label.pack(pady=5)
    entry = tk.Entry(window)
    entry.pack(pady=5)

    # Crear un widget de entrada de texto para "Número de películas que desea buscar"
    num_movies_label = tk.Label(window, text="Numero de peliculas que desea buscar: ", fg="white", bg="black")
    num_movies_label.pack(pady=5)
    entry_number = tk.Entry(window)
    entry_number.pack(pady=5)

    # Filtro de categoría
    def update_category_value(*args):
        global selected_category
        selected_category = genre_var.get()

    category_label = tk.Label(window, text="Filtro de categoría: ", fg="white", bg="black")
    genres_df = pd.read_csv('src\data\genres.csv')
    genres = ['--Ninguno--'] + list(genres_df['Genres'])
    genre_var = tk.StringVar(window)
    genre_var.set(genres[0])
    genre_var.trace('w', update_category_value)  # Llama a la función de actualización al cambiar la categoría seleccionada
    category_menu = tk.OptionMenu(window, genre_var, *genres)
    category_label.pack(pady=5)
    category_menu.pack(pady=5)

    # Filtro de año
    def validate_year(input_text):
        global selected_year
        if input_text.isdigit():
            selected_year = int(input_text)
            return True
        else:
            return False

    year_label = tk.Label(window, text="Filtro de año: ", fg="white", bg="black")
    validate_year_cmd = window.register(validate_year)
    year_entry = tk.Entry(window, validate='key', validatecommand=(validate_year_cmd, '%P'))
    year_label.pack(pady=5)
    year_entry.pack(pady=5)

    # Crear un widget de botón de búsqueda
    search_button = tk.Button(window, text="Buscar", command=search_movie, bg="#2C75BF", fg="white")
    search_button.pack(pady=10)
    
    label = tk.Label(window, image=result_photo)
    label.configure(fg="black", image=result_photo)
    label.pack()
    
    result_text = scrolledtext.ScrolledText(label, fg="black", bd=0, relief=tk.SOLID, wrap='word')
    result_text.place(relx=0.03, rely=0.03, relwidth=0.94, relheight=0.94)

    window.mainloop()
# -------------------------------------------------------
# Generar el grafo
nx_graph = generate_graph()
graph = convert_graph(nx_graph)

# Crear una instancia de la clase Tk
window = tk.Tk()
window.title("Ventana Principal")
window.geometry("420x300") 

background_image = Image.open("introd.gif")
background_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(window, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Crear una fuente personalizada
fuente_personalizada = ("Arial", 15, "bold")  # Familia de la fuente, tamaño, y estilo (negrita)
titulo = tk.Label(window, text="Bienvenido a nuestro buscador de peliculas", font=fuente_personalizada, bg="#6C488D", fg="black", bd=0, relief=tk.SOLID, wraplength=450, anchor="center", justify="center")
titulo.pack(pady=15)

# Crear un botón para ingresar
enter_button = tk.Button(window, text="Ingresar", command=show_code_window)
enter_button.pack(pady=50)

fuente_personalizada = ("Arial", 15, "bold")  # Familia de la fuente, tamaño, y estilo (negrita)
titulo = tk.Label(window, text="Grupo 05", font=fuente_personalizada, bg="#6C488D", fg="black", bd=0, relief=tk.SOLID, wraplength=450, anchor="center", justify="center")
titulo.pack(pady=50)

# Iniciar el bucle principal de la aplicación
window.mainloop()
# -------------------------------------------------------