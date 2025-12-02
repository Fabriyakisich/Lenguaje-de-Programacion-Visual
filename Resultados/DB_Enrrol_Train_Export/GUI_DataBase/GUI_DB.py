import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# Asegurar que la raíz del proyecto esté en sys.path para poder importar el paquete
# `FRT` cuando se ejecuta este archivo directamente (p. ej. python GUI_DataBase/GUI_DB.py)
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

try:
    # When executed as a module: python -m GUI_DataBase.GUI_DB
    from .Data_Base import (
        crear_base_de_datos,
        mostrar_personas,
        insertar_persona,
        insertar_persona_con_id,
        obtener_siguiente_id,
        editar_persona,
        eliminar_persona,
        buscar_personas,
        persona_existe,
    )
except Exception:
    # When executed as a script: python GUI_DataBase/GUI_DB.py
    from Data_Base import (
        crear_base_de_datos,
        mostrar_personas,
        insertar_persona,
        insertar_persona_con_id,
        obtener_siguiente_id,
        editar_persona,
        eliminar_persona,
        buscar_personas,
        persona_existe,
    )
from threading import Thread
from tkinter import Toplevel, Label
from FRT.enrolar_persona import enroll_person
from FRT.entrenar_modelo import train_model
from config import FACES_DIR
import shutil


