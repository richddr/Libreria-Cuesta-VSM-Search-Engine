import math
import os
import webbrowser
from nltk.compat import raw_input
import csv
import pprint
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SpanishStemmer
from numpy import dot
from numpy.linalg import norm
__author__ = 'Richard Garcia || Ricardo Batista'

queries = ["mujer", "historia dominicana", "como ganar dinero"]
query_id = 2
queries_group_analysis = [(5, 6, 9, 38, 48, 61, 77, 78, 86, 92), (82, 84, 87, 88, 89, 90, 96, 98), (71, 81, 93)]
class_query = True

user_query = raw_input("Especifique el query a consultar: ")
if user_query in queries:
    query = user_query
    query_id = queries.index(user_query)
else:
    class_query = False
    query = user_query

#PREPROCESAMOS LOS DOCUMENTOS Y CREAMOS NUESTRO VECTOR DE PALABRAS
file = open("libros_libreriacuesta.csv", "r")
reader = csv.DictReader(file, delimiter=',')

stop = stopwords.words('spanish')
tokenizer = RegexpTokenizer(r'\w+')
#no funciono, es excelente en ingles pero no muy buena herramienta en español, mismo caso para sinonimos
stemmer = SpanishStemmer()
all_words = dict()
lista_docs_preprocesados = []
docs_titulo_link = []
results = []
#creamos nuestro vector de palabras global, analizando cada documento
for line in reader:
    docs_titulo_link.append({"id": line["id"], "titulo": line["titulo"], "link": line["link_libreria"]})
    data = line["titulo"].lower() + " " + line["argumento"].lower()
    tokens = tokenizer.tokenize(data)  # tokenizamos
    lista = []
    listaStemmed = []
    for i in tokens:
        if i not in stop:  # filtramos por stopwords
            lista.append(i)
            listaStemmed.append(stemmer.stem(i))
            all_words.setdefault(i, 0)
            all_words[i] += 1
    lista_docs_preprocesados.append(lista)
    #print(lista)
    #print(listaStemmed)
list_keys_all_words = sorted(list(all_words.keys()))

#Creamos los IDF de cada palabra, por cada palabra se guarda la cantidad de documentos en la que aparece
idf_terms = [0]*len(list_keys_all_words)
for doc in lista_docs_preprocesados:
    iterator = 0
    for palabra in list_keys_all_words:
        if palabra in doc:
            idf_terms[iterator] += 1
        iterator += 1
#print(idf_terms)

#funcion que crea el vector de un documento/query
def create_vector(lenVectorArray, document, total_cant_docs):
    #calculamos los term frequency del documento
    term_freq = {}
    for word in document:
        if word in term_freq:
            term_freq[word] += 1
        else:
            term_freq[word] = 1

    #creamos nuestro vector
    doc_vector = [0] * lenVectorArray
    iterator = 0
    for key_in_vector in list_keys_all_words:
        if key_in_vector in document:
            # si la palabra existe, se marca con la frecuencia que existe que existe en el doc, de lo contrario 0.
            doc_vector[iterator] = float(term_freq[key_in_vector])
        else:
            doc_vector[iterator] = 0
        iterator += 1
    iterator = 0
    for index in idf_terms:
        if index != 0 and doc_vector[iterator] != 0:
            doc_vector[iterator] = math.log2((total_cant_docs / index)) * doc_vector[iterator]
        iterator += 1
    #print(doc_vector)
    return doc_vector

# creamos el vector del query a consultar
vector_query = create_vector(lenVectorArray=len(list_keys_all_words), document=query.lower().split(),
                             total_cant_docs=len(lista_docs_preprocesados))


def check_if_query_appears(vector):
    for i in vector:
        if i != 0:
            return True
    return False


def get_result_link(id_book):
    for i in results:
        if int(i[0]) == int(id_book):
            return i[2]


appears = check_if_query_appears(vector_query)
if appears:
    #creamos los vectores de cada documento y lo comparamos con el vector del query
    iterator = 0
    for documento in lista_docs_preprocesados:
        #vector del documento actual
        vector_doc = create_vector(lenVectorArray=len(list_keys_all_words), document=documento,
                                   total_cant_docs=len(lista_docs_preprocesados))
        #cos(A,B) = dot(A,B) / ( || A || * || B || )
        similaridad = float(dot(vector_doc, vector_query) / (norm(vector_doc) * norm(vector_query)))
        if similaridad > 0:
            results.append((
                docs_titulo_link[iterator]["id"], docs_titulo_link[iterator]["titulo"], docs_titulo_link[iterator]["link"],
                similaridad))
        iterator += 1

    #ordenamos los resultados
    results = sorted(results, key=lambda x: (x[3]), reverse=True)
    pprint.pprint(results)
    #calculamos precision y recall, si el query a consultar fue uno de los tres establecidos en el curso
    precision = 0
    recall = 0
    f_measure = 0
    if class_query:
        precision_asserted = 0
        for i in results:
            if int(i[0]) in queries_group_analysis[query_id]:
                precision_asserted += 1
        precision = precision_asserted / len(results)
        recall = precision_asserted / len(queries_group_analysis[query_id])
        f_measure = (2 * precision * recall) / (precision + recall)
        print("\nprecision: " + str(precision))
        print("recall: " + str(recall))
        print("f_measure: " + str(f_measure))
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        pprint.pprint(results)
        if class_query:
            print("\nprecision: " + str(precision))
            print("recall: " + str(recall))
            print("f_measure: " + str(f_measure))
        user_link_click = raw_input("Digite el id del libro que desea visitar (Presione 'e' para salir): ")
        if user_link_click == 'e':
            break
        url = get_result_link(user_link_click)
        if url is None:
            break
        webbrowser.open(url, new=2, autoraise=True)
else:
    #query no aparece
    print("La consulta '"+user_query+"' no aparece en la lista de libros.\n")
    os.system('pause' if os.name == 'nt' else 'read')