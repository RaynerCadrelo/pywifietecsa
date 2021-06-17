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
        wifietecsa._raywifi._portalContrasena = contrasena

        self.window.show_all()
        mensaje = self._wifietecsa._raywifi.autentificarPortal(usuario, contrasena)
        if mensaje == "Error de conexión":
            self._wifietecsa._labelEstado.set_text("Error de conexión")
            self.window.close()
            return

        self.imagenGtk.set_from_file(directorio + '/imagenCaptcha.png')


    def on_botonAceptarCaptcha_clicked(self, gparam):
        [error, mensaje, saldo] = self._wifietecsa._raywifi.verificarCaptcha(self.textoGtk.get_text())
        if error == "Error de conexión":
            self._wifietecsa._labelEstado.set_text(mensaje)
            print("cerrado por errores")
            self.window.close()
            return
        print("vamos a carcar ventana saldo")
        self._wifietecsa._saldo = saldo
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
