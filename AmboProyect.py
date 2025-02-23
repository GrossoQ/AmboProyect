import sqlite3
from tkinter import Tk, Label, Entry, Button, Text, Frame, Scrollbar, messagebox, ttk 
from datetime import datetime

# Función para conectar a la base de datos
def conectar_db():
    conn = sqlite3.connect('inventario.db')
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

# Función para crear las tablas si no existen
def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()

    # Crear tabla Productos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Productos (
        id_producto INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        stock INTEGER NOT NULL,
        precio REAL NOT NULL
    )
    ''')

    # Crear tabla Ventas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER,
        cantidad INTEGER NOT NULL,
        fecha_venta TEXT NOT NULL,
        FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
    )
    ''')

    # Crear tabla Compras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Compras (
        id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER,
        cantidad INTEGER NOT NULL,
        fecha_compra TEXT NOT NULL,
        FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
    )
    ''')

    conn.commit()
    conn.close()

# Función para agregar un producto
def agregar_producto():
    id_producto = entry_id_producto.get()
    nombre = entry_nombre.get()
    descripcion = entry_descripcion.get()
    stock = entry_stock.get()
    precio = entry_precio.get()

    if id_producto and nombre and descripcion and stock and precio:
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO Productos (id_producto, nombre, descripcion, stock, precio)
            VALUES (?, ?, ?, ?, ?)
            ''', (int(id_producto), nombre, descripcion, int(stock), float(precio)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            limpiar_campos()
            actualizar_lista_productos()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
    else:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

# Función para registrar una venta
def registrar_venta():
    id_producto = combo_productos_ventas.get().split(" - ")[0]  # Obtener el ID del producto seleccionado
    cantidad = entry_cantidad_venta.get()

    if id_producto and cantidad:
        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # Verificar stock
            cursor.execute('SELECT stock FROM Productos WHERE id_producto = ?', (id_producto,))
            stock = cursor.fetchone()[0]

            if stock >= int(cantidad):
                fecha_venta = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                INSERT INTO Ventas (id_producto, cantidad, fecha_venta)
                VALUES (?, ?, ?)
                ''', (id_producto, int(cantidad), fecha_venta))

                # Actualizar stock
                cursor.execute('''
                UPDATE Productos
                SET stock = stock - ?
                WHERE id_producto = ?
                ''', (int(cantidad), id_producto))

                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Venta registrada correctamente.")
                limpiar_campos_venta()
                actualizar_lista_productos()
            else:
                messagebox.showwarning("Advertencia", "No hay suficiente stock.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
    else:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

# Función para registrar una compra
def registrar_compra():
    id_producto = combo_productos_compras.get().split(" - ")[0]  # Obtener el ID del producto seleccionado
    cantidad = entry_cantidad_compra.get()

    if id_producto and cantidad:
        try:
            conn = conectar_db()
            cursor = conn.cursor()

            if int(cantidad) > 0:
                fecha_compra = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                INSERT INTO Compras (id_producto, cantidad, fecha_compra)
                VALUES (?, ?, ?)
                ''', (id_producto, int(cantidad), fecha_compra))

                # Actualizar stock
                cursor.execute('''
                UPDATE Productos
                SET stock = stock + ?
                WHERE id_producto = ?
                ''', (int(cantidad), id_producto))

                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Compra registrada correctamente.")
                limpiar_campos_compra()
                actualizar_lista_productos()
            else:
                messagebox.showwarning("Advertencia", "La cantidad de compra tiene que ser mayor a cero.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
    else:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")

# Función para actualizar la lista de productos
def actualizar_lista_productos():
    seleccion_actual_ventas = combo_productos_ventas.get()
    seleccion_actual_compras = combo_productos_compras.get()

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id_producto, nombre, descripcion, precio, stock FROM Productos')
    productos = cursor.fetchall()
    conn.close()

    valores = [f"{p[0]} - {p[1]} - {p[2]} - ${p[3]} - (Stock: {p[4]})" for p in productos]

    # Actualizar Combobox de Ventas
    combo_productos_ventas['values'] = valores
    combo_productos_ventas.config(width=80)
    if seleccion_actual_ventas in valores:
        combo_productos_ventas.set(seleccion_actual_ventas)
    else:
        if valores:
            combo_productos_ventas.current(0)
        else:
            combo_productos_ventas.set('')

    # Actualizar Combobox de Compras
    combo_productos_compras['values'] = valores
    combo_productos_compras.config(width=80)
    if seleccion_actual_compras in valores:
        combo_productos_compras.set(seleccion_actual_compras)
    else:
        if valores:
            combo_productos_compras.current(0)
        else:
            combo_productos_compras.set('')

# Función para limpiar campos de productos
def limpiar_campos():
    entry_id_producto.delete(0, 'end')
    entry_nombre.delete(0, 'end')
    entry_descripcion.delete(0, 'end')
    entry_stock.delete(0, 'end')
    entry_precio.delete(0, 'end')

# Función para limpiar campos de ventas
def limpiar_campos_venta():
    entry_cantidad_venta.delete(0, 'end')

# Función para limpiar campos de compras
def limpiar_campos_compra():
    entry_cantidad_compra.delete(0, 'end')

# Función para mostrar las ventas en el widget Text
def mostrar_ventas():
    # Limpiar el widget Text antes de mostrar nuevos datos
    text_ventas.delete(1.0, "end")

    # Conectar a la base de datos
    conn = conectar_db()
    cursor = conn.cursor()

    # Consultar las ventas
    cursor.execute('''
    SELECT Ventas.id_venta, Productos.nombre, Ventas.cantidad, Ventas.fecha_venta
    FROM Ventas
    INNER JOIN Productos ON Ventas.id_producto = Productos.id_producto
    ''')
    ventas = cursor.fetchall()

    # Mostrar los datos en el widget Text
    if ventas:
        text_ventas.insert("end", "--- Lista de Ventas ---\n")
        for venta in ventas:
            id_venta, nombre, cantidad, fecha_venta = venta
            text_ventas.insert("end", f"ID Venta: {id_venta}\n")
            text_ventas.insert("end", f"Producto: {nombre}\n")
            text_ventas.insert("end", f"Cantidad: {cantidad}\n")
            text_ventas.insert("end", f"Fecha: {fecha_venta}\n")
            text_ventas.insert("end", "-" * 30 + "\n")
    else:
        text_ventas.insert("end", "No hay ventas registradas.\n")

    # Cerrar la conexión
    conn.close()
    
# Función para mostrar las ventas del producto seleccionado en el Combobox
def mostrar_ventas_por_producto():
    # Obtener el valor seleccionado en el Combobox
    seleccion = combo_productos_ventas.get()

    if seleccion:
        # Extraer el ID del producto desde el valor seleccionado
        id_producto = seleccion.split(" - ")[0]  # El ID está antes del primer " - "

        # Limpiar el widget Text antes de mostrar nuevos datos
        text_ventas.delete(1.0, "end")

        # Conectar a la base de datos
        conn = conectar_db()
        cursor = conn.cursor()

        # Consultar las ventas del producto específico
        cursor.execute('''
        SELECT Ventas.id_venta, Productos.nombre, Ventas.cantidad, Ventas.fecha_venta
        FROM Ventas
        INNER JOIN Productos ON Ventas.id_producto = Productos.id_producto
        WHERE Ventas.id_producto = ?
        ''', (id_producto,))
        ventas = cursor.fetchall()

        # Mostrar los datos en el widget Text
        if ventas:
            text_ventas.insert("end", f"--- Ventas del Producto ID {id_producto} ---\n")
            for venta in ventas:
                id_venta, nombre, cantidad, fecha_venta = venta
                text_ventas.insert("end", f"ID Venta: {id_venta}\n")
                text_ventas.insert("end", f"Producto: {nombre}\n")
                text_ventas.insert("end", f"Cantidad: {cantidad}\n")
                text_ventas.insert("end", f"Fecha: {fecha_venta}\n")
                text_ventas.insert("end", "-" * 30 + "\n")
        else:
            text_ventas.insert("end", f"No hay ventas registradas para el Producto ID {id_producto}.\n")

        # Cerrar la conexión
        conn.close()
    else:
        messagebox.showwarning("Advertencia", "Selecciona un producto.")
        
# Función para mostrar las compras del producto seleccionado en el Combobox
def mostrar_compras_por_producto():
    # Obtener el valor seleccionado en el Combobox
    seleccion = combo_productos_compras.get()

    if seleccion:
        # Extraer el ID del producto desde el valor seleccionado
        id_producto = seleccion.split(" - ")[0]  # El ID está antes del primer " - "

        # Limpiar el widget Text antes de mostrar nuevos datos
        text_compras.delete(1.0, "end")

        # Conectar a la base de datos
        conn = conectar_db()
        cursor = conn.cursor()

        # Consultar las compras del producto específico
        cursor.execute('''
        SELECT Compras.id_compra, Productos.nombre, Compras.cantidad, Compras.fecha_compra
        FROM Compras
        INNER JOIN Productos ON Compras.id_producto = Productos.id_producto
        WHERE Compras.id_producto = ?
        ''', (id_producto,))
        compras = cursor.fetchall()

        # Mostrar los datos en el widget Text
        if compras:
            text_compras.insert("end", f"--- Compras del Producto ID {id_producto} ---\n")
            for compra in compras:
                id_compra, nombre, cantidad, fecha_compra = compra
                text_compras.insert("end", f"ID Compra: {id_compra}\n")
                text_compras.insert("end", f"Producto: {nombre}\n")
                text_compras.insert("end", f"Cantidad: {cantidad}\n")
                text_compras.insert("end", f"Fecha: {fecha_compra}\n")
                text_compras.insert("end", "-" * 30 + "\n")
        else:
            text_compras.insert("end", f"No hay compras registradas para el Producto ID {id_producto}.\n")

        # Cerrar la conexión
        conn.close()
    else:
        messagebox.showwarning("Advertencia", "Selecciona un producto.")
        
def borrar_producto():
    # Obtener el ID del producto desde el campo de entrada
    id_producto = entry_id_producto.get()
    if id_producto:
        try:
            id_producto = int(id_producto)  # Convertir a entero
            # Preguntar al usuario si está seguro de eliminar el producto
            yesno = messagebox.askyesno("Eliminar producto", f"¿Desea eliminar el producto ID: {id_producto}?")
            if yesno:  # Si el usuario hace clic en "Sí"
                conn = conectar_db()
                cursor = conn.cursor()
                # Verificar si el producto existe
                cursor.execute('''SELECT id_producto FROM Productos WHERE id_producto = ?''', (id_producto,))
                producto = cursor.fetchone()
                if producto:
                    # Eliminar las ventas asociadas al producto
                    cursor.execute('''DELETE FROM Ventas WHERE id_producto = ?''', (id_producto,))
                    # Eliminar las compras asociadas al producto
                    cursor.execute('''DELETE FROM Compras WHERE id_producto = ?''', (id_producto,))
                    # Eliminar el producto
                    cursor.execute('''DELETE FROM Productos WHERE id_producto = ?''', (id_producto,))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Éxito", "Producto y su historial eliminados correctamente.")
                    limpiar_campos()
                    actualizar_lista_productos()  # Actualizar la lista de productos
                else:
                    messagebox.showwarning("Advertencia", "El ID del producto no existe.")
        except ValueError:
            messagebox.showerror("Error", "El ID del producto debe ser un número.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
    else:
        messagebox.showwarning("Advertencia", "Ingresa un ID de producto.")
        

# Crear la ventana principal
ventana = Tk()
ventana.title("Sistema de Inventario")
ventana.geometry("500x400")

# Pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(fill='both', expand=True)

# Pestaña de productos
pestana_productos = ttk.Frame(notebook)
notebook.add(pestana_productos, text="Productos")

entradas = Frame(pestana_productos)
entradas.grid(row=0, column=0, columnspan=1, pady=10, sticky="w")

Label(entradas, text="ID Producto:").grid(row=0, column=0, padx=10, pady=5)
entry_id_producto = Entry(entradas, width=30)
entry_id_producto.grid(row=0, column=1, padx=10, pady=5)

Label(entradas, text="Nombre:").grid(row=1, column=0, padx=10, pady=5)
entry_nombre = Entry(entradas, width=30)
entry_nombre.grid(row=1, column=1, padx=10, pady=5)

Label(entradas, text="Descripción:").grid(row=2, column=0, padx=10, pady=5)
entry_descripcion = Entry(entradas, width=30)
entry_descripcion.grid(row=2, column=1, padx=10, pady=5)

Label(entradas, text="Stock:").grid(row=3, column=0, padx=10, pady=5)
entry_stock = Entry(entradas, width=30)
entry_stock.grid(row=3, column=1, padx=10, pady=5)

Label(entradas, text="Precio:").grid(row=4, column=0, padx=10, pady=5)
entry_precio = Entry(entradas, width=30)
entry_precio.grid(row=4, column=1, padx=10, pady=5)

marco_botones_productos = Frame(pestana_productos)
marco_botones_productos.grid(row=0, column=1, columnspan=3, pady=10, sticky="ne")

Button(marco_botones_productos, text="Agregar Producto", command=agregar_producto).grid(row=0, column=0, columnspan=1, pady=5, padx=10)

Button(marco_botones_productos, text="Borrar Producto", command=borrar_producto).grid(row=1, column=0, columnspan=1, pady=5, padx=10)

# Configurar las columnas para que se expandan correctamente
pestana_productos.grid_columnconfigure(3, weight=1)  # Esto hace que la columna 3 se expanda
pestana_productos.grid_columnconfigure(4, weight=0)  # Esto mantiene la columna 4 fija

# Pestaña de ventas
pestana_ventas = ttk.Frame(notebook)
notebook.add(pestana_ventas, text="Ventas")

Label(pestana_ventas, text="Producto:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
combo_productos_ventas = ttk.Combobox(pestana_ventas, state="readonly")
combo_productos_ventas.grid(row=0, column=1, columnspan=3, padx=10, pady=5, sticky="w")

Label(pestana_ventas, text="Cantidad:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_cantidad_venta = Entry(pestana_ventas)
entry_cantidad_venta.grid(row=1, column=1, padx=10, pady=5, sticky="w")

marco_botones_ventas = Frame(pestana_ventas)
marco_botones_ventas.grid(row=2, column=0, columnspan=3, pady=10, sticky="w")

Button(marco_botones_ventas, text="Registrar Venta", command=registrar_venta).grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="w")

Button(marco_botones_ventas, text="Mostrar Ventas", command=mostrar_ventas_por_producto).grid(row=0, column=1, columnspan=1, pady=10, sticky="w")

# Crear el Text antes de aplicar grid()
text_ventas = Text(pestana_ventas, wrap="none", height=10, width=40, font=("Arial", 12))
text_ventas.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# Crear y configurar la barra de desplazamiento
scrollbar = Scrollbar(pestana_ventas, orient="vertical", command=text_ventas.yview)
scrollbar.grid(row=3, column=4, sticky="ns")  # Ubicar la scrollbar en la misma fila que el Text
text_ventas.config(yscrollcommand=scrollbar.set)

# Configurar el layout para expansión
pestana_ventas.grid_columnconfigure(0, weight=0)  # Columna fija
pestana_ventas.grid_columnconfigure(1, weight=1)  # Se expande con la ventana
pestana_ventas.grid_columnconfigure(2, weight=0)  # Columna fija
pestana_ventas.grid_columnconfigure(3, weight=0)  # Columna fija
pestana_ventas.grid_columnconfigure(4, weight=0)  # Espacio para la scrollbar
pestana_ventas.grid_rowconfigure(3, weight=1)  # Permite que el Text crezca verticalmente



# Pestaña de compras
pestana_compras = ttk.Frame(notebook)
notebook.add(pestana_compras, text="Compras")

Label(pestana_compras, text="Producto:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
combo_productos_compras = ttk.Combobox(pestana_compras, state="readonly")
combo_productos_compras.grid(row=0, column=1, columnspan=3, padx=10, pady=5, sticky="w")

Label(pestana_compras, text="Cantidad:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_cantidad_compra = Entry(pestana_compras)
entry_cantidad_compra.grid(row=1, column=1, padx=10, pady=5, sticky="w")

marco_botones = Frame(pestana_compras)
marco_botones.grid(row=2, column=0, columnspan=3, pady=10, sticky="w")

Button(marco_botones, text="Registrar Compra", command=registrar_compra).grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="w")

Button(marco_botones, text="Mostrar Compras", command=mostrar_compras_por_producto).grid(row=0, column=1, columnspan=1, pady=10, sticky="w")

# Crear el Text antes de aplicar grid()
text_compras = Text(pestana_compras, wrap="none", height=10, width=40, font=("Arial", 12))
text_compras.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# Crear y configurar la barra de desplazamiento
scrollbar = Scrollbar(pestana_compras, orient="vertical", command=text_compras.yview)
scrollbar.grid(row=3, column=4, sticky="ns")  # Ubicar la scrollbar en la misma fila que el Text
text_compras.config(yscrollcommand=scrollbar.set)

# Definir la estructura de la cuadrícula para evitar desplazamientos
pestana_compras.grid_columnconfigure(0, weight=0)  # Mantiene la primera columna fija
pestana_compras.grid_columnconfigure(1, weight=1)  # Permite que la columna 1 se expanda
pestana_compras.grid_columnconfigure(2, weight=0)  # Mantiene la columna 2 fija
pestana_compras.grid_columnconfigure(3, weight=0)  # Mantiene la columna 3 fija
pestana_compras.grid_columnconfigure(4, weight=0)  # Espacio para la scrollbar
pestana_compras.grid_rowconfigure(3, weight=1)  # Permite que el Text crezca verticalmente


# Crear las tablas si no existen
crear_tablas()

# Actualizar lista de productos al iniciar
actualizar_lista_productos()

# Ejecutar la ventana
ventana.mainloop()