# coding=UTF-8


import os
import configparser
import lxml.html
import requests

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


from os.path import dirname as updir

directorio = updir(os.path.abspath(__file__))
UI_FILE = directorio+"/saldo.glade"

class Ventana:

    def __init__(self, wifietecsa, usuario, contrasena):
        self._usuario = usuario
        self._contrasena = contrasena
        self._wifietecsa = wifietecsa
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('window')
        self.labelUsuario = self.builder.get_object('labelUsuario')
        self.labelSaldo = self.builder.get_object('labelSaldo')
        self.labelEstado = self.builder.get_object('labelEstado')
        self.numeroRecarga = self.builder.get_object('numeroRecarga')
        self.usuarioTransferir = self.builder.get_object('usuarioTransferir')
        self.cantidadTransferir = self.builder.get_object('cantidadTransferir')
        self.labelUsuario.set_text(usuario)
        self.labelSaldo.set_text(wifietecsa._saldo)

        #-----Carga la lista de autocompletado
        self.autocompletado = self.builder.get_object('autocompetadoUsuarios')
        self.store = Gtk.ListStore(str)
        self._config = configparser.ConfigParser()
        self._config.read(directorio+'/config.ini')
        self.store.clear()
        for key in self._config['USERS']:
            if key.count("user"):
                self.store.append([self._config['USERS'][key]])
        self.autocompletado.set_model(self.store)
        self.autocompletado.set_text_column(0)
        #----Muestra todos los componentes de la ventana
        self.window.show_all()

    def on_window_destroy(self, window):
        self._wifietecsa.cargarConfiguracion()
        self._wifietecsa.mostrar()

    def on_botonTransferir_clicked(self, gparam):
        try:
            x4 = requests.get("https://www.portal.nauta.cu/useraaa/transfer_balance", headers = {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/5.0 (X11; Linux x86_64)"}, stream=True, timeout=5, cookies = self._wifietecsa.cookies)
        except:
            self.labelEstado.set_text("Error de conexión")
        body4=x4.text
        elementosRecarga={}
        root_element4 = lxml.html.fromstring(body4)
        form4 = root_element4.xpath('//form')[0] # //form
        inputs4 = form4.inputs
        for a in inputs4:
            elementosRecarga[ a.name ] = a.value
        elementosRecarga["id_cuenta"] = self.usuarioTransferir.get_text()
        elementosRecarga["password_user"] = self._contrasena
        elementosRecarga["transfer"] = self.cantidadTransferir.get_text()
        elementosRecarga["action"] = "checkdata"

        try:
            x5 = requests.post("https://www.portal.nauta.cu/useraaa/transfer_balance", data=elementosRecarga, headers = {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/40.0 (X11; Linux x86_64)"}, stream=True, timeout=5, cookies = self._wifietecsa.cookies)
        except:
            self.labelEstado.set_text("Error de conexión")
        body5=x5.text
        if body5.count("msg_error"):
            mensaje_error=body5.split('"msg_error">')[1].split("<")[0]
            self.labelEstado.set_text(mensaje_error)
        elif body5.count('"msg_message">'):
            mensaje_mensaje=body5.split('"msg_message">')[1].split("<")[0]
            self.labelEstado.set_text(mensaje_mensaje)
        else:
            self.labelEstado.set_text("Error desconocido")
        root_element5 = lxml.html.fromstring(body5)
        saldo = root_element5.xpath('//div[@class="card-panel"]/div/div/p')[0] # //form
        self.labelSaldo.set_text(saldo.text_content())

    def on_botonRecargar_clicked(self, gparam):
        try:
            x4 = requests.get("https://www.portal.nauta.cu/useraaa/recharge_account", headers = {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/5.0 (X11; Linux x86_64)"}, stream=True, timeout=5, cookies = self._wifietecsa.cookies)
        except:
            self.labelEstado.set_text("Error de conexión")
        body4=x4.text
        elementosRecarga={}
        root_element4 = lxml.html.fromstring(body4)
        form4 = root_element4.xpath('//form')[0] # //form
        inputs4 = form4.inputs
        for a in inputs4:
            elementosRecarga[ a.name ] = a.value
        elementosRecarga["recharge_code"] = self.numeroRecarga.get_text()
        elementosRecarga["btn_submit"]="" # si no se pone no procede en el post

        x5 = requests.post("https://www.portal.nauta.cu/useraaa/recharge_account", data=elementosRecarga, headers = {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/40.0 (X11; Linux x86_64)"}, stream=True, timeout=5, cookies = self._wifietecsa.cookies)
        body5=x5.text
        if body5.count("msg_error"):
            mensaje_error=body5.split('"msg_error">')[1].split("<")[0]
            self.labelEstado.set_text(mensaje_error)
        elif body5.count('"msg_message">'):
            mensaje_mensaje=body5.split('"msg_message">')[1].split("<")[0]
            self.labelEstado.set_text(mensaje_mensaje)
        else:
            self.labelEstado.set_text("Error desconocido")



def main(argv):

    ventana = Ventana()
    Gtk.main()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
