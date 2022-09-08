import requests
import re

def test_version():
   response = requests.get("http://192.168.0.206/version")
   expresion = re.compile('v[\\d].[\\d].[\\d]') # Expresion regular para que la version tenga el formato v.digitos.digitos.digitos
   version = response.text
   print("\nVersion obtenida en el testeo: " + version)

   assert response.status_code == 200, "Wrong status code"
   assert expresion.match(version) is not None, "La expresion regular no coincide"

def test_test():
   response = requests.get("http://192.168.0.206/test")

   assert response.status_code == 200, "Wrong status code"
   assert response.text == "Response from a generic test", "El resultado del test no es el esperado"

def main_test():
    test_version()
    test_test()
    print("\nTest finalizado correctamente")

if __name__ == '__main__':
    main_test()