# ejercicio que usa una API pública para mostrar un dato curioso

import requests

respuesta = requests.get("https://catfact.ninja/fact")
print(respuesta)


# que tipo de datos es la respuesta?
#print(type(respuesta))

# la respuesta es un objeto de la clase Response
# podemos ver sus atributos y métodos
#print(dir(respuesta))

# listemos los atributos
# atributos = [attr for attr in dir(respuesta) if not attr.startswith('_')]
# for attr in atributos:
#     print(attr)

# Los atributos más útiles de requests.Response son:
# status_code - Código HTTP (200, 404, etc.)
# text - Contenido de la respuesta como string
# content - Contenido en bytes
# json() - Método para convertir respuesta JSON a diccionario
# headers - Headers de la respuesta
# url - URL final de la petición
# encoding - Codificación detectada
# ok - True si status_code < 400

# veamos el atributo text y su tipo
# print(respuesta.text)
# print(type(respuesta.text))

# convertir la respuesta a un diccionario con el metodo json
# print(respuesta.json())
# print(type(respuesta.json()))

#print("Dato curioso:")
#print(respuesta.json()["fact"])
