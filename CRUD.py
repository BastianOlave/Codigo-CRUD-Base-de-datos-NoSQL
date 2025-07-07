from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import tkinter as tk
from tkinter import ttk, messagebox
from time import sleep

# ---------- GUI ----------
root = tk.Tk()
root.title("Evaluación 4 - Base de Datos NoSQL")
root.geometry("800x600")
root.configure(bg="lavender")

# ---------- Consola de mensajes ----------
consola = tk.Text(root, 
                height=8, 
                bg="black", 
                fg="lime", 
                font=("Courier", 10))
consola.pack(side=tk.BOTTOM, fill=tk.X)

def log(mensaje):
    consola.insert(tk.END, mensaje + "\n")
    consola.see(tk.END)

# ---------- Contenedor dinámico ----------
main_frame = tk.Frame(root, 
                bg="lightblue")
main_frame.pack(fill=tk.BOTH, expand=True)

def mostrar_frame(func):
    for widget in main_frame.winfo_children():
        widget.destroy()
    func(main_frame)

# ---------- Cerrar ventana con confirmación ----------
def cerrar():
    if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", cerrar)

# ---------- Conexión a MongoDB ----------
db = None  # la definimos global para usar en otras funciones

def conectar_mongo():
    global db
    log("🔄 Conectando a MongoDB...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        client.server_info()
        db = client["ComercioTech"]
        
        log("✅ Conexión exitosa a MongoDB.")
    except ConnectionFailure as e:
        log(f"❌ Error al conectar a MongoDB: {e}")
        messagebox.showerror("Error", "No se pudo conectar a MongoDB.")
        root.destroy()  

# ---------- Funciones para ejecutar acciones según entidad ----------
def ejecutar_creacion(entidad):
    if entidad == "clientes":
        mostrar_frame(crear_cliente_form)
    elif entidad == "productos":
        mostrar_frame(crear_producto_form)
    elif entidad == "pedidos":
        mostrar_frame(crear_pedido_form)

def ejecutar_Actualizacion(entidad):
    if entidad == "clientes":
        mostrar_frame(actualizar_cliente_form)
    elif entidad == "productos":
        mostrar_frame(actualizar_producto_form)
    elif entidad == "pedidos":
        mostrar_frame(actualizar_pedido_form)

def ejecutar_eliminacion(entidad):
    if entidad == "clientes":
        mostrar_frame(eliminar_cliente_form)
    elif entidad == "productos":
        mostrar_frame(eliminar_producto_form)
    elif entidad == "pedidos":
        mostrar_frame(eliminar_pedido_form)

def ejecutar_consulta(entidad):
    if entidad == "clientes_ciudad":
        mostrar_frame(consulta_clientes_por_ciudad)


# ---------- Pantalla principal ----------
def pantalla_principal(frame):
    cuadroTitulo = tk.Frame(frame, bg="lightblue")
    titulo = tk.Label(frame,
        text="Evaluación 4 - Base de Datos NoSQL",
        font=("Helvetica", 20),
        bg="lightblue",
        fg="black",
        relief=tk.GROOVE, bd=2,
        padx=20, pady=20)
    titulo.pack()
    cuadroTitulo.pack()

    cuadro1 = tk.Frame(frame, bg="lightblue")
    texto1 = tk.Label(cuadro1,
        text="Seleccione una opción:",
        bg="lightblue",
        fg="black",
        font=("Helvetica", 14),
        width=30)
    texto1.pack(side=tk.LEFT, padx=20, pady=20)
    cuadro1.pack()

    opciones = [
        ("Crear Documento", lambda: mostrar_frame(lambda f: selector_entidad(f, "Crear Documento", ejecutar_creacion))),
        ("Actualizar Documento", lambda: mostrar_frame(lambda f: selector_entidad(f, "Actualizar Documento", ejecutar_Actualizacion))),
        ("Eliminar Documento", lambda: mostrar_frame(lambda f: selector_entidad(f, "Eliminar Documento", ejecutar_eliminacion))),
        ("Clientes por Ciudad", lambda: mostrar_frame(lambda f: ejecutar_consulta("clientes_ciudad")))

    ]


    for texto, comando in opciones:
        tk.Button(frame,
            text=texto,
            width=25,
            bg="yellow",
            fg="black",
            font=("Helvetica", 14),
            command=comando).pack(pady=10)
        
# Submenu para escoger si se quiere trabajar en cliente, proucto o pedido

def selector_entidad(frame, titulo, callback):
    tk.Label(frame, 
             text=titulo, 
             font=("Helvetica", 18), 
             bg="lightblue").pack(pady=20)
    entidades = [
        ("Clientes", "clientes"),
        ("Productos", "productos"),
        ("Pedidos", "pedidos")
    ]

    for texto, valor in entidades:
        tk.Button(frame, 
                  text=texto, 
                  width=25, 
                  font=("Helvetica", 12),
                  command=lambda v=valor: callback(v)).pack(pady=5)

    tk.Button(frame, 
              text="← Volver", 
              bg="gray", 
              command=lambda: mostrar_frame(pantalla_principal)).pack(pady=10)

# ---------- Crear Cliente ----------
def crear_cliente_form(frame):
    tk.Label(frame, 
             text="Formulario - Crear Cliente", 
             font=("Helvetica", 18), 
             bg="lightblue").pack(pady=10)

    entradas = {}

    campos = [
        ("Nombre", "nombre"),
        ("Apellidos", "apellidos"),
        ("Calle", "calle"),
        ("Número", "numero"),
        ("Ciudad", "ciudad"),
        ("Fecha de registro (YYYY-MM-DD)", "fecha_registro")
    ]

    for etiqueta, clave in campos:
        tk.Label(frame,
                 text=etiqueta + ":",
                 bg="lightblue",
                 font=("Helvetica", 12)).pack()
        entrada = tk.Entry(frame)
        entrada.pack()
        entradas[clave] = entrada

    def guardar():
        try:
            nombre = entradas["nombre"].get()
            apellidos = entradas["apellidos"].get()
            calle = entradas["calle"].get()
            numero = int(entradas["numero"].get())
            ciudad = entradas["ciudad"].get()
            fecha_registro = entradas["fecha_registro"].get()

            if not all([nombre, apellidos, calle, ciudad, fecha_registro]):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                log("❌ Campos incompletos.")
                return
            
            def generar_id_cliente():
                ultimo = db.Clientes.find_one(
                    {"id_cliente": {"$regex": "^CL[0-9]+$"}},
                    sort=[("id_cliente", -1)]
                )
                if ultimo:
                    ultimo_num = int(ultimo["id_cliente"][2:])
                    return f"CL{ultimo_num + 1:03}"
                else:
                    return "CL001"
            clid = generar_id_cliente()
            cliente_data = {
                "id_cliente": clid,
                "nombre": nombre,
                "apellidos": apellidos,
                "direccion": {
                    "calle": calle,
                    "numero": numero,
                    "ciudad": ciudad
                },
                "fecha_registro": fecha_registro
            }

            db.Clientes.insert_one(cliente_data)
            log(f"✅ Cliente '{nombre} {apellidos}' creado exitosamente.")
            mostrar_frame(pantalla_principal)

        except ValueError:
            messagebox.showerror("Error", "Número de casa debe ser un entero.")
            log("❌ Error al guardar: número de casa inválido.")

    tk.Button(frame, 
              text="Guardar", 
              bg="green", 
              fg="white", 
              font=("Helvetica", 12), 
              command=guardar).pack(pady=10)
    tk.Button(frame, 
              text="← Volver", 
              bg="gray", 
              command=lambda: mostrar_frame(pantalla_principal)).pack(pady=5)
    
## ---------- Crear Producto ----------

def crear_producto_form(frame):
    tk.Label(frame, 
             text="Formulario - Crear Producto", 
             font=("Helvetica", 18), 
             bg="lightblue").pack(pady=10)
    entradas = {}
    campos = [
        ("Nombre", "nombre_producto"),
        ("Precio", "precio"),
        ("Stock", "stock")
    ]
    for etiqueta, clave in campos:
        tk.Label(frame,
                 text=etiqueta + ":",
                 bg="lightblue",
                 font=("Helvetica", 12)).pack()
        entrada = tk.Entry(frame)
        entrada.pack()
        entradas[clave] = entrada

    def guardar_producto():
        try:
            nombre = entradas["nombre_producto"].get()
            precio = float(entradas["precio"].get())
            stock = int(entradas["stock"].get())

            if not nombre or precio < 0 or stock < 0:
                messagebox.showerror("Error", "Todos los campos son obligatorios y deben ser válidos.")
                log("❌ Campos incompletos o inválidos.")
                return
            estado = "Disponible" if stock > 0 else "No disponible"

            def codigoP():
                ultimo = db.Productos.find_one(
                    {"codigo_producto":{"$regex": "^P[0-9]+$"}},
                    sort=[("codigo_producto", -1)]
                )
                if ultimo and "codigo_producto" in ultimo:
                    ultimo_codigo = int(ultimo["codigo_producto"][1:])
                    nuevo_codigo = f"P{ultimo_codigo + 100}"
                else:
                    nuevo_codigo = "P100"
                return nuevo_codigo

            codigo = codigoP()
            producto_data = {
                "codigo_producto": codigo,
                "nombre_producto": nombre,
                "precio": precio,
                "stock": stock,
                "estado": estado
            }

            db.Productos.insert_one(producto_data)
            log(f"✅ Producto '{nombre}' creado exitosamente.")
            mostrar_frame(pantalla_principal)

        except ValueError:
            messagebox.showerror("Error", "Precio y stock deben ser números válidos.")
            log("❌ Error al guardar: precio o stock inválidos.")

    tk.Button(frame, 
        text="Guardar", 
        bg="green", 
        fg="white", 
        font=("Helvetica", 12), 
        command=guardar_producto).pack(pady=10)
    
    tk.Button(frame, 
        text="← Volver", 
        bg="gray", 
        command=lambda: mostrar_frame(pantalla_principal)).pack(pady=5)       

## --------- Funcion para pedir un producto ----------

def crear_pedido_form(frame):
    tk.Label(frame, 
             text="Formulario - Crear Pedido", 
             font=("Helvetica", 18), 
             bg="lightblue").pack(pady=10)
    
    clientes = [cliente["id_cliente"] for cliente in db.Clientes.find()]
    productos = list(db.Productos.find())
    selected_cliente = tk.StringVar()
    selected_producto = tk.StringVar()
    cantidad = tk.StringVar()
    metodo_pago = tk.StringVar()
    fecha_pedido = tk.StringVar()
    productos_agregados = []
    total_compra = tk.DoubleVar(value=0.0)

    tk.Label(frame,
            text="Cliente:", 
            bg="lightblue").pack()
    
    cliente_menu = ttk.Combobox(frame, 
                        textvariable=selected_cliente, 
                        values=clientes, 
                        state="readonly")
    cliente_menu.pack()

    tk.Label(frame, 
            text="Producto:", 
            bg="lightblue").pack()
    
    producto_menu = ttk.Combobox(frame, 
                                 textvariable=selected_producto, 
                                 values=[f"{p['codigo_producto']} - {p['nombre_producto']}" for p in productos],
                                 state="readonly")
    producto_menu.pack()

    tk.Label(frame, 
            text="Cantidad:", 
            bg="lightblue").pack()
    tk.Entry(frame, 
            textvariable=cantidad).pack()
    productos_frame = tk.Frame(frame, 
                            bg="white", 
                            relief=tk.SUNKEN, 
                            bd=1)
    productos_frame.pack(pady=5)

    def agregar_producto():
        try:
            codigo = selected_producto.get().split(" - ")[0]
            prod = next((p for p in productos if p["codigo_producto"] == codigo), None)
            if not prod:
                log("❌ Producto no encontrado.")
                return
            cant = int(cantidad.get())
            if cant <= 0:
                raise ValueError
            subtotal = cant * prod["precio"]
            productos_agregados.append({
                "codigo_producto": prod["codigo_producto"],
                "nombre": prod["nombre_producto"],
                "cantidad": cant,
                "precio_unitario": prod["precio"],
                "total_comprado": subtotal
            })
            total_compra.set(total_compra.get() + subtotal)
            log(f"➕ Agregado {cant}x {prod['nombre_producto']} (${subtotal})")

            # Mostrar en frame
            tk.Label(productos_frame, 
                    text=f"{cant}x {prod['nombre_producto']} - ${subtotal}", 
                    bg="white").pack(anchor="w")
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.")
            log("❌ Error: cantidad inválida.")

    tk.Button(frame, 
            text="Agregar producto", 
            command=agregar_producto, 
            bg="lightblue").pack(pady=5)
    tk.Label(frame, 
            text="Fecha del pedido (YYYY-MM-DD):", 
            bg="lightblue").pack()
    tk.Entry(frame, 
            textvariable=fecha_pedido).pack()
    tk.Label(frame, 
            text="Método de pago:", 
            bg="lightblue").pack()
    metodos = ["Efectivo", "Tarjeta de crédito", "Transferencia bancaria", "Débito"]
    metodo_pago_menu = ttk.Combobox(frame, 
                            textvariable=metodo_pago, 
                            values=metodos, 
                            state="readonly")
    metodo_pago_menu.pack()

    tk.Label(frame, textvariable=tk.StringVar(value="Total:")).pack()
    total_label = tk.Label(frame, textvariable=total_compra, font=("Helvetica", 12, "bold"), bg="lightblue")
    total_label.pack()

    def guardar_pedido():
        if not selected_cliente.get() or not productos_agregados or not metodo_pago.get() or not fecha_pedido.get():
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            log("❌ Pedido incompleto.")
            return

        # Autogenerar código de pedido
        ultimo = db.Pedidos.find_one(
            {"codigo_pedido": {"$regex": "^PED[0-9]+$"}},
            sort=[("codigo_pedido", -1)]
        )
        if ultimo and "codigo_pedido" in ultimo:
            ultimo_codigo = int(ultimo["codigo_pedido"][3:])
            codigo_pedido = f"PED{ultimo_codigo + 1:03}"
        else:
            codigo_pedido = "PED001"

        pedido_data = {
            "codigo_pedido": codigo_pedido,
            "codigo_cliente": selected_cliente.get(),
            "fecha_pedido": fecha_pedido.get(),
            "productos": productos_agregados,
            "total_compra": total_compra.get(),
            "metodo_pago": metodo_pago.get()
        }

        db.Pedidos.insert_one(pedido_data)
        messagebox.showinfo("Éxito", f"Pedido '{codigo_pedido}' guardado.")
        log(f"✅ Pedido creado: {pedido_data}")
        mostrar_frame(pantalla_principal)

    tk.Button(frame, 
            text="Guardar Pedido", 
            command=guardar_pedido, 
            bg="green", 
            fg="white").pack(pady=10)
    tk.Button(frame, 
            text="← Volver", 
            bg="gray", 
            command=lambda: mostrar_frame(pantalla_principal)).pack()
    
# ---------- Funcion para actualizar clientes ----------

def actualizar_cliente_form(frame):
    tk.Label(frame, 
             text="Formulario - Actualizar Cliente", 
             font=("Helvetica", 18), 
             bg="lightblue").pack(pady=10)

    clientes = [cliente["id_cliente"] for cliente in db.Clientes.find()]
    selected_cliente = tk.StringVar()
    entradas = {}

    tk.Label(frame,
            text="Seleccione un cliente:",
            bg="lightblue").pack()
    cliente_menu = ttk.Combobox(frame, 
                            textvariable=selected_cliente, 
                            values=clientes, 
                            state="readonly")
    cliente_menu.pack()

    campos=[
        ("Nombre", "nombre"),
        ("Apellidos", "apellidos"),
        ("Calle", "calle"),
        ("Número", "numero"),
        ("Ciudad", "ciudad"),
        ("Fecha de registro (YYYY-MM-DD)", "fecha_registro")
    ]

    for etiqueta, clave in campos:
        tk.Label(frame,
                 text=etiqueta + ":",
                 bg="lightblue",
                 font=("Helvetica", 12)).pack()
        entrada = tk.Entry(frame)
        entrada.pack()
        entradas[clave] = entrada
    
    def cargar_cliente(event=None):
        cliente = db.Clientes.find_one({"id_cliente": selected_cliente.get()})
        if cliente:
            entradas["nombre"].delete(0, tk.END)
            entradas["nombre"].insert(0, cliente.get("nombre", ""))
            entradas["apellidos"].delete(0, tk.END)
            entradas["apellidos"].insert(0, cliente.get("apellidos", ""))
            entradas["calle"].delete(0, tk.END)
            entradas["calle"].insert(0, cliente.get("direccion", {}).get("calle", ""))
            entradas["numero"].delete(0, tk.END)
            entradas["numero"].insert(0, cliente.get("direccion", {}).get("numero", ""))
            entradas["ciudad"].delete(0, tk.END)
            entradas["ciudad"].insert(0, cliente.get("direccion", {}).get("ciudad", ""))
            entradas["fecha_registro"].delete(0, tk.END)
            entradas["fecha_registro"].insert(0, cliente.get("fecha_registro", ""))
        else:
            log("❌ Cliente no encontrado.")
    cliente_menu.bind("<<ComboboxSelected>>", cargar_cliente)

    def guardar_actualizacion():
        try:
            datos_actualizados = {
                "nombre": entradas["nombre"].get(),
                "apellidos": entradas["apellidos"].get(),
                "direccion": {
                    "calle": entradas["calle"].get(),
                    "numero": int(entradas["numero"].get()),
                    "ciudad": entradas["ciudad"].get()
                },
                "fecha_registro": entradas["fecha_registro"].get()
            }
            db.Clientes.update_one(
                {"id_cliente": selected_cliente.get()},
                {"$set": datos_actualizados}
            )
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            log(f"✅ Cliente '{selected_cliente.get()}' actualizado.")
            mostrar_frame(pantalla_principal)
        except ValueError:
            messagebox.showerror("Error", "Número de casa debe ser un entero.")
            log("❌ Error al actualizar: número de casa inválido.")
    tk.Button(frame, 
              text="Guardar Cambios", 
              bg="green", 
              fg="white", 
              font=("Helvetica", 12), 
              command=guardar_actualizacion).pack(pady=10)
    tk.Button(frame,
                text="← Volver", 
                bg="gray", 
                command=lambda: mostrar_frame(pantalla_principal)).pack(pady=5)
    
# ---------- Función para actualizar productos ----------

def actualizar_producto_form(frame):
    tk.Label(frame, text="Formulario - Actualizar Producto", font=("Helvetica", 18), bg="lightblue").pack(pady=10)

    productos = [p["codigo_producto"] for p in db.Productos.find()]
    selected_producto = tk.StringVar()
    entradas = {}

    tk.Label(frame, text="Seleccione un producto:", bg="lightblue").pack()
    producto_menu = ttk.Combobox(frame, textvariable=selected_producto, values=productos, state="readonly")
    producto_menu.pack()

    campos = [
        ("Nombre", "nombre_producto"),
        ("Precio", "precio"),
        ("Stock", "stock")
    ]

    for etiqueta, clave in campos:
        tk.Label(frame, text=etiqueta + ":", bg="lightblue", font=("Helvetica", 12)).pack()
        entrada = tk.Entry(frame)
        entrada.pack()
        entradas[clave] = entrada

    def cargar_producto(event=None):
        producto = db.Productos.find_one({"codigo_producto": selected_producto.get()})
        if producto:
            entradas["nombre_producto"].delete(0, tk.END)
            entradas["nombre_producto"].insert(0, producto.get("nombre_producto", ""))
            entradas["precio"].delete(0, tk.END)
            entradas["precio"].insert(0, producto.get("precio", ""))
            entradas["stock"].delete(0, tk.END)
            entradas["stock"].insert(0, producto.get("stock", ""))
        else:
            log("❌ Producto no encontrado.")

    producto_menu.bind("<<ComboboxSelected>>", cargar_producto)

    def guardar_producto():
        try:
            precio = float(entradas["precio"].get())
            stock = int(entradas["stock"].get())
            estado = "Disponible" if stock > 0 else "No disponible"

            producto_actualizado = {
                "nombre_producto": entradas["nombre_producto"].get(),
                "precio": precio,
                "stock": stock,
                "estado": estado
            }

            db.Productos.update_one(
                {"codigo_producto": selected_producto.get()},
                {"$set": producto_actualizado}
            )
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            log(f"✅ Producto '{selected_producto.get()}' actualizado.")
            mostrar_frame(pantalla_principal)
        except ValueError:
            messagebox.showerror("Error", "Precio y stock deben ser válidos.")
            log("❌ Error al actualizar: datos inválidos.")

    tk.Button(frame, text="Guardar Cambios", bg="green", fg="white", command=guardar_producto).pack(pady=10)
    tk.Button(frame, text="← Volver", bg="gray", command=lambda: mostrar_frame(pantalla_principal)).pack(pady=5)

# ---------- Función para actualizar pedidos ----------

def actualizar_pedido_form(frame):
    tk.Label(frame, text="Formulario - Actualizar Pedido", font=("Helvetica", 18), bg="lightblue").pack(pady=10)

    pedidos = [p["codigo_pedido"] for p in db.Pedidos.find()]
    selected_pedido = tk.StringVar()
    fecha = tk.StringVar()
    metodo_pago = tk.StringVar()
    total = tk.DoubleVar()

    tk.Label(frame, text="Seleccione un pedido:", bg="lightblue").pack()
    pedido_menu = ttk.Combobox(frame, textvariable=selected_pedido, values=pedidos, state="readonly")
    pedido_menu.pack()

    tk.Label(frame, text="Fecha del pedido (YYYY-MM-DD):", bg="lightblue").pack()
    entry_fecha = tk.Entry(frame, textvariable=fecha)
    entry_fecha.pack()

    tk.Label(frame, text="Método de pago:", bg="lightblue").pack()
    metodos = ["Efectivo", "Tarjeta de crédito", "Transferencia bancaria", "Débito"]
    metodo_pago_menu = ttk.Combobox(frame, textvariable=metodo_pago, values=metodos, state="readonly")
    metodo_pago_menu.pack()

    tk.Label(frame, text="Total actual:", bg="lightblue").pack()
    tk.Label(frame, textvariable=total, font=("Helvetica", 12, "bold"), bg="lightblue").pack()

    def cargar_pedido(event=None):
        pedido = db.Pedidos.find_one({"codigo_pedido": selected_pedido.get()})
        if pedido:
            fecha.set(pedido.get("fecha_pedido", ""))
            metodo_pago.set(pedido.get("metodo_pago", ""))
            total.set(pedido.get("total_compra", 0))
        else:
            log("❌ Pedido no encontrado.")

    pedido_menu.bind("<<ComboboxSelected>>", cargar_pedido)

    def guardar_actualizacion():
        if not selected_pedido.get():
            return
        pedido_actualizado = {
            "fecha_pedido": fecha.get(),
            "metodo_pago": metodo_pago.get()
            # No se actualiza productos ni total aquí por simplicidad
        }
        db.Pedidos.update_one(
            {"codigo_pedido": selected_pedido.get()},
            {"$set": pedido_actualizado}
        )
        messagebox.showinfo("Éxito", "Pedido actualizado correctamente.")
        log(f"✅ Pedido '{selected_pedido.get()}' actualizado.")
        mostrar_frame(pantalla_principal)

    tk.Button(frame, text="Guardar Cambios", bg="green", fg="white", command=guardar_actualizacion).pack(pady=10)
    tk.Button(frame, text="← Volver", bg="gray", command=lambda: mostrar_frame(pantalla_principal)).pack(pady=5)

# ---------- Función para eliminar clientes ----------

def eliminar_cliente_form(frame):
    tk.Label(frame, text="Eliminar Cliente", font=("Helvetica", 18), bg="lightblue").pack(pady=10)

    clientes = [cliente["id_cliente"] for cliente in db.Clientes.find()]
    selected = tk.StringVar()

    tk.Label(frame, text="Seleccione un cliente a eliminar:", bg="lightblue").pack()
    selector = ttk.Combobox(frame, textvariable=selected, values=clientes, state="readonly")
    selector.pack(pady=5)

    def eliminar():
        if not selected.get():
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente '{selected.get()}'?"):
            db.Clientes.delete_one({"id_cliente": selected.get()})
            log(f"🗑️ Cliente '{selected.get()}' eliminado.")
            messagebox.showinfo("Eliminado", "Cliente eliminado exitosamente.")
            mostrar_frame(pantalla_principal)

    tk.Button(frame, text="Eliminar", bg="red", fg="white", command=eliminar).pack(pady=10)
    tk.Button(frame, text="← Volver", bg="gray", command=lambda: mostrar_frame(pantalla_principal)).pack()

# ---------- Función para eliminar productos ----------

def eliminar_producto_form(frame):
    tk.Label(frame, text="Eliminar Producto", font=("Helvetica", 18), bg="lightblue").pack(pady=10)

    productos = [prod["codigo_producto"] for prod in db.Productos.find()]
    selected = tk.StringVar()

    tk.Label(frame, text="Seleccione un producto a eliminar:", bg="lightblue").pack()
    selector = ttk.Combobox(frame, textvariable=selected, values=productos, state="readonly")
    selector.pack(pady=5)

    def eliminar():
        if not selected.get():
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar producto '{selected.get()}'?"):
            db.Productos.delete_one({"codigo_producto": selected.get()})
            log(f"🗑️ Producto '{selected.get()}' eliminado.")
            messagebox.showinfo("Eliminado", "Producto eliminado exitosamente.")
            mostrar_frame(pantalla_principal)

    tk.Button(frame, text="Eliminar", bg="red", fg="white", command=eliminar).pack(pady=10)
    tk.Button(frame, text="← Volver", bg="gray", command=lambda: mostrar_frame(pantalla_principal)).pack()

# ---------- Función para eliminar pedidos ----------

def eliminar_pedido_form(frame):
    tk.Label(frame, text="Eliminar Pedido", font=("Helvetica", 18), bg="lightblue").pack(pady=10)

    pedidos = [p["codigo_pedido"] for p in db.Pedidos.find()]
    selected = tk.StringVar()

    tk.Label(frame, text="Seleccione un pedido a eliminar:", bg="lightblue").pack()
    selector = ttk.Combobox(frame, textvariable=selected, values=pedidos, state="readonly")
    selector.pack(pady=5)

    def eliminar():
        if not selected.get():
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar pedido '{selected.get()}'?"):
            db.Pedidos.delete_one({"codigo_pedido": selected.get()})
            log(f"🗑️ Pedido '{selected.get()}' eliminado.")
            messagebox.showinfo("Eliminado", "Pedido eliminado exitosamente.")
            mostrar_frame(pantalla_principal)

    tk.Button(frame, text="Eliminar", bg="red", fg="white", command=eliminar).pack(pady=10)
    tk.Button(frame, text="← Volver", bg="gray", command=lambda: mostrar_frame(pantalla_principal)).pack()

# ---------- Consulta de clientes por ciudad ----------

def consulta_clientes_por_ciudad(frame):
    tk.Label(frame, text="Consulta de Clientes por Ciudad", font=("Helvetica", 18), bg="lightblue").pack(pady=10)

    # ---------- Obtener ciudades únicas ----------
    ciudades = sorted(set(cliente.get("direccion", {}).get("ciudad", "") for cliente in db.Clientes.find()))
    selected_ciudad = tk.StringVar()

    # ---------- Combobox de ciudades ----------
    tk.Label(frame, text="Seleccione una ciudad:", bg="lightblue").pack()
    ciudad_combo = ttk.Combobox(frame, textvariable=selected_ciudad, values=ciudades, state="readonly")
    ciudad_combo.pack(pady=5)

    # ---------- Frame para los resultados ----------
    resultados_frame = tk.Frame(frame, bg="white", relief=tk.SUNKEN, bd=2)
    resultados_frame.pack(pady=20, padx=30, fill=tk.X)

    def consultar():
        for widget in resultados_frame.winfo_children():
            widget.destroy()

        ciudad = selected_ciudad.get()
        if not ciudad:
            log("⚠️ Debes seleccionar una ciudad.")
            return

        clientes = db.Clientes.find({"direccion.ciudad": ciudad})
        encontrados = list(clientes)

        if not encontrados:
            tk.Label(resultados_frame, text="No se encontraron clientes.", bg="white", font=("Helvetica", 12)).pack()
            log(f"🔍 Sin resultados para ciudad '{ciudad}'.")
        else:
            for cli in encontrados:
                nombre = f"{cli.get('nombre', '')} {cli.get('apellidos', '')}"
                tk.Label(resultados_frame, text=nombre, anchor="w", bg="white", font=("Helvetica", 12)).pack(fill=tk.X)
            log(f"📋 {len(encontrados)} cliente(s) encontrados en '{ciudad}'.")

    # ---------- Botón consultar ----------
    tk.Button(frame, text="Consultar", bg="blue", fg="white", command=consultar).pack(pady=10)

    # ---------- Botón volver ----------
    tk.Button(frame, text="← Volver", bg="gray", command=lambda: mostrar_frame(pantalla_principal)).pack(pady=5)


# ---------- Lanzar app ----------
mostrar_frame(pantalla_principal)
conectar_mongo()  # ← Aquí llamamos la conexión al iniciar
root.mainloop()
