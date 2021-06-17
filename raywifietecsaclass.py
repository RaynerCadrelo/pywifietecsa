# coding=UTF-8

import requests
import lxml.html
import time
import configparser

import os
directorio = os.path.dirname(os.path.abspath(__file__))

class RayWifiEtecsa:

    def __init__(self):

        self._configDataLogin = configparser.ConfigParser()
        self._configDataLogin.read(directorio+'/.datalogin')

        self._linkInicio = "https://www.portal.nauta.cu/user/login/es-es"
        self._linkTransferir = "https://www.portal.nauta.cu/useraaa/transfer_balance"
        self._linkRecargar = "https://www.portal.nauta.cu/useraaa/recharge_account"

        self._headers =  {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/5.0 (X11; Linux x86_64)"}




    def status(self): # retorna "Desconectado" / "Conectado"
        try:
            self._x=requests.get("http://www.cubadebate.cu/")
        except:
            return("Desconectado")
        if self._x.text.count("Cubadebate"):
            return("Conectado")
        else:
            return("Desconectado")





    def saldo(self, username, password):
        try:
            x1=requests.get("https://secure.etecsa.net:8443")
        except:
            return("Error de conexión")
        body=x1.text
        elementForm={}
        root_element = lxml.html.fromstring(body)
        form = root_element.xpath('/html/body/div/div/div/div/form')[0]
        inputs = form.inputs
        for a in inputs:
            elementForm[ a.name ] = a.value
        elementForm['username'] = username
        elementForm['password'] = password
        try:
            self._x=requests.post("https://secure.etecsa.net:8443/EtecsaQueryServlet", data=elementForm, headers = {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/40.0 (X11; Linux x86_64)"}, timeout=5, cookies=x1.cookies)
        except:
            return("Error de conexión")
        if self._x.text.count("Crédito:"):
            dinero_str = lxml.html.fromstring(self._x.text).xpath('//table[@id="sessioninfo"]/tbody/tr[2]/td[2]/text()')[0].replace('\n','').replace('\t','').replace('\r','')
            print(dinero_str)
            dinero_float = float(dinero_str.split(" ")[0])*100 #dinero en centavos
            if username.split("@")[1] == "nauta.com.cu":   #calculo para la navegación internación de 0.70 cuc la hora
                hora = int((dinero_float*6/175)/60)
                minuto = int((dinero_float*6/175)%60)
                segundo = int(((dinero_float*6/175)*100-int(dinero_float*6/175)*100)*0.6)
            else:  #cálculo para la navegación nacional
                hora = int((dinero_float*6/25)/60)
                minuto = int((dinero_float*6/25)%60)
                segundo = int(((dinero_float*6/25)*100-int(dinero_float*6/25)*100)*0.6)

            if hora<10:
                hora_str = "0" + str(hora)
            else:
                hora_str = str(hora)
            if minuto<10:
                minuto_str = "0" + str(minuto)
            else:
                minuto_str = str(minuto)
            if segundo<10:
                segundo_str = "0" + str(segundo)
            else:
                segundo_str = str(segundo)
            tiempo_str = hora_str + ":"+minuto_str + ":" + segundo_str #tiempo en el formato 1:59:59
            return( tiempo_str +"  ("+dinero_str+") ")
        return("Usuarios o Contraseña\nincorrecto")




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












    def autentificarPortal(self, usuario, contrasena):
        try:
            x1=requests.get(self._linkInicio, headers=self._headers, stream=True, timeout=5)
        except:
            return("Error de conexión")
        self._elementosFormAutentificar={}
        root_element = lxml.html.fromstring(x1.text)
        try:
            form = root_element.xpath('/html/body/div/div/form')[0] # //form
        except:
            return("Error de conexión")
        inputs = form.inputs
        for a in inputs:
            self._elementosFormAutentificar[ a.name ] = a.value
        del self._elementosFormAutentificar[None]
        self._elementosFormAutentificar["btn_submit"]=""
        self._elementosFormAutentificar["login_user"]=usuario
        self._elementosFormAutentificar["password_user"]=contrasena

        self._cookies = x1.cookies

        ## Cargar imagen captcha
        imagen =requests.get("https://www.portal.nauta.cu/captcha/?"+str(int(time.time()*1000)), headers=self._headers, stream=True, timeout=5, cookies=self._cookies)

        #### Guardar imagen captcha
        with open(directorio + '/imagenCaptcha.png', 'wb') as img_file:
            img_file.write(imagen.content)
        return("")








    def verificarCaptcha(self, codigoCaptcha):
        self._elementosFormAutentificar["captcha"] = codigoCaptcha
        saldo = ""
        try:
            x3=requests.post(self._linkInicio, data=self._elementosFormAutentificar, headers = self._headers, cookies=self._cookies, stream=True)
        except:
            return(["Error de conexión","Problemas de conexión", saldo])
        root_element = lxml.html.fromstring(x3.text)
        try:
            elementoSaldo = root_element.xpath('//div[@class="z-depth-1 card-panel"]/div/div/div[5]/div/p')[0]
        except:
            saldo = "--,--"

        if not saldo == "--,--":
            saldo = elementoSaldo.text_content()

        if x3.text.count('"msg_error">'):
            mensaje_error=x3.text.split('"msg_error">')[1].split("<")[0]
            return(["Error de conexión", mensaje_error, saldo])
        return(["Autentificado", "", saldo])







    #return([ mensaje, saldo_actual ])
    def transferirSaldo(self, usuarioRecibir, cantidadRecibir):
        try:
            x4 = requests.get(self._linkTransferir, headers = self._headers, stream=True, timeout=5, cookies = self._cookies)
        except:
            return(["Error de conexión", ""])
        body4=x4.text
        elementosRecarga={}
        root_element4 = lxml.html.fromstring(body4)
        form4 = root_element4.xpath('//form')[0] # //form
        inputs4 = form4.inputs
        for a in inputs4:
            elementosRecarga[ a.name ] = a.value
        elementosRecarga["id_cuenta"] = usuarioRecibir
        elementosRecarga["password_user"] = self._portalContrasena
        elementosRecarga["transfer"] = cantidadRecibir
        elementosRecarga["action"] = "checkdata"

        try:
            x5 = requests.post(self._linkTransferir, data=elementosRecarga, headers = self._headers, stream=True, timeout=5, cookies = self._cookies)
        except:
            return(["Error de conexión", ""])
        body5=x5.text
        root_element5 = lxml.html.fromstring(body5)
        saldo = root_element5.xpath('//div[@class="card-panel"]/div/div/p')[0] # //form
        saldo_str = saldo.text_content()
        if body5.count("msg_error"):
            mensaje_error=body5.split('"msg_error">')[1].split("<")[0]
            return(mensaje_error,saldo_str)
        elif body5.count('"msg_message">'):
            mensaje_mensaje=body5.split('"msg_message">')[1].split("<")[0]
            return(mensaje_mensaje,saldo_str)
        else:
            return("Error desconocido","")








    def recargarCuenta(self, codigoCupon):
        try:
            x4 = requests.get(self._linkRecargar, headers = self._headers, stream=True, timeout=5, cookies = self._cookies)
        except:
            return("Error de conexión","")
        body4=x4.text
        elementosRecarga={}
        root_element4 = lxml.html.fromstring(body4)
        form4 = root_element4.xpath('//form')[0] # //form
        inputs4 = form4.inputs
        for a in inputs4:
            elementosRecarga[ a.name ] = a.value
        elementosRecarga["recharge_code"] = codigoCupon
        elementosRecarga["btn_submit"]="" # si no se pone no procede en el post

        x5 = requests.post(self._linkRecargar, data=elementosRecarga, headers = self._headers, stream=True, timeout=5, cookies = self._cookies)
        body5=x5.text
        if body5.count("msg_error"):
            mensaje_error=body5.split('"msg_error">')[1].split("<")[0]
            return(mensaje_error,"")
        elif body5.count('"msg_message">'):
            mensaje_mensaje=body5.split('"msg_message">')[1].split("<")[0]
            return(mensaje_mensaje,"")
        else:
            return("Error desconocido","")





