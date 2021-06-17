# coding=UTF-8


import os
import configparser
import raywifietecsaclass

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
        # ----Muestra todos los componentes de la ventana
        self.window.show_all()

        self._rayWifiEtecsa = wifietecsa._raywifi

    def on_window_destroy(self, window):
        self._wifietecsa.cargarConfiguracion()
        self._wifietecsa.mostrar()

    def on_botonTransferir_clicked(self, gparam):
        mensaje, saldoActual =  self._rayWifiEtecsa.transferirSaldo(self.usuarioTransferir.get_text(), self.cantidadTransferir.get_text())
        self.labelEstado.set_text(mensaje)
        if saldoActual:
            self.labelSaldo.set_text(saldoActual)

    def on_botonRecargar_clicked(self, gparam):
        mensaje, saldoActual = self._rayWifiEtecsa.recargarCuenta(self.numeroRecarga.get_text())
        self.labelEstado.set_text(mensaje)
        if saldoActual:
            self.labelSaldo.set_text(saldoActual)




def main(argv):

    ventana = Ventana()
    Gtk.main()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
