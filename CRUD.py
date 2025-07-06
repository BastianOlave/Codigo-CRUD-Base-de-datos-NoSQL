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

def ejecutar_lectura(entidad):
    if entidad == "clientes":
        mostrar_frame(actualizar_cliente_form)


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
        ("Leer Documentos", lambda: mostrar_frame(lambda f: selector_entidad(f, "Leer Documentos", ejecutar_lectura))),
        ("Actualizar Documento", lambda: mostrar_frame(lambda f: selector_entidad(f, "Actualizar Documento", ejecutar_actualizacion))),
        ("Eliminar Documento", lambda: mostrar_frame(lambda f: selector_entidad(f, "Eliminar Documento", ejecutar_eliminacion)))
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
                    {"_id": {"$regex": "^CL[0-9]+$"}},
                    sort=[("_id", -1)]
                )
                if ultimo:
                    ultimo_num = int(ultimo["_id"][2:])
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

# ---------- Lanzar app ----------
mostrar_frame(pantalla_principal)
conectar_mongo()  # ← Aquí llamamos la conexión al iniciar
root.mainloop()
