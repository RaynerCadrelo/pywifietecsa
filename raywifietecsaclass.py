# coding=UTF-8

import requests
import lxml.html
import configparser

import os
directorio = os.path.dirname(os.path.abspath(__file__))

class RayWifiEtecsa:

    def __init__(self):

        self._configDataLogin = configparser.ConfigParser()
        self._configDataLogin.read(directorio+'/.datalogin')




    def status(self): # retorna "Desconectado" / "Conectado"
        try:
            self._x=requests.get("http://www.cubadebate.cu/")
        except:
            return("Desconectado")
        if self._x.text.count("Cubadebate"):
            return("Conectado")
        else:
            return("Desconectado")





    def login(self, username, password):
        try:
            self._x=requests.get("https://secure.etecsa.net:8443")
        except:
            return("Error de conexión")
        body=self._x.text
        elementForm={}
        root_element = lxml.html.fromstring(body)
        form = root_element.xpath('/html/body/div/div/div/div/form')[0]
        inputs = form.inputs
        for a in inputs:
            elementForm[ a.name ] = a.value

        elementForm['username'] = username
        elementForm['password'] = password

        try:
            self._x=requests.post(form.action, data=elementForm, headers = {'content-type': 'application/x-www-form-urlencoded'})
        except:
            return("Error de conexión")

        if self._x.status_code==200:
            if self._x.text.count("Su tarjeta no tiene saldo disponible"):
                return("Su tarjeta no tiene saldo disponible")
            if self._x.text.count("No se pudo autorizar al usuario"):
                return("No se pudo autorizar al usuario")
            if self._x.text.count("Usted está conectado"):
                pass
                #print("Usted está conectado")

        else:
            return("servidor no responde")

        body=self._x.text
        body2=body.split("ATTRIBUTE_UUID")[1].split("&remove=")[0].replace("+","").replace(" ","").replace("\r\n","").replace('"',"")
        urlParam = "ATTRIBUTE_UUID"+body2+"&remove=1"

        self._configDataLogin['DATA_LOGIN']={'DATA': urlParam}
        with open(directorio+'/.datalogin', 'w') as configfile:
            self._configDataLogin.write(configfile)

        return("Usted está conectado")







    def time(self):
        try:
            urlParam = self._configDataLogin['DATA_LOGIN']['DATA']
            self._x=requests.post("https://secure.etecsa.net:8443/EtecsaQueryServlet", data="op=getLeftTime&"+urlParam, headers = {'content-type': 'application/x-www-form-urlencoded'})
        except:
            return("Error de conexión")
        return(self._x.text)








    def logout(self):
        try:
            urlParam = self._configDataLogin['DATA_LOGIN']['DATA']
            self._x=requests.post("https://secure.etecsa.net:8443//LogoutServlet", data=urlParam, headers = {'content-type': 'application/x-www-form-urlencoded'})
        except:
            return("Error de conexión")

        if self._x.status_code==200:
            if self._x.text.count("SUCCESS"): #retorna esto: "logoutcallback('SUCCESS');"
                return("Cerrado con éxito")
            else:
                return("Error al desconectar")








