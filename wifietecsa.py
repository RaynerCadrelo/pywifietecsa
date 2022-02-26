# coding=UTF-8

import configparser
import os
import threading
import raywifietecsaclass
import usuarios
import captcha
import saldo
import __about__
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from os.path import dirname as updir

directorio = updir(os.path.abspath(__file__))
UI_FILE = directorio+"/ventana.glade"
os.environ["__version__"] = __about__.__version__

class WifiEtecsa:

    def __init__(self):
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
        self._cargandoConfig = False
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
            self._labelEstado.set_text(self._raywifi.login(usuario, contrasena))
            self._labelTiempo.set_text("")
            threading.Thread(target=self.actualizarSaldo, args=(usuario,contrasena, )).start()
            
    def actualizarSaldo(self, usuario, contrasena):
        saldo = self._raywifi.saldo(usuario, contrasena)
        horas, minutos = saldo.split(":")[0:2]
        color = "darkgreen"
        minutos = int(minutos) + int(horas)*60
        if minutos <= 5:
            color = "red"
        if minutos == 0:
            color = "black"
        GLib.idle_add(self._labelTiempo.set_markup, f'<b><span color=\"{color}\">{saldo}</span></b>')

    def on_botonTiempo_clicked(self, gparam):
        usuario = self._config['USERS']["USER"+self._comboUsuarios.get_active_id()]
        contrasena = self._config['USERS']["PASS"+self._comboUsuarios.get_active_id()]
        threading.Thread(target=self.actualizarSaldo, args=(usuario,contrasena, )).start()

    def on_botonEstado_clicked(self, gparam):
        estado = self._raywifi.status()
        if estado == "Conectado":
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
        
    def on_comboUsuarios_changed(self, gparam):
        if not self._cargandoConfig:
            self._config['SETTINGS']['last_user_id'] = self._comboUsuarios.get_active_id()
            with open(directorio+'/config.ini', 'w') as configfile:
                self._config.write(configfile)

    def on_window_destroy(self, window):
        self._config['SETTINGS']['last_user_id'] = self._comboUsuarios.get_active_id()
        with open(directorio+'/config.ini', 'w') as configfile:
            self._config.write(configfile)
        Gtk.main_quit()

    def cargarConfiguracion(self):
        self._cargandoConfig = True
        self._config = configparser.ConfigParser()
        self._config.read(directorio+'/config.ini')
        self._comboUsuarios.remove_all()
        for key in self._config['USERS']:
            if key.count("user"):
                self._comboUsuarios.append(key[4:], self._config["USERS"][key])
        self._comboUsuarios.set_active_id(self._config['SETTINGS']['last_user_id'])
        self._labelEstado.set_text(f'Actualización: {os.environ["__version__"]}')
        self._cargandoConfig = False


def main(argv):
    wifiEtecsa = WifiEtecsa()
    Gtk.main()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
