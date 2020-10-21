# coding=UTF-8


import configparser
import os
import raywifietecsaclass
import usuarios
import captcha
import saldo

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from os.path import dirname as updir

directorio = updir(os.path.abspath(__file__))
UI_FILE = directorio+"/ventana.glade"

class WifiEtecsa:

    def __init__(self):

        #print(UI_FILE)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        self._window = self.builder.get_object('window')
        self._window.show_all()

        self._loginLogout = self.builder.get_object('loginLogout')
        self._comboUsuarios = self.builder.get_object('comboUsuarios')
        self._labelEstado = self.builder.get_object('labelEstado')
        self._labelTiempo = self.builder.get_object('labelTiempo')
        self._botonTiempo = self.builder.get_object('botonTiempo')
        self._botonEstado = self.builder.get_object('botonEstado')
        self._imagenConexionInternetSi = self.builder.get_object('conexionInternetSi')
        self._imagenConexionInternetNo = self.builder.get_object('conexionInternetNo')


        self.cargarConfiguracion()

        self._raywifi = raywifietecsaclass.RayWifiEtecsa()

        self._saldo = ""



    def on_loginLogout_button_press_event(self, loginLogout, gparam):

        if loginLogout.get_active():
            cerrarSesion = self._raywifi.logout()
            self._labelEstado.set_text(cerrarSesion)
            self._labelTiempo.set_text("--:--:--")
        else:
            self._labelEstado.set_text("Iniciando...")
            usuario = self._config['USERS']["USER"+self._comboUsuarios.get_active_id()]
            contrasena = self._config['USERS']["PASS"+self._comboUsuarios.get_active_id()]
            self._labelEstado.set_text(self._raywifi.login(usuario,contrasena))
            self._labelTiempo.set_text("")

    def on_botonTiempo_clicked(self, gparam):
        usuario = self._config['USERS']["USER"+self._comboUsuarios.get_active_id()]
        contrasena = self._config['USERS']["PASS"+self._comboUsuarios.get_active_id()]
        self._labelTiempo.set_text(self._raywifi.saldo(usuario,contrasena))

    def on_botonEstado_clicked(self, gparam):
        estado = self._raywifi.status()
        if estado=="Conectado":
            self._botonEstado.set_image(self._imagenConexionInternetSi)
        else:
            self._botonEstado.set_image(self._imagenConexionInternetNo)
        self._labelEstado.set_text(estado)

    def on_botonUsuarios_clicked(self, gparam):
        self._ventanaUsuarios = usuarios.Ventana(self)
        self._window.hide()

    def on_botonSaldo_clicked(self, gparam):
        usuario = self._config['USERS']["USER"+self._comboUsuarios.get_active_id()]
        contrasena = self._config['USERS']["PASS"+self._comboUsuarios.get_active_id()]
        self._ventanaCaptcha = captcha.Ventana(self, usuario, contrasena)
        self._window.hide()

    def cargarVentanaSaldo(self):
        usuario = self._config['USERS']["USER"+self._comboUsuarios.get_active_id()]
        contrasena = self._config['USERS']["PASS"+self._comboUsuarios.get_active_id()]
        self._ventanaSaldo = saldo.Ventana(self, usuario, contrasena)
        self._window.hide()

    def mostrar(self):
        self._window.show_all()

    def on_window_destroy(self, window):
        Gtk.main_quit()




    def cargarConfiguracion(self):
        self._config = configparser.ConfigParser()
        self._config.read(directorio+'/config.ini')
        self._comboUsuarios.remove_all()
        for key in self._config['USERS']:
            if key.count("user"):
                self._comboUsuarios.append(key[4:], self._config['USERS'][key])
        self._comboUsuarios.set_active_id("1")
























def main(argv):

    wifiEtecsa = WifiEtecsa()
    Gtk.main()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
