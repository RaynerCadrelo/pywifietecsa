# coding=UTF-8

import requests
import configparser
import os

directorio = os.path.dirname(os.path.abspath(__file__))

def main(argv):
    if len(argv)<2:
        print("Uso:")
        print("raywifietecsa ")
        print("               login")
        print("               logout")
        print("               login-logout")
        print("               time")
        print("               status")
        print("Ejemplos:")
        print("raywifietecsa login 1   'Inicia sesión el usuario número 1, ver el archivo de configuración config.ini'")
        print("raywifietecsa logout    'Cierra la sesión abierta'")
        print("raywifietecsa time      'Muestra el tiempo restante de la cuenta abierta'")
        print("raywifietecsa status    'Muestra el estado de conexión'")
        return
    action=argv[1]
    numberUser=1
    if len(argv)==3:
        numberUser=argv[2]
    
        

    config = configparser.ConfigParser()
    config.read(directorio+'/config.ini')

    configDataLogin = configparser.ConfigParser()
    configDataLogin.read(directorio+'/.datalogin')
    

    ######################################################
    #                   ESTADO                           #

    if action=="status":
        try:
            x=requests.get("http://www.cubadebate.cu/")
        except:
            print("Desconectado")
            return   
        if x.text.count("Cubadebate"):
            print("Conectado")
        else:            
            print("Desconectado")

    ######################################################
    #                   CONECTAR                         #
    if action=="login" or action=="login-logout":
        try:
            x=requests.get("https://secure.etecsa.net:8443")
        except:
            print("Error de conexión")
            return
        body=x.text
        body2=body.replace('\t','')
        body2=body2.split('<form')[2]
        lines=body2.split('\r\n')
        elementForm={}
        nombre=""
        for line in lines:
            if line.count("<input"):
                for element in line.split(" "):
                    if element.count("name="):
                        nombre = element[5:].replace('"','')
                    if element.count("value="):
                        elementForm[nombre]=element[6:].replace('/>','').replace('"','')
                        
        elementForm['username'] = config['USERS']['USER'+numberUser]
        elementForm['password'] = config['USERS']['PASS'+numberUser]
        
        try:    
            x=requests.post("https://secure.etecsa.net:8443//LoginServlet", data=elementForm, headers = {'content-type': 'application/x-www-form-urlencoded'})
        except:
            print("Error de conexión")
            return

        if x.status_code==200:
            if x.text.count("Su tarjeta no tiene saldo disponible"):
                print("Su tarjeta no tiene saldo disponible")
                return
            if x.text.count("No se pudo autorizar al usuario"):
                print("No se pudo autorizar al usuario")
                return
            if x.text.count("Usted está conectado"):
                print("Usted está conectado")
                
        else:
            print("servidor no responde")

        body=x.text
        body2=body.split("ATTRIBUTE_UUID")[1].split("&remove=")[0].replace("+","").replace(" ","").replace("\r\n","").replace('"',"")
        urlParam = "ATTRIBUTE_UUID"+body2+"&remove=1"

        configDataLogin['DATA_LOGIN']={'DATA': urlParam}
        with open(directorio+'/.datalogin', 'w') as configfile:
            configDataLogin.write(configfile)



#######################################################
#########      TIEMPO DISPONIBLE    ###################
    if action=="time" or action=="login" or action=="login-logout":
        try:
            urlParam = configDataLogin['DATA_LOGIN']['DATA']
            x=requests.post("https://secure.etecsa.net:8443/EtecsaQueryServlet", data="op=getLeftTime&"+urlParam, headers = {'content-type': 'application/x-www-form-urlencoded'})
        except:
            print("Error de conexión")
        print("Tiempo disponible " + x.text)


#######################################################
###########      DESCONECTAR           ################
    if action=="logout" or action=="login-logout":
        intentar=True
        while(intentar):
            if action=="login-logout":
                input("Presione ENTER para desconectar ")
            intentar=False

            try:
                urlParam = configDataLogin['DATA_LOGIN']['DATA']
                x=requests.post("https://secure.etecsa.net:8443//LogoutServlet", data=urlParam, headers = {'content-type': 'application/x-www-form-urlencoded'})
            except:
                print("Error de conexión")
                intentar=True

        if x.status_code==200:
            if x.text.count("SUCCESS"): #retorna esto: "logoutcallback('SUCCESS');"
                print("Cerrado con éxito")
            else:
                print("Error al desconectar")
########################################################
    






if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
