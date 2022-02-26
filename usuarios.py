# coding=UTF-8


import os
import threading

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

import configparser


from os.path import dirname as updir

directorio = updir(os.path.abspath(__file__))
UI_FILE = directorio+"/usuarios.glade"

class Ventana:

    def __init__(self,wifietecsa):
        self._wifietecsa = wifietecsa
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        self._window = self.builder.get_object('window')
        self._listbox = self.builder.get_object('listbox')
        self._row=[]
        
        self._usuarioNuevo = self.builder.get_object('usuario')
        self._contrasenaNuevo = self.builder.get_object('contrasena')

        self._proximoUsuarioBorrar=""        
        self.actualizar()

    def actualizar_saldos(self, labelSaldo, usuario, contrasena):
        saldo = self._wifietecsa._raywifi.saldo(usuario, contrasena)
        horas, minutos = saldo.split(":")[0:2]
        color = "darkgreen"
        minutos = int(minutos) + int(horas)*60
        if minutos <= 5:
            color = "red"
        if minutos == 0:
            color = "black"
        GLib.idle_add(labelSaldo.set_markup, f'<b><span color=\"{color}\">{saldo}</span></b>')

    def actualizar(self):
        self._config = configparser.ConfigParser()
        self._config.read(directorio+'/config.ini')
        for item in self._row:
            self._listbox.remove(item)    #tambien funciona bien.
            #item.destroy()
        self._row=[]
        a=0;
        for key in self._config['USERS']:
            if key.count("user"):
                self._row.append(Gtk.ListBoxRow())
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self._row[a].add(hbox)
                labelUsuario = Gtk.Label()
                labelVencimiento = Gtk.Label()
                labelSaldo = Gtk.Label()
                threading.Thread(target=self.actualizar_saldos, args=(labelSaldo,self._config['USERS'][key], self._config['USERS'][ "PASS"+key[4:]])).start()
                usuario = self._config['USERS'][key]
                labelUsuario.set_markup(f'<b><span color=\"{"navy" if usuario.count("com.cu") else "dodgerblue"}\">{usuario}</span></b>')
                hbox.pack_start(labelUsuario, True, True, 0)
                hbox.pack_start(labelSaldo, False, True, 0)
                botonBorrar=Gtk.Button()
                botonBorrar.connect("clicked", self.on_botonBorrar_clicked,self._config['USERS'][key])
                botonEditar=Gtk.Button()
                botonEditar.connect("clicked", self.on_botonEditar_clicked, self._config['USERS'][key], self._config['USERS'][ "PASS"+key[4:]])
                imagenBotonBorrar=Gtk.Image()
                imagenBotonEditar=Gtk.Image()
                imagenBotonBorrar.set_from_file(directorio+"/imagenes/user-trash-symbolic.symbolic.png")
                imagenBotonEditar.set_from_file(directorio+"/imagenes/text-editor-symbolic.symbolic.png")
                botonBorrar.set_image(imagenBotonBorrar)
                botonEditar.set_image(imagenBotonEditar)
                hbox.pack_start(botonBorrar, False, True, 0)
                hbox.pack_start(botonEditar, False, True, 0)                
                self._listbox.add(self._row[a])
                a=a+1
        self._window.show_all()
        
        

    def on_botonAnadirUsuario_clicked(self, gparam=None, soloBorrar=False):        
        config2 = configparser.ConfigParser()
        usuarios = {}
        a=0;
        for key in self._config['USERS']:
            if key.count("user"):
                usuarios[self._config['USERS']['USER'+str(a)]] = self._config['USERS']['PASS'+str(a)]
                a=a+1
        if self._proximoUsuarioBorrar in usuarios:
            del(usuarios[self._proximoUsuarioBorrar])
            self._proximoUsuarioBorrar = ""
        if not soloBorrar:
            usuarios[self._usuarioNuevo.get_text()] = self._contrasenaNuevo.get_text() #agrega el nuevo usuario que está en las cajas de texto
        
        a=0
        datos={}
        for usu, con in usuarios.items():
            datos['USER'+str(a)] = usu
            datos['PASS'+str(a)] = con
            a=a+1
        config2['USERS']=datos
        config2['SETTINGS'] = {"last_user_id": self._wifietecsa._comboUsuarios.get_active_id()}
        with open(directorio+'/config.ini', 'w') as configfile:
            config2.write(configfile)      
        self._usuarioNuevo.set_text("")
        self._contrasenaNuevo.set_text("")  
        self.actualizar()


    def on_botonEditar_clicked(self,gparam, usuario, contrasena):
        self._proximoUsuarioBorrar = usuario
        self._usuarioNuevo.set_text(usuario)
        self._contrasenaNuevo.set_text(contrasena)

    def on_botonBorrar_clicked(self,gparam,usuario):
        self._proximoUsuarioBorrar = usuario
        self.on_botonAnadirUsuario_clicked(soloBorrar=True)
    
        

    def on_window_destroy(self, window):
        self._wifietecsa.cargarConfiguracion()
        self._wifietecsa.mostrar()
        #Gtk.main_quit()


def main(argv):

    ventana = Ventana()
    Gtk.main()
        

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
