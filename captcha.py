# coding=UTF-8


import os

import lxml.html
import requests
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


from os.path import dirname as updir

directorio = updir(os.path.abspath(__file__))
UI_FILE = directorio+"/captcha.glade"

class Ventana:

    def __init__(self, wifietecsa, usuario, contrasena):
        self._wifietecsa = wifietecsa
        self._captchaCorrecto = False
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('window')
        self.imagenGtk = self.builder.get_object('imagenCaptcha')
        self.textoGtk = self.builder.get_object('textoCaptcha')

        self.window.show_all()

        headers={'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/5.0 (X11; Linux x86_64)"}
        try:
            self._x1=requests.get("https://www.portal.nauta.cu/user/login/es-es", headers=headers, stream=True, timeout=5)
        except:
            self._wifietecsa._labelEstado.set_text("Error de conexión")
            self.window.close()
            return
        self._elementosFormAutentificar={}
        root_element = lxml.html.fromstring(self._x1.text)
        try:
            form = root_element.xpath('/html/body/div/div/form')[0] # //form
        except:
            self.window.close()
        inputs = form.inputs
        for a in inputs:
            self._elementosFormAutentificar[ a.name ] = a.value
        del self._elementosFormAutentificar[None]
        self._elementosFormAutentificar["btn_submit"]=""
        self._elementosFormAutentificar["login_user"]=usuario
        self._elementosFormAutentificar["password_user"]=contrasena

        self._wifietecsa.cookies = self._x1.cookies

        ## Cargar imagen captcha
        imagen =requests.get("https://www.portal.nauta.cu/captcha/?"+str(int(time.time()*1000)), headers=headers, stream=True, timeout=5, cookies=self._x1.cookies)

        #### Guardar imagen captcha
        with open(directorio + '/imagenCaptcha.png', 'wb') as img_file:
            img_file.write(imagen.content)
        self.imagenGtk.set_from_file(directorio + '/imagenCaptcha.png')


    def on_botonAceptarCaptcha_clicked(self, gparam):
        self._elementosFormAutentificar["captcha"]=self.textoGtk.get_text()
        try:
            x3=requests.post("https://www.portal.nauta.cu/user/login/es-es", data=self._elementosFormAutentificar, headers = {'content-type': 'application/x-www-form-urlencoded', "User-agent":"Mozilla/5.0 (X11; Linux x86_64)"}, cookies=self._x1.cookies, stream=True)
        except:
            print("Error de conexión")
            self.window.close()
        root_element = lxml.html.fromstring(x3.text)
        try:
            elementoSaldo = root_element.xpath('//div[@class="z-depth-1 card-panel"]/div/div/div[5]/div/p')[0]
        except:
            self.window.close()
        self._wifietecsa._saldo = elementoSaldo.text_content()

        if x3.text.count('"msg_error">'):
            mensaje_error=x3.text.split('"msg_error">')[1].split("<")[0]
            print(mensaje_error)
            self.window.close()
        #print(x3.text)
        self._captchaCorrecto = True
        self._wifietecsa.cargarVentanaSaldo()
        self.window.close()

    def on_textoCaptcha_key_press_event(self,event_controller_key, key):
        if key.keyval==65293:
            self.on_botonAceptarCaptcha_clicked(None)


    def on_window_destroy(self, window):
        if not self._captchaCorrecto:
            self._wifietecsa.cargarConfiguracion()
            self._wifietecsa.mostrar()


def main(argv):

    ventana = Ventana()
    Gtk.main()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
