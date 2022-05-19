# coding=UTF-8
import os
import threading
import configparser
from os.path import dirname as updir
from time import sleep, time
directorio = updir(os.path.abspath(__file__))
UI_FILE = directorio+"/usuarios.glade"


class Ventana:

    def __init__(self, wifietecsa, _Gtk, _GLib, _builder):
        self.Gtk = _Gtk
        self.GLib = _GLib
        self._wifietecsa = wifietecsa
        self.builder = _builder
        # self.builder.connect_signals(self)
        self._window = self.builder.get_object('usuarios')
        self._window.connect("delete_event", self.ocultarVentana)
        self._listbox = self.builder.get_object('listbox')
        self._listbox.connect("row-activated", self.usuarioSeleccionado)
        self._row = []
        self._rowSeleccionado = None
        self._botonBorrar = self.builder.get_object('btBorrarCuenta')
        self._botonBorrar.connect("clicked", self.on_botonBorrar_clicked)
        self._nombreUsuarioEditar = self.builder.get_object('nombreUsuarioEditar')
        self._contrasenaUsuarioEditar = self.builder.get_object('contrasenaUsuarioEditar')
        self._botonPreAnadirUsuario = self.builder.get_object('btPreAnadirUsuario')
        self._botonPreAnadirUsuario.connect("clicked", self.on_pre_anadirUsuario)
        self._botonAnadirUsuario = self.builder.get_object('btAnadirUsuario')
        self._botonAnadirUsuario.connect("clicked", self.on_anadirUsuario)
        self._popoverAnadirUsuario = self.builder.get_object('popoverAnadirUsuario')
        self._usuarioNuevo = self.builder.get_object('usuarioNuevo')
        self._contrasenaNueva = self.builder.get_object('contrasenaNueva')
        self._botonGuardarEdicion = self.builder.get_object('btGuardarEdicion')
        self._botonGuardarEdicion.connect("clicked", self.modificarUsuario)
        self.nombre_usuario_seleccionado = None
        self._imagenCaptcha = self.builder.get_object('imagenCaptcha')
        self._botonRecargarCaptcha = self.builder.get_object("btRecargarCaptcha")
        self._botonRecargarCaptcha.connect("clicked", self.recargarCaptcha)
        self._textoCaptcha = self.builder.get_object('textoCaptcha')
        self._textoCaptcha.connect("key_press_event", self.aceptarCaptchaByKey)
        self._botonAceptarCaptcha = self.builder.get_object("btAceptarCaptcha")
        self._botonAceptarCaptcha.connect("clicked", self.aceptarCaptcha)
        self._boxEscribirCaptcha = self.builder.get_object("boxEscribirCaptcha")
        self._labelEstadoCaptcha = self.builder.get_object("lbEstadoCaptcha")
        self._usuarioTransferir = self.builder.get_object('usuarioTransferir')
        self._cantidadTransferir = self.builder.get_object('cantidadTransferir')
        self._numeroRecarga = self.builder.get_object('numeroRecarga')
        self._btRecargarCupon = self.builder.get_object('btRecargarCupon')
        self._btRecargarCupon.connect("clicked", self.on_botonRecargar_clicked)
        self.transferiendo = False
        self._lbEstadoTransferirSaldo = self.builder.get_object('lbEstadoTransferirSaldo')
        self._btEnviarSaldo = self.builder.get_object('btEnviarSaldo')
        self._btEnviarSaldo.connect("clicked", self.on_botonTransferir_clicked)
        self._lbEstadoRecargarSaldo = self.builder.get_object('lbEstadoRecargarSaldo')
        self._lbEstado = self.builder.get_object('lbEstado')
        self._horaSeg = None
        self._boxPanel = self.builder.get_object('boxPanel')
        self._boxOtrasOpciones = self.builder.get_object("boxOtrasOpciones")

        #-----Carga la lista de autocompletado
        self._autocompletado = self.builder.get_object('autocompetadoUsuarios')
        self._store = self.Gtk.ListStore(str)


        # self.actualizar()

    def mostrarVentana(self):
        self.actualizar()
        self._window.show_all()
        self._boxPanel.hide()
        self._boxOtrasOpciones.hide()
        # if self._row:
        #     self.usuarioSeleccionado(None, self._row[0])

    def actualizar_saldos(self, row):
        saldo = self._wifietecsa._raywifi.saldo(row._user, row._pwd)
        horas, minutos = saldo.split(":")[0:2]
        color = "darkgreen"
        minutos = int(minutos) + int(horas) * 60
        if minutos <= 5:
            color = "red"
        if minutos == 0:
            color = "black"
        row._labelSaldoMarkup = f'<b><span color=\"{color}\">{saldo}</span></b>'
        self.GLib.idle_add(row._labelSaldo.set_markup, row._labelSaldoMarkup)

    def actualizar_todos_saldos(self):
        for row in self._row:
            self.actualizar_saldos(row)

    def actualizar(self, gparam=None):
        self._config = configparser.ConfigParser()
        self._config.read(directorio+'/config.ini')
        for item in self._row:
            self._listbox.remove(item)    #tambien funciona bien.
            # item.destroy()
        self._row = []
        for key in self._config['USERS']:
            if key.count("user"):
                self.anadirUnoInterfaz(self._config['USERS'][key],
                                       self._config['USERS']["PASS"+key[4:]])
        #-----Carga la lista de autocompletado
        self._config = configparser.ConfigParser()
        self._config.read(directorio+'/config.ini')
        self._store.clear()
        for key in self._config['USERS']:
            if key.count("user"):
                self._store.append([self._config['USERS'][key]])
        self._autocompletado.set_model(self._store)
        self._autocompletado.set_text_column(0)

    def anadirUnoInterfaz(self, usuario, contrasena):
        self._row.append(self.Gtk.ListBoxRow())
        hbox = self.Gtk.Box(orientation=self.Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.show()
        self._row[-1].add(hbox)
        labelUsuario = self.Gtk.Label()
        labelUsuario.show()
        self._row[-1]._user = usuario
        self._row[-1]._pwd = contrasena
        self._row[-1]._labelSaldo = self.Gtk.Label()
        self._row[-1]._labelSaldo.show()
        self._row[-1]._labelSaldoMarkup = [""]
        threading.Thread(target=self.actualizar_saldos, args=(self._row[-1],)).start()
        labelUsuario.set_markup(f'<b><span color=\"{"navy" if usuario.count("com.cu") else "dodgerblue"}\">{usuario}</span></b>')
        hbox.pack_start(labelUsuario, True, True, 0)
        hbox.pack_start(self._row[-1]._labelSaldo, False, True, 0)
        self._listbox.add(self._row[-1])
        self._row[-1].show()

    def usuarioSeleccionado(self, lb, lbr):
        self._rowSeleccionado = lbr
        self.nombre_usuario_seleccionado = lbr._user
        self._nombreUsuarioEditar.set_text(lbr._user)
        self._contrasenaUsuarioEditar.set_text(lbr._pwd)
        self.GLib.idle_add(self._labelEstadoCaptcha.set_text, "Escriba el código captcha\npara más opciones")
        self.recargarCaptcha()
        self._boxPanel.show()
        self._boxEscribirCaptcha.show()
        self._boxOtrasOpciones.hide()
        if self._row:
            self._lbEstado.set_markup(lbr._labelSaldoMarkup)

    def recargarCaptcha(self, gparam=None):
        threading.Thread(target=self.cargarCaptcha, args=()).start()

    def cargarCaptcha(self):
        usuario = self._nombreUsuarioEditar.get_text()
        contrasena = self._contrasenaUsuarioEditar.get_text()
        mensaje = self._wifietecsa._raywifi.autentificarPortal(usuario, contrasena)
        # Reiniciar y bloquear opciones que dependen del captcha
        self._textoCaptcha.set_text("")
        # self._labelEstadoCaptcha.set_text("Escriba el código captcha \npara más opciones")
        if mensaje == "Error de conexión":
            self.GLib.idle_add(self._imagenCaptcha.set_from_icon_name, "error", 48)
            self.GLib.idle_add(self._labelEstadoCaptcha.set_markup, "<span color='red'> Error de conexión </span>")
            return
        sleep(0.7)
        self.GLib.idle_add(self._imagenCaptcha.set_from_file, directorio + '/imagenCaptcha.png')

    def aceptarCaptcha(self, gparam=None):
        [error, mensaje, saldo] = self._wifietecsa._raywifi.verificarCaptcha(self._textoCaptcha.get_text())
        if error == "Error de conexión":
            self._wifietecsa._labelEstado.set_text(mensaje)
            self._labelEstadoCaptcha.set_markup("<span color='red'>Texto captcha incorrecto\nintente nuevamente</span>")
            self.recargarCaptcha()
            return
        self._labelEstadoCaptcha.set_markup("<b><span color='green'>Texto captcha correcto</span></b>")
        self._imagenCaptcha.set_from_icon_name("dialog-ok", 48)
        self._textoCaptcha.set_text("")
        self._horaSeg = time()
        self._boxOtrasOpciones.show()
        self._boxEscribirCaptcha.hide()

    def aceptarCaptchaByKey(self, event_controller_key, key):
        if key.keyval == 65293:  # al presionar ENTER
            self.aceptarCaptcha()

    def on_botonTransferir_clicked(self, gparam):
        if not self.transferiendo:
            self.transferiendo = True
            threading.Thread(target=self.transferirSaldo, args=()).start()

    def transferirSaldo(self):
        usuario = self._nombreUsuarioEditar.get_text()
        contrasena = self._contrasenaUsuarioEditar.get_text()
        # try:
        mensaje, saldoActual = self._wifietecsa._raywifi.transferirSaldo(self._usuarioTransferir.get_text(),
                                                                         self._cantidadTransferir.get_text(),
                                                                         self._contrasenaUsuarioEditar.get_text())
        # except :
        self.transferiendo = False
        if "satisfactoriamente" in mensaje:
            self._lbEstadoTransferirSaldo.set_markup(f"<b><span color='green'>{mensaje}</span></b>")
            self._usuarioTransferir.set_text("")
            self._cantidadTransferir.set_text("")
        else:
            _mensaje = mensaje.replace('. ', '.\n')  # Hacer un salto de línea donde hay punto
            self._lbEstadoTransferirSaldo.set_markup(f"<b><span color='red'>{_mensaje}</span></b>")
        self.transferiendo = False
        self.GLib.idle_add(self._lbEstado.set_markup, f'<b><span color=\"goldenrod\">--:--:--</span></b>')
        saldo = self._wifietecsa._raywifi.saldo(usuario, contrasena)
        horas, minutos = saldo.split(":")[0:2]
        color = "darkgreen"
        minutos = int(minutos) + int(horas)*60
        if minutos <= 5:
            color = "red"
        if minutos == 0:
            color = "black"
        self.GLib.idle_add(self._lbEstado.set_markup, f'<b><span color=\"{color}\">{saldo}</span></b>')
        self.actualizar_todos_saldos()
        self.GLib.idle_add(self._lbEstado.set_markup, self._rowSeleccionado._labelSaldoMarkup)

    def on_botonRecargar_clicked(self, gparam):
        threading.Thread(target=self.recargarSaldo, args=()).start()

    def recargarSaldo(self):
        mensaje, saldoActual = self._wifietecsa._raywifi.recargarCuenta(self._numeroRecarga.get_text())
        self._lbEstadoRecargarSaldo.set_text(mensaje)
        if saldoActual:
            self._lbEstadoRecargarSaldo.set_text(saldoActual)

    def on_pre_anadirUsuario(self, gparam):
        self._popoverAnadirUsuario.popup()
        self._usuarioNuevo.set_text("")
        self._contrasenaNueva.set_text("")

    def on_anadirUsuario(self, gparam):
        self._popoverAnadirUsuario.popdown()
        self.anadirBorrarUsuario()
        self._boxPanel.hide()

    def modificarUsuario(self, gparam):
        self.anadirBorrarUsuario(soloBorrar=True,
                                 usuarioBorrar=self.nombre_usuario_seleccionado)
        self.nombre_usuario_seleccionado = ""
        self.anadirBorrarUsuario(anadirDeEdicion=True)

    def anadirBorrarUsuario(self,
                            gparam=None,
                            soloBorrar=False,
                            usuarioBorrar="",
                            anadirDeEdicion=False):
        config2 = configparser.ConfigParser()
        usuarios = {}
        a = 0
        self._config.read(directorio+'/config.ini')  # recargar el el fichero config
        for key in self._config['USERS']:
            if key.count("user"):
                usuarios[self._config['USERS']['USER'+str(a)]] = self._config['USERS']['PASS'+str(a)]
                a = a + 1
        if not soloBorrar:
            if anadirDeEdicion:
                nuevoUsuario = self._nombreUsuarioEditar.get_text()
                nuevaContrasena = self._contrasenaUsuarioEditar.get_text()
                self._nombreUsuarioEditar.set_text("")
                self._contrasenaUsuarioEditar.set_text("")
            else:
                nuevoUsuario = self._usuarioNuevo.get_text()
                nuevaContrasena = self._contrasenaNueva.get_text()
                self._usuarioNuevo.set_text("")
                self._contrasenaNueva.set_text("")
            usuarios[nuevoUsuario] = nuevaContrasena  # agrega el nuevo usuario que está en las cajas de texto
            self.anadirUnoInterfaz(nuevoUsuario, nuevaContrasena)
        else:
            del(usuarios[usuarioBorrar])
        a = 0
        datos = {}
        for usu, con in usuarios.items():
            datos['USER'+str(a)] = usu
            datos['PASS'+str(a)] = con
            a = a + 1
        config2['USERS'] = datos
        config2['SETTINGS'] = {"last_user_id": self._wifietecsa._comboUsuarios.get_active_id()}
        with open(directorio+'/config.ini', 'w') as configfile:
            config2.write(configfile)
        self._config.read(directorio+'/config.ini')
        self.actualizar()

    def on_botonBorrar_clicked(self, gparam):
        self.anadirBorrarUsuario(soloBorrar=True, usuarioBorrar=self._nombreUsuarioEditar.get_text())
        self._boxPanel.hide()
        self._boxOtrasOpciones.hide()
        self.actualizar()

    # def on_botonRecargar_clicked(self, gparam):
    #     mensaje, saldoActual = self._wifietecsa._raywifi.recargarCuenta(self._numeroRecarga.get_text())
    #     self._lbEstadoRecargarSaldo.set_text(mensaje)

    def ocultarVentana(self, *gparam):
        self._window.hide()
        return True


def main(argv):
    pass


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
