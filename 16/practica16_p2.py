import requests
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON

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

def ejecutar_consulta_sparql_wrapper(fuseki_sparql_url, consulta_sparql):
    # Crear un objeto SPARQLWrapper y configurar la consulta y el formato de retorno
    sparql = SPARQLWrapper(fuseki_sparql_url)
    sparql.setQuery(consulta_sparql)
    sparql.setReturnFormat(JSON)

    # Ejecutar la consulta SPARQL
    try:
        sparql_results = sparql.query().convert()
        if 'results' in sparql_results:
            for result in sparql_results['results']['bindings']:
                name = result['name']['value'] if 'name' in result else 'N/A'
                president = result['president']['value'] if 'president' in result else 'N/A'
                print(f"Nombre: {name}, Presidente: {president}")
        else:
            print("No se encontraron resultados.")
    except Exception as e:
        print(f"Error al ejecutar la consulta SPARQL: {e}")

def menu():
    dataset = 'p16_investigaciones'
    archivo_ttl = 'investigaciones_kg.ttl'
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
                PREFIX ex: <http://example.org#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                SELECT ?name ?president
                WHERE {
                    ?investigation a ex:Indictment ;
                                ex:name ?name ;
                                ex:president ?president ;
                                ex:outcome ex:conviction ;
                                ex:overturned true .
                }
                """
            ejecutar_consulta_sparql_wrapper(fuseki_sparql_url, consulta_sparql)

        elif opcion == '3':
            break

        else:
            print("Opción no válida, por favor seleccione nuevamente.")

if __name__ == '__main__':
    menu()