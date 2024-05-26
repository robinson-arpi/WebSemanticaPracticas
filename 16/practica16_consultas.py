import requests
from rdflib import Graph
from SPARQLWrapper import POST, SPARQLWrapper, JSON
from tabulate import tabulate


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

def ejecutar_consulta_sparql(fuseki_sparql_url, consulta_sparql):
    sparql = SPARQLWrapper(fuseki_sparql_url)
    sparql.setQuery(consulta_sparql)
    sparql.setReturnFormat(JSON)

    try:
        sparql_results = sparql.query().convert()
        return sparql_results['results']['bindings']
    except Exception as e:
        print(f"Error al ejecutar la consulta SPARQL: {e}")
        return None
    
def ejecutar_actualizacion_sparql(fuseki_update_url, consulta_sparql):
    sparql = SPARQLWrapper(fuseki_update_url)
    sparql.setQuery(consulta_sparql)
    sparql.setMethod(POST)
    sparql.setReturnFormat(JSON)
    
    try:
        sparql.query()
        print("Grafo actualizado exitosamente.")
    except Exception as e:
        print(f"Error al actualizar el grafo: {e}")


consulta_1 = """
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

#Por cada presidente, enumerar el número de condenas e indultos realizados
consulta_2 ="""
                PREFIX ex: <http://example.org#>
                SELECT ?president (COUNT(?condena) AS ?condenas) (COUNT(?indulto) AS ?indultos)
                WHERE {
                    ?investigation ex:president ?president .
                    OPTIONAL { 
                        ?investigation ex:outcome ex:conviction .
                        BIND(1 AS ?condena) 
                    }
                    OPTIONAL { 
                        ?investigation ex:pardoned true. 
                        BIND(1 AS ?indulto) 
                    }
                }
                GROUP BY ?president

"""


consulta_3 ="""
                PREFIX ex: <http://example.org#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>

                INSERT {
                    ?name_iri a foaf:Person ;
                            foaf:name ?name .
                }
                WHERE {
                    {
                        ?s ex:name ?name_iri .
                        FILTER (?name_iri != "None")
                        BIND(REPLACE(STR(?name_iri), str(ex:), "") AS ?name)
                    }
                    UNION
                    {
                        ?s ex:president ?name_iri .
                        FILTER (?name_iri != "None")
                        BIND(REPLACE(STR(?name_iri), str(ex:), "") AS ?name)
                    }
                }

"""

consulta_4 = """ 
                PREFIX ns1: <http://example.org#>
                PREFIX dbp: <https://dbpedia.org/page/>
                DELETE {
                    ?subject ns1:name ?oldObject .
                }
                INSERT {
                    ?subject dbp:name ?newObject .
                }
                WHERE {
                    ?subject ns1:name ?oldObject .
                    BIND(IRI(CONCAT("https://dbpedia.org/page/", STRAFTER(STR(?oldObject), "http://example.org#"))) AS ?newObject)
                }
"""

def menu():
    dataset = 'p16_investigaciones'
    archivo_ttl = 'investigaciones_kg.ttl'
    fuseki_url = f'http://localhost:3030/{dataset}/data'
    fuseki_sparql_url = f'http://localhost:3030/{dataset}/sparql'
    fuseki_update_url = f'http://localhost:3030/{dataset}/update'
    
    while True:
        print("\nMenú")
        print("1. Cargar datos en Fuseki")
        print("2. Consulta 1")
        print("3. Consulta 2")
        print("4. Consulta 3")
        print("5. Consulta 4")
        print("6. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            cargar_datos(fuseki_url, archivo_ttl)

        elif opcion == '2':
            resultados_1 = ejecutar_consulta_sparql(fuseki_sparql_url, consulta_1)
            if resultados_1:
                print("Personas condenadas cuyas condenas fueron anuladas y el presidente que ejecutó la anulación:")
                data = []
                for resultado in resultados_1:
                    name = resultado['name']['value'].split('#')[-1]
                    president = resultado['president']['value'].split('#')[-1]
                    data.append([name, president])
                print(tabulate(data, headers=["Nombre", "Presidente"], tablefmt="grid"))

        elif opcion == '3':
            resultados_2 = ejecutar_consulta_sparql(fuseki_sparql_url, consulta_2)
            if resultados_2:
                print("\nTabla combinada de Condenas e Indultos:")
                data_combinada = []
                for resultado in resultados_2:
                    president = resultado['president']['value'].split('#')[-1]
                    condenas = int(resultado['condenas']['value']) if 'condenas' in resultado else 0
                    indultos = int(resultado['indultos']['value']) if 'indultos' in resultado else 0
                    data_combinada.append([president, condenas, indultos])
                print(tabulate(data_combinada, headers=["Presidente", "Condenas", "Indultos"], tablefmt="grid"))
        
        elif opcion == '4':
            ejecutar_actualizacion_sparql(fuseki_update_url, consulta_3)

        elif opcion == '5':
            ejecutar_actualizacion_sparql(fuseki_update_url, consulta_4)    

        elif opcion == '6':
            break

        else:
            print("Opción no válida, por favor seleccione nuevamente.")

if __name__ == '__main__':
    menu()