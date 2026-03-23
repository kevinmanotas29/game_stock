import customtkinter as ctk
from tkinter import ttk
from database import db_unified as database
import threading
from utils.logger import get_logger

logger = get_logger(__name__)

# Variables globales
usuario_actual = None
ventana = None
label_usuario = None
callbacks_pendientes = []  # Para rastrear callbacks de after()
gemini_chat = None  # Cliente de Gemini AI
animacion_activa = False  # Estado de la animación de "escribiendo..."
frame_escribiendo = None  # Frame de la animación
label_escribiendo = None  # Label de la animación

def inicializar_interfaz():
    """Inicializa toda la interfaz después de crear la ventana"""
    global ventana, usuario_actual, label_usuario
    
    logger.info("Inicializando interfaz principal...")
    
    # Configurar CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Crear la base si no existe
    logger.info("Conectando a base de datos...")
    database.conectar()
    logger.info("Base de datos conectada")

    # Ventana principal
    ventana = ctk.CTk()
    ventana.title("GameStock | Sistema de Inventario con IA")
    ventana.geometry("1400x750")
    ventana.minsize(1200, 650)
    
    # CONTENEDORES PRINCIPALES
    
    # Panel izquierdo - Formulario
    frame_izquierdo = ctk.CTkFrame(ventana, width=320, corner_radius=15)
    frame_izquierdo.pack(side="left", fill="both", padx=20, pady=20)
    frame_izquierdo.pack_propagate(False)

    # Obtener categorías de la base de datos
    categorias = database.obtener_categorias()
    nombres_categorias = [cat[1] for cat in categorias]  # cat[1] es el nombre

    # Panel central - Tabla de productos
    frame_central = ctk.CTkFrame(ventana, corner_radius=15)
    frame_central.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=20)

    # Panel derecho - Chat IA
    frame_derecho = ctk.CTkFrame(ventana, width=480, corner_radius=15)
    frame_derecho.pack(side="right", fill="both", padx=(0, 20), pady=20)
    frame_derecho.pack_propagate(False)

    # ==================== PANEL IZQUIERDO: FORMULARIO ====================

    # Título
    titulo = ctk.CTkLabel(
        frame_izquierdo,
        text="🎮 GameStock",
        font=("Arial", 24, "bold"),
        text_color="#4FC3F7"
    )
    titulo.pack(pady=(10, 10))

    # Label de usuario logueado
    label_usuario = ctk.CTkLabel(
        frame_izquierdo,
        text="",
        font=("Arial", 10),
        text_color="#888888"
    )
    label_usuario.pack(pady=(0, 10))

    # Botón cerrar sesión
    def cerrar_sesion():
        global animacion_activa, callbacks_pendientes
        
        # Detener animaciones activas
        animacion_activa = False
        
        # Cancelar todos los callbacks pendientes
        for callback_id in callbacks_pendientes:
            try:
                ventana.after_cancel(callback_id)
            except:
                pass
        callbacks_pendientes.clear()
        
        # Cerrar ventana
        ventana.quit()
        ventana.destroy()

    btn_cerrar_sesion = ctk.CTkButton(
        frame_izquierdo,
        text="Cerrar Sesión",
        command=cerrar_sesion,
        height=30,
        width=120,
        font=("Arial", 10),
        fg_color="#F44336",
        hover_color="#D32F2F"
    )
    btn_cerrar_sesion.pack(pady=(0, 15))

    # Campo Nombre
    ctk.CTkLabel(frame_izquierdo, text="Nombre del Producto", 
                 font=("Arial", 11)).pack(pady=(5, 2), anchor="w", padx=15)
    entrada_nombre = ctk.CTkEntry(frame_izquierdo, height=40, font=("Arial", 12))
    entrada_nombre.pack(pady=(0, 15), padx=15, fill="x")

    # Campo Cantidad
    ctk.CTkLabel(frame_izquierdo, text="Cantidad", 
                 font=("Arial", 11)).pack(pady=(5, 2), anchor="w", padx=15)
    entrada_cantidad = ctk.CTkEntry(frame_izquierdo, height=40, font=("Arial", 12))
    entrada_cantidad.pack(pady=(0, 15), padx=15, fill="x")

    # Campo Precio
    ctk.CTkLabel(frame_izquierdo, text="Precio (COP)", 
                 font=("Arial", 11)).pack(pady=(5, 2), anchor="w", padx=15)
    entrada_precio = ctk.CTkEntry(frame_izquierdo, height=40, font=("Arial", 12))
    entrada_precio.pack(pady=(0, 15), padx=15, fill="x")

    # Campo Categoría
    ctk.CTkLabel(frame_izquierdo, text="Categoría", 
                 font=("Arial", 11)).pack(pady=(5, 2), anchor="w", padx=15)
    
    # Obtener categorías de la base de datos
    categorias = database.obtener_categorias()
    nombres_categorias = [cat[1] for cat in categorias]  # cat[1] es el nombre
    
    combo_categoria = ctk.CTkComboBox(
        frame_izquierdo,
        values=nombres_categorias,
        height=40,
        font=("Arial", 12),
        state="readonly"
    )
    combo_categoria.pack(pady=(0, 15), padx=15, fill="x")
    combo_categoria.set("Selecciona una categoría")

    # Mensaje de estado
    mensaje = ctk.CTkLabel(frame_izquierdo, text="", font=("Arial", 10), text_color="#4CAF50")
    mensaje.pack(pady=10)

    # FUNCIONES

    def guardar_producto():
        global usuario_actual  # Declarar como global
        try:
            nombre = entrada_nombre.get()
            cantidad = int(entrada_cantidad.get())
            precio = float(entrada_precio.get())

            logger.info(f"Guardando producto: {nombre}, cantidad={cantidad}, precio={precio}")
            
            # Obtener categoría seleccionada
            categoria_seleccionada = combo_categoria.get()
            categoria_id = None
            
            # Buscar el ID de la categoría
            if categoria_seleccionada != "Selecciona una categoría":
                for cat in categorias:
                    if cat[1] == categoria_seleccionada:
                        categoria_id = cat[0]
                        break
            
            # Pasar el usuario_id para registrar en historial
            usuario_id = usuario_actual['id'] if usuario_actual else None
            logger.info(f"Usuario actual ID: {usuario_id}, Categoría ID: {categoria_id}")
            database.agregar_producto(nombre, cantidad, precio, categoria_id=categoria_id, usuario_id=usuario_id)
            
            logger.info(f"Producto guardado: {nombre}")
            mensaje.configure(text="✓ Producto guardado", text_color="#4CAF50")

            entrada_nombre.delete(0, "end")
            entrada_cantidad.delete(0, "end")
            entrada_precio.delete(0, "end")
            combo_categoria.set("Selecciona una categoría")

            cargar_productos()
        except Exception as e:
            logger.error(f"✗ Error al guardar producto: {e}")
            mensaje.configure(text="✗ Datos inválidos", text_color="#F44336")


    def cargar_productos():
        # Limpiar tabla
        for item in tabla_productos.get_children():
            tabla_productos.delete(item)
    
        productos = database.obtener_productos()
    
        for producto in productos:
            precio_formateado = f"${producto[3]:,.0f}".replace(",", ".")
            tabla_productos.insert("", "end", values=(
                producto[0],
                producto[1],
                producto[2],
                precio_formateado
            ))


    def seleccionar_producto(event):
        try:
            seleccion = tabla_productos.selection()
            if not seleccion:
                return
        
            item = tabla_productos.item(seleccion[0])
            valores = item['values']
        
            nombre = valores[1]
            cantidad = valores[2]
            precio = str(valores[3]).replace("$", "").replace(".", "")
        
            entrada_nombre.delete(0, "end")
            entrada_nombre.insert(0, nombre)
        
            entrada_cantidad.delete(0, "end")
            entrada_cantidad.insert(0, cantidad)
        
            entrada_precio.delete(0, "end")
            entrada_precio.insert(0, precio)
        except:
            pass


    def eliminar_producto():
        global usuario_actual  # Declarar como global
        try:
            seleccion = tabla_productos.selection()
            if not seleccion:
                mensaje.configure(text="⚠ Selecciona un producto", text_color="#FF9800")
                return

            item = tabla_productos.item(seleccion[0])
            id_producto = item['values'][0]

            # Pasar el usuario_id para registrar en historial
            usuario_id = usuario_actual['id'] if usuario_actual else None
            logger.info(f"Eliminando producto ID {id_producto}, usuario: {usuario_id}")  # Debug
            database.eliminar_producto(id_producto, usuario_id=usuario_id)
            
            cargar_productos()
            mensaje.configure(text="✓ Producto eliminado", text_color="#4CAF50")
        except:
            mensaje.configure(text="✗ Error al eliminar", text_color="#F44336")


    def actualizar_producto():
        global usuario_actual  # Declarar como global
        try:
            seleccion = tabla_productos.selection()
            if not seleccion:
                mensaje.configure(text="⚠ Selecciona un producto", text_color="#FF9800")
                return

            item = tabla_productos.item(seleccion[0])
            id_producto = item['values'][0]

            nombre = entrada_nombre.get()
            cantidad = int(entrada_cantidad.get())
            precio = float(entrada_precio.get())

            # Pasar el usuario_id para registrar en historial
            usuario_id = usuario_actual['id'] if usuario_actual else None
            logger.info(f"Actualizando producto ID {id_producto}, usuario: {usuario_id}")  # Debug
            database.actualizar_producto(id_producto, nombre, cantidad, precio, categoria_id=None, usuario_id=usuario_id)
            
            cargar_productos()
            mensaje.configure(text="✓ Producto actualizado", text_color="#4CAF50")
        except:
            mensaje.configure(text="✗ Error al actualizar", text_color="#F44336")


    # BOTONES con iconos
    btn_guardar = ctk.CTkButton(
        frame_izquierdo,
        text="💾 Guardar Producto",
        command=guardar_producto,
        height=45,
        font=("Arial", 13, "bold"),
        fg_color="#4CAF50",
        hover_color="#45a049"
    )
    btn_guardar.pack(pady=8, padx=15, fill="x")

    btn_actualizar = ctk.CTkButton(
        frame_izquierdo,
        text="✏️ Actualizar Producto",
        command=actualizar_producto,
        height=45,
        font=("Arial", 13, "bold"),
        fg_color="#2196F3",
        hover_color="#1976D2"
    )
    btn_actualizar.pack(pady=8, padx=15, fill="x")

    btn_eliminar = ctk.CTkButton(
        frame_izquierdo,
        text="🗑️ Eliminar Producto",
        command=eliminar_producto,
        height=45,
        font=("Arial", 13, "bold"),
        fg_color="#F44336",
        hover_color="#D32F2F"
    )
    btn_eliminar.pack(pady=8, padx=15, fill="x")

    # ==================== PANEL CENTRAL: TABLA ====================

    # Título
    titulo_tabla = ctk.CTkLabel(
        frame_central,
        text="📦 Inventario de Productos",
        font=("Arial", 20, "bold")
    )
    titulo_tabla.pack(pady=(15, 20))

    # Frame para la tabla
    tabla_frame = ctk.CTkFrame(frame_central, fg_color="transparent")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    # Crear Treeview (tabla) con estilo mejorado
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
                    background="#2b2b2b",
                    foreground="white",
                    rowheight=35,
                    fieldbackground="#2b2b2b",
                    borderwidth=0,
                    font=("Arial", 11))

    style.configure("Treeview.Heading",
                    background="#1f538d",
                    foreground="white",
                    font=("Arial", 12, "bold"),
                    borderwidth=0)

    style.map("Treeview",
              background=[("selected", "#1f538d")],
              foreground=[("selected", "white")])

    # Scrollbar
    scrollbar_y = ttk.Scrollbar(tabla_frame)
    scrollbar_y.pack(side="right", fill="y")

    # Tabla
    tabla_productos = ttk.Treeview(
        tabla_frame,
        columns=("ID", "Nombre", "Cantidad", "Precio"),
        show="headings",
        yscrollcommand=scrollbar_y.set,
        selectmode="browse"
    )

    # Configurar columnas
    tabla_productos.heading("ID", text="ID")
    tabla_productos.heading("Nombre", text="Nombre del Producto")
    tabla_productos.heading("Cantidad", text="Stock")
    tabla_productos.heading("Precio", text="Precio (COP)")

    tabla_productos.column("ID", width=60, anchor="center")
    tabla_productos.column("Nombre", width=300, anchor="w")
    tabla_productos.column("Cantidad", width=100, anchor="center")
    tabla_productos.column("Precio", width=150, anchor="e")

    tabla_productos.pack(fill="both", expand=True, side="left")
    scrollbar_y.config(command=tabla_productos.yview)

    tabla_productos.bind("<<TreeviewSelect>>", seleccionar_producto)

    # ==================== PANEL DERECHO: CHAT IA ====================

    # Título del chat
    titulo_chat = ctk.CTkLabel(
        frame_derecho,
        text="🤖 Asistente IA",
        font=("Arial", 20, "bold"),
        text_color="#4FC3F7"
    )
    titulo_chat.pack(pady=(15, 15))

    # Frame para el área de chat con scroll
    chat_frame = ctk.CTkScrollableFrame(
        frame_derecho, 
        fg_color="#1a1a1a",
        corner_radius=10,
        scrollbar_button_color="#3a3a3a",
        scrollbar_button_hover_color="#4a4a4a"
    )
    chat_frame.pack(fill="both", expand=True, padx=15)

    # Frame para entrada
    input_frame = ctk.CTkFrame(frame_derecho, fg_color="transparent")
    input_frame.pack(fill="x", padx=15, pady=(15, 15))

    # Campo de entrada
    entrada_chat = ctk.CTkEntry(
        input_frame,
        height=45,
        font=("Arial", 12),
        placeholder_text="Escribe tu mensaje..."
    )
    entrada_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))

    # Botón enviar
    btn_enviar = ctk.CTkButton(
        input_frame,
        text="Enviar",
        command=lambda: enviar_mensaje_chat(),
        height=45,
        width=100,
        font=("Arial", 13, "bold"),
        fg_color="#4CAF50",
        hover_color="#45a049"
    )
    btn_enviar.pack(side="right")

    def agregar_mensaje_sistema(mensaje):
        """Muestra mensaje del sistema (errores, avisos)"""
        frame_msg = ctk.CTkFrame(chat_frame, fg_color="transparent")
        frame_msg.pack(fill="x", pady=5, padx=10)
    
        label = ctk.CTkLabel(
            frame_msg,
            text=f"⚠️ {mensaje}",
            font=("Arial", 10),
            text_color="#FFA726",
            wraplength=350,
            justify="center"
        )
        label.pack()

    def agregar_mensaje_usuario(mensaje):
        """Muestra mensaje del usuario (burbuja azul a la derecha)"""
        # Frame contenedor alineado a la derecha
        frame_msg = ctk.CTkFrame(chat_frame, fg_color="transparent")
        frame_msg.pack(fill="x", pady=8, padx=10)
    
        # Burbuja del mensaje
        burbuja = ctk.CTkFrame(
            frame_msg,
            fg_color="#0084ff",
            corner_radius=15
        )
        burbuja.pack(side="right", anchor="e")
    
        # Calcular ancho dinámico basado en la longitud del mensaje
        # Mensajes cortos = burbuja pequeña, largos = burbuja grande
        longitud = len(mensaje)
        if longitud <= 20:
            ancho = 100
        elif longitud <= 50:
            ancho = 220
        elif longitud <= 100:
            ancho = 300
        else:
            ancho = 380
    
        # Calcular altura dinámica
        num_lineas = mensaje.count('\n') + 1
        caracteres_por_linea = ancho // 6  # Aproximación
        lineas_estimadas = max(num_lineas, (len(mensaje) // caracteres_por_linea) + 1)
        altura = max(lineas_estimadas * 20 + 10, 35)
    
        textbox = ctk.CTkTextbox(
            burbuja,
            font=("Arial", 11),
            text_color="white",
            fg_color="#0084ff",
            width=ancho,
            height=altura,
            wrap="word",
            activate_scrollbars=False
        )
        textbox.insert("1.0", mensaje)
        textbox.configure(state="disabled")
        textbox.pack(padx=15, pady=10)

    def agregar_mensaje_ai(mensaje):
        """Muestra mensaje de la IA (burbuja gris a la izquierda)"""
        # Frame contenedor alineado a la izquierda
        frame_msg = ctk.CTkFrame(chat_frame, fg_color="transparent")
        frame_msg.pack(fill="x", pady=8, padx=10)
    
        # Container para ícono y burbuja
        contenedor = ctk.CTkFrame(frame_msg, fg_color="transparent")
        contenedor.pack(side="left", anchor="w")
    
        # Ícono IA
        icono = ctk.CTkLabel(
            contenedor,
            text="🤖",
            font=("Arial", 16)
        )
        icono.pack(side="left", anchor="nw", padx=(0, 8))
    
        # Burbuja del mensaje
        burbuja = ctk.CTkFrame(
            contenedor,
            fg_color="#2d2d2d",
            corner_radius=15
        )
        burbuja.pack(side="left")
    
        # Calcular ancho dinámico basado en la longitud del mensaje
        longitud = len(mensaje)
        if longitud <= 30:
            ancho = 150
        elif longitud <= 80:
            ancho = 260
        elif longitud <= 150:
            ancho = 350
        else:
            ancho = 410
    
        # Calcular altura dinámica
        num_lineas = mensaje.count('\n') + 1
        caracteres_por_linea = ancho // 6
        lineas_estimadas = max(num_lineas, (len(mensaje) // caracteres_por_linea) + 1)
        altura = max(lineas_estimadas * 20 + 10, 35)
    
        textbox = ctk.CTkTextbox(
            burbuja,
            font=("Arial", 11),
            text_color="white",
            fg_color="#2d2d2d",
            width=ancho,
            height=altura,
            wrap="word",
            activate_scrollbars=False
        )
        textbox.insert("1.0", mensaje)
        textbox.configure(state="disabled")
        textbox.pack(padx=15, pady=10)

    def mostrar_escribiendo():
        """Muestra animación de 'escribiendo...' mientras la IA piensa"""
        global animacion_activa, frame_escribiendo, label_escribiendo
    
        # Crear frame para el indicador de escribiendo
        frame_escribiendo = ctk.CTkFrame(chat_frame, fg_color="transparent")
        frame_escribiendo.pack(fill="x", pady=8, padx=10)
    
        # Ícono IA
        icono = ctk.CTkLabel(
            frame_escribiendo,
            text="🤖",
            font=("Arial", 16)
        )
        icono.pack(side="left", anchor="nw", padx=(0, 8))
    
        # Burbuja animada
        burbuja = ctk.CTkFrame(
            frame_escribiendo,
            fg_color="#2d2d2d",
            corner_radius=15
        )
        burbuja.pack(side="left", anchor="w")
    
        # Label del texto animado
        label_escribiendo = ctk.CTkLabel(
            burbuja,
            text="escribiendo.",
            font=("Arial", 11),
            text_color="#888888",
            padx=15,
            pady=10
        )
        label_escribiendo.pack()
    
        puntos = [".", "..", "..."]
        contador = [0]
    
        def animar():
            global animacion_activa, callbacks_pendientes  # Declarar como global
            if not animacion_activa or label_escribiendo is None:
                return
        
            try:
                # Verificar que la ventana y el label existan
                if ventana and ventana.winfo_exists() and label_escribiendo and label_escribiendo.winfo_exists():
                    label_escribiendo.configure(text=f"escribiendo{puntos[contador[0] % 3]}")
                    contador[0] += 1
                    callback_id = ventana.after(500, animar)
                    callbacks_pendientes.append(callback_id)
            except:
                animacion_activa = False
    
        animacion_activa = True
        animar()

    def detener_escribiendo():
        """Detiene la animación y elimina el indicador de 'escribiendo...'"""
        global animacion_activa, frame_escribiendo, label_escribiendo
    
        animacion_activa = False
    
        if frame_escribiendo:
            try:
                frame_escribiendo.destroy()
            except:
                pass
            frame_escribiendo = None
    
        label_escribiendo = None

    def inicializar_gemini():
        """Inicializa la conexión con Gemini en segundo plano (silencioso)"""
        logger.info("Inicializando conexión con Gemini AI...")
        def init():
            global gemini_chat
            try:
                from chat.gemini_chat import GeminiChat
                gemini_chat = GeminiChat()
                logger.info("Gemini AI inicializado correctamente")
                # Conexión exitosa (sin mensajes visibles)
            except ImportError as e:
                logger.error(f"✗ Error al importar Gemini: {e}")
                # Solo mostrar error si falla
                ventana.after(0, lambda: agregar_mensaje_sistema(f"✗ Error: Módulo 'google-genai' no instalado"))
            except Exception as e:
                logger.error(f"✗ Error al conectar con Gemini: {e}")
                # Solo mostrar error si falla
                ventana.after(0, lambda: agregar_mensaje_sistema(f"✗ Error: Verifica tu API key en .env"))
    
        thread = threading.Thread(target=init, daemon=True)
        thread.start()

    def enviar_mensaje_chat():
        global gemini_chat  # Declarar como global
        mensaje = entrada_chat.get().strip()
        if not mensaje:
            return
    
        if not gemini_chat:
            logger.warning("Usuario intentó enviar mensaje antes de que Gemini esté listo")
            agregar_mensaje_sistema("⚠ Esperando conexión con Gemini...")
            return
    
        logger.info(f"Usuario envía mensaje: {mensaje}")
        entrada_chat.delete(0, "end")
        agregar_mensaje_usuario(mensaje)
    
        btn_enviar.configure(state="disabled", text="...")
        mostrar_escribiendo()
    
        def procesar():
            try:
                logger.info("Enviando mensaje a Gemini AI...")
                respuesta = gemini_chat.send_message(mensaje)
                logger.info(f"Respuesta recibida de Gemini ({len(respuesta)} caracteres)")
            
                # Programar actualización de UI en el thread principal
                ventana.after(0, detener_escribiendo)
                ventana.after(0, lambda: agregar_mensaje_ai(respuesta))
            
                # Verificar que la ventana existe antes de programar callbacks
                if ventana and ventana.winfo_exists():
                    callback_id1 = ventana.after(100, cargar_productos)
                    callback_id2 = ventana.after(100, lambda: entrada_nombre.delete(0, "end") if entrada_nombre.winfo_exists() else None)
                    callback_id3 = ventana.after(100, lambda: entrada_cantidad.delete(0, "end") if entrada_cantidad.winfo_exists() else None)
                    callback_id4 = ventana.after(100, lambda: entrada_precio.delete(0, "end") if entrada_precio.winfo_exists() else None)
                    callbacks_pendientes.extend([callback_id1, callback_id2, callback_id3, callback_id4])
            
            except Exception as e:
                logger.error(f"✗ Error al procesar mensaje: {type(e).__name__}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Programar actualización de UI en el thread principal
                ventana.after(0, detener_escribiendo)
                ventana.after(0, lambda: agregar_mensaje_sistema(f"Error: {str(e)}"))
            finally:
                # Programar actualización del botón en el thread principal
                if ventana and ventana.winfo_exists():
                    ventana.after(0, lambda: btn_enviar.configure(state="normal", text="Enviar") if btn_enviar and btn_enviar.winfo_exists() else None)
    
        thread = threading.Thread(target=procesar, daemon=True)
        thread.start()

    # Bind Enter para enviar mensaje
    entrada_chat.bind("<Return>", lambda e: enviar_mensaje_chat())

    # Inicializar Gemini en segundo plano (sin mensajes visibles)
    inicializar_gemini()

    # Cargar productos iniciales
    logger.info("Cargando productos iniciales...")
    cargar_productos()
    logger.info("Interfaz completamente inicializada")
    
    return ventana

def actualizar_usuario():
    global usuario_actual, label_usuario
    if usuario_actual:
        nombre = usuario_actual.get('nombre_completo') or usuario_actual.get('usuario')
        label_usuario.configure(text=f"👤 {nombre}")

