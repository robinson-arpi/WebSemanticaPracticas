import requests
from rdflib import Graph

def cargar_datos(fuseki_url, archivo_ttl):
    # Cargar el archivo Turtle con rdflib
    g = Graph()
    g.parse(archivo_ttl, format='turtle')

    # Serializar los datos en formato Turtle
    turtle_data = g.serialize(format='turtle')

    # Configurar los headers para la solicitud HTTP
    headers = {
        'Content-Type': 'text/turtle'
    }

    # Hacer la solicitud HTTP PUT para cargar los datos en el dataset
    response = requests.put(fuseki_url, data=turtle_data, headers=headers)

    # Verificar el estado de la respuesta
    if response.status_code == 200:
        print(f'Datos de {archivo_ttl} cargados exitosamente en Fuseki.')
    else:
        print(f'Error al cargar los datos de {archivo_ttl}: {response.status_code} - {response.text}')

def ejecutar_consulta(fuseki_sparql_url, consulta_sparql):
    # Configurar los parámetros de la consulta SPARQL
    params = {
        'query': consulta_sparql
    }

    # Hacer la solicitud HTTP POST para ejecutar la consulta SPARQL
    response = requests.post(fuseki_sparql_url, data=params)

    # Verificar el estado de la respuesta
    if response.status_code == 200:
        results = response.json()
        for result in results['results']['bindings']:
            print(result['name']['value'])
    else:
        print(f'Error al ejecutar la consulta SPARQL: {response.status_code} - {response.text}')


def menu():
    dataset = 'p16_estaciones'
    archivo_ttl = 'estaciones.ttl'
    while True:
        print("\nMenú")
        print("1. Cargar datos en Fuseki")
        print("2. Ejecutar consulta SPARQL")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            fuseki_url = f'http://localhost:3030/{dataset}/data'
            cargar_datos(fuseki_url, archivo_ttl)

        elif opcion == '2':
            fuseki_sparql_url = f'http://localhost:3030/{dataset}/sparql'
            consulta_sparql = """
                PREFIX est: <http://example.org/estaciones/>
                PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?name
                WHERE {
                    ?station a geo:Point ;
                            rdfs:label ?name .
                }
                """
            ejecutar_consulta(fuseki_sparql_url, consulta_sparql)

        elif opcion == '3':
            break

        else:
            print("Opción no válida, por favor seleccione nuevamente.")

if __name__ == '__main__':
    menu()