class PersonasGUI:
    """Interfaz reorganizada y con colores usando ttk.Treeview."""
    def __init__(self, root):
        self.root = root
        root.title("Gestión de Personas — Color & Layout Mejorados")
        root.geometry("920x560")
        root.configure(bg="#f4f7fb")

        crear_base_de_datos()

        # Estilos
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#2B7A78', foreground='white')
        style.map('TButton', foreground=[('active', 'white')])

        # Top header
        header = tk.Frame(root, bg="#7410D1", height=60)
        header.pack(fill='x')
        tk.Label(header, text='Sistema de Gestión de Personas', bg='#7410D1', fg='white', font=('Segoe UI', 14, 'bold')).pack(padx=20, pady=12, anchor='w')

        main = tk.Frame(root, bg='#f4f7fb')
        main.pack(fill='both', expand=True, padx=12, pady=12)

        # Left: Formulario
        left = tk.Frame(main, bg='#ffffff', bd=1, relief='solid')
        left.pack(side='left', fill='y', padx=(0,10), ipadx=8, ipady=8)

        tk.Label(left, text='Formulario', bg='#ffffff', font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, columnspan=2, pady=(6,12))

        tk.Label(left, text='Nombre:', bg='#ffffff').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.entry_nombre = tk.Entry(left, width=28, font=('Segoe UI', 10))
        self.entry_nombre.grid(row=1, column=1, padx=6, pady=6)

        tk.Label(left, text='Cédula:', bg='#ffffff').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.entry_cedula = tk.Entry(left, width=28, font=('Segoe UI', 10))
        self.entry_cedula.grid(row=2, column=1, padx=6, pady=6)

        tk.Label(left, text='Cargo:', bg='#ffffff').grid(row=3, column=0, sticky='e', padx=6, pady=6)
        self.entry_cargo = tk.Entry(left, width=28, font=('Segoe UI', 10))
        self.entry_cargo.grid(row=3, column=1, padx=6, pady=6)

        btn_frame = tk.Frame(left, bg='#ffffff')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12,6))

        self.btn_add = tk.Button(btn_frame, text='Agregar', bg='#2B7A78', fg='white', width=10, command=self.agregar)
        self.btn_add.grid(row=0, column=0, padx=6)

        self.btn_edit = tk.Button(btn_frame, text='Guardar cambios', bg='#D3D3D3', fg='gray', width=15, command=self.editar, state='disabled')
        self.btn_edit.grid(row=0, column=1, padx=6)

        self.btn_delete = tk.Button(btn_frame, text='Eliminar', bg='#D90429', fg='white', width=10, command=self.eliminar)
        self.btn_delete.grid(row=0, column=2, padx=6)

        self.btn_clear = tk.Button(btn_frame, text='Limpiar', bg='#6C757D', fg='white', width=10, command=self.clear_form)
        self.btn_clear.grid(row=0, column=3, padx=6)

        # Right: Tabla y búsqueda
        right = tk.Frame(main, bg='#f4f7fb')
        right.pack(side='left', fill='both', expand=True)

        search_frame = tk.Frame(right, bg='#f4f7fb')
        search_frame.pack(fill='x', pady=(0,8))

        tk.Label(search_frame, text='Buscar:', bg='#f4f7fb').pack(side='left', padx=(6,4))
        self.entry_buscar = tk.Entry(search_frame, width=30, font=('Segoe UI', 10))
        self.entry_buscar.pack(side='left', padx=4)
        tk.Button(search_frame, text='Buscar', bg='#0077B6', fg='white', command=self.buscar).pack(side='left', padx=6)
        tk.Button(search_frame, text='Refrescar', bg='#2B7A78', fg='white', command=self.refrescar).pack(side='left', padx=6)

        # Treeview
        columns = ('id', 'nombre', 'cedula', 'cargo', 'hora')
        self.tree = ttk.Treeview(right, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('id', text='ID')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('cedula', text='Cédula')
        self.tree.heading('cargo', text='Cargo')
        self.tree.heading('hora', text='Últ. ingreso')

        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nombre', width=220)
        self.tree.column('cedula', width=120, anchor='center')
        self.tree.column('cargo', width=160)
        self.tree.column('hora', width=130, anchor='center')

        vsb = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='left', fill='y')

        # estilos de filas alternas
        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('even', background='#f0f6f5')

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        self.selected_id = None

        self.refrescar()

    def refrescar(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        personas = mostrar_personas()
        for i, p in enumerate(personas):
            tag = 'even' if i % 2 == 0 else 'odd'
            id_, nombre, cedula, ultima, cargo = p
            hora_text = ultima if ultima else '-'
            self.tree.insert('', 'end', iid=str(id_), values=(id_, nombre, cedula, cargo, hora_text), tags=(tag,))

    def agregar(self):
        nombre = self.entry_nombre.get().strip()
        cedula = self.entry_cedula.get().strip()
        cargo = self.entry_cargo.get().strip()
        # Validaciones
        if not (nombre and cedula and cargo):
            messagebox.showwarning('Advertencia', 'Complete todos los campos antes de agregar.')
            return

        if not re.fullmatch(r"\d{6,7}", cedula):
            messagebox.showwarning('Advertencia', 'La cédula debe contener solo números y tener entre 6 y 7 dígitos.')
            return

        if re.search(r"\d", nombre):
            messagebox.showwarning('Advertencia', 'El nombre no puede contener números.')
            return

        if re.search(r"\d", cargo):
            messagebox.showwarning('Advertencia', 'El cargo no puede contener números.')
            return

        # Verificar duplicados
        if persona_existe(nombre, cedula):
            messagebox.showwarning('Advertencia', 'Ya existe una persona con esa cédula o los mismos datos.')
            return

        # Obtener siguiente id disponible (sin insertar aún)
        next_id = obtener_siguiente_id()

        # Mostrar diálogo de progreso sencillo
        progress_win = Toplevel(self.root)
        progress_win.title('Progreso: Enrolando y entrenando')
        progress_win.geometry('360x80')
        lbl = Label(progress_win, text='Iniciando...')
        lbl.pack(padx=12, pady=12)
        progress_win.transient(self.root)
        progress_win.grab_set()

        # Deshabilitar botones principales mientras se hace el proceso
        self.btn_add.config(state='disabled')
        self.btn_edit.config(state='disabled')
        self.btn_delete.config(state='disabled')

        def progress_cb(pct, msg):
            # Este callback puede ser llamado desde el hilo de enrolamiento
            def _upd():
                lbl.config(text=f"{msg} ({pct}%)")
            self.root.after(0, _upd)

        def _rmtree_folder(path):
            try:
                p = Path(path)
                if p.exists() and p.is_dir():
                    for f in p.iterdir():
                        try:
                            if f.is_file():
                                f.unlink()
                            elif f.is_dir():
                                # recursive
                                import shutil
                                shutil.rmtree(f)
                        except Exception:
                            pass
                    try:
                        p.rmdir()
                    except Exception:
                        pass
            except Exception:
                pass


        def worker():
            try:
                # 1) Enrolar: abrir cámara y capturar muestras en FACES_DIR/{next_id}
                ok, emsg, taken = enroll_person(str(next_id), nombre, progress_cb=progress_cb)
                if not ok:
                    # cleanup carpeta parcial
                    _rmtree_folder(Path(__file__).resolve().parents[1] / 'faces' / str(next_id))
                    raise RuntimeError(f"Enrolamiento falló: {emsg}")

                # Verificar número mínimo de muestras
                min_required = 20
                if taken < min_required:
                    # eliminar muestras parciales
                    _rmtree_folder(Path(__file__).resolve().parents[1] / 'faces' / str(next_id))
                    raise RuntimeError(f"Enrolamiento incompleto: solo se capturaron {taken} imágenes (mínimo {min_required}).")

                # 2) Entrenar el modelo con las nuevas imágenes
                self.root.after(0, lambda: lbl.config(text='Entrenando modelo...'))
                trained = train_model()
                if not trained:
                    raise RuntimeError('Entrenamiento falló o no hay imágenes para entrenar.')

                # 3) Si todo OK, insertar la persona en la base usando el id reservado
                inserted_id = insertar_persona_con_id(next_id, nombre, cedula, cargo)
                # Actualizar UI en el hilo principal
                def _done():
                    progress_win.grab_release()
                    progress_win.destroy()
                    messagebox.showinfo('Éxito', f'Persona agregada y entrenada. ID: {inserted_id}')
                    self.clear_form()
                    self.refrescar()
                    self.btn_add.config(state='normal')
                    self.btn_edit.config(state='normal')
                    self.btn_delete.config(state='normal')
                self.root.after(0, _done)
            except Exception as e:
                # En caso de error, cerrar ventana de progreso y avisar
                def _error():
                    try:
                        progress_win.grab_release()
                        progress_win.destroy()
                    except Exception:
                        pass
                    messagebox.showerror('Error', f'Proceso abortado: {e}')
                    self.btn_add.config(state='normal')
                    self.btn_edit.config(state='normal')
                    self.btn_delete.config(state='normal')
                self.root.after(0, _error)

        Thread(target=worker, daemon=True).start()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.selected_id = None
            self.btn_edit.config(state='disabled', bg='#D3D3D3', fg='gray')
            return
        iid = sel[0]
        try:
            persona = next((p for p in mostrar_personas() if str(p[0]) == iid), None)
        except Exception:
            persona = None
        if persona:
            id_, nombre, cedula, ultima, cargo = persona
            self.selected_id = id_
            # Rellenar campos (manejar None)
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, nombre or '')
            self.entry_cedula.delete(0, tk.END)
            self.entry_cedula.insert(0, cedula or '')
            self.entry_cargo.delete(0, tk.END)
            self.entry_cargo.insert(0, cargo or '')
            # Habilitar botón cuando hay selección
            self.btn_edit.config(state='normal', bg='#FFB703', fg='black')
        else:
            self.selected_id = None
            self.btn_edit.config(state='disabled', bg='#D3D3D3', fg='gray')

    def editar(self):
        if not self.selected_id:
            messagebox.showwarning('Advertencia', 'Seleccione una persona de la tabla para editar.')
            return
        nombre = self.entry_nombre.get().strip()
        cedula = self.entry_cedula.get().strip()
        cargo = self.entry_cargo.get().strip()
        # Validaciones
        if not (nombre and cedula and cargo):
            messagebox.showwarning('Advertencia', 'Complete todos los campos antes de editar.')
            return

        if not re.fullmatch(r"\d{6,7}", cedula):
            messagebox.showwarning('Advertencia', 'La cédula debe contener solo números y tener entre 6 y 7 dígitos.')
            return

        if re.search(r"\d", nombre):
            messagebox.showwarning('Advertencia', 'El nombre no puede contener números.')
            return

        if re.search(r"\d", cargo):
            messagebox.showwarning('Advertencia', 'El cargo no puede contener números.')
            return

        # Verificar duplicados excluyendo el registro actual
        if persona_existe(nombre, cedula, exclude_id=self.selected_id):
            messagebox.showwarning('Advertencia', 'Otro registro ya tiene estos datos o la misma cédula.')
            return

        editar_persona(self.selected_id, nombre=nombre, cedula=cedula, cargo=cargo)
        messagebox.showinfo('Éxito', 'Persona actualizada')
        self.clear_form()
        self.refrescar()

    def eliminar(self):
        if not self.selected_id:
            messagebox.showwarning('Advertencia', 'Seleccione una persona para eliminar.')
            return
        if messagebox.askyesno('Confirmar', '¿Eliminar la persona seleccionada?'):
            try:
                # Eliminar de la base de datos primero
                eliminar_persona(self.selected_id)
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo eliminar la persona de la base de datos: {e}')
                return

            # Luego intentar eliminar las fotos asociadas
            try:
                person_folder = Path(FACES_DIR) / str(self.selected_id)
                if person_folder.exists() and person_folder.is_dir():
                    shutil.rmtree(person_folder)
                    # intentar eliminar carpeta padre si está vacía (opcional)
                    try:
                        parent = person_folder.parent
                        if parent.exists() and not any(parent.iterdir()):
                            parent.rmdir()
                    except Exception:
                        pass
                    messagebox.showinfo('Éxito', 'Persona y fotos asociadas eliminadas')
                else:
                    messagebox.showinfo('Éxito', 'Persona eliminada (no se encontraron fotos)')
            except Exception as e:
                messagebox.showwarning('Advertencia', f'Persona eliminada de la BD, pero no se pudieron borrar las fotos: {e}')

            self.clear_form()
            self.refrescar()

    def buscar(self):
        termino = self.entry_buscar.get().strip()
        if not termino:
            self.refrescar()
            return
        resultados = buscar_personas(termino)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, p in enumerate(resultados):
            tag = 'even' if i % 2 == 0 else 'odd'
            id_, nombre, cedula, ultima, cargo = p
            hora_text = ultima if ultima else '-'
            self.tree.insert('', 'end', iid=str(id_), values=(id_, nombre, cedula, cargo, hora_text), tags=(tag,))

    def clear_form(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_cedula.delete(0, tk.END)
        self.entry_cargo.delete(0, tk.END)
        self.selected_id = None
        # deseleccionar en la tabla
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        # Deshabilitar botón al limpiar
        self.btn_edit.config(state='disabled', bg='#D3D3D3', fg='gray')


if __name__ == '__main__':
    root = tk.Tk()
    app = PersonasGUI(root)
    root.mainloop()