import customtkinter as ctk
from database import auth_unified as auth

class VentanaLogin:
    def __init__(self):
        self.ventana = ctk.CTk()
        self.ventana.title("GameStock | Iniciar Sesión")
        self.ventana.geometry("450x600")
        self.ventana.resizable(False, False)
        
        # Centrar ventana
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
        
        self.usuario_logueado = None
        self.callbacks_pendientes = []  # Para rastrear callbacks
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal
        frame_principal = ctk.CTkFrame(self.ventana, corner_radius=20)
        frame_principal.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo/Título
        titulo = ctk.CTkLabel(
            frame_principal,
            text="🎮 GameStock",
            font=("Arial", 36, "bold"),
            text_color="#4FC3F7"
        )
        titulo.pack(pady=(30, 10))
        
        subtitulo = ctk.CTkLabel(
            frame_principal,
            text="Sistema de Inventario",
            font=("Arial", 14),
            text_color="#888888"
        )
        subtitulo.pack(pady=(0, 40))
        
        # Frame de login/registro
        self.frame_contenido = ctk.CTkFrame(frame_principal, fg_color="transparent")
        self.frame_contenido.pack(fill="both", expand=True, padx=20)
        
        # Mostrar formulario de login por defecto
        self.mostrar_login()
    
    def limpiar_frame(self):
        """Limpia el frame de contenido"""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
    
    def mostrar_login(self):
        """Muestra el formulario de inicio de sesión"""
        self.limpiar_frame()
        
        # Campo Usuario
        ctk.CTkLabel(
            self.frame_contenido,
            text="Usuario",
            font=("Arial", 12)
        ).pack(anchor="w", pady=(10, 5))
        
        self.entrada_usuario_login = ctk.CTkEntry(
            self.frame_contenido,
            height=40,
            font=("Arial", 12),
            placeholder_text="Ingresa tu usuario"
        )
        self.entrada_usuario_login.pack(fill="x", pady=(0, 15))
        
        # Campo Contraseña
        ctk.CTkLabel(
            self.frame_contenido,
            text="Contraseña",
            font=("Arial", 12)
        ).pack(anchor="w", pady=(0, 5))
        
        self.entrada_password_login = ctk.CTkEntry(
            self.frame_contenido,
            height=40,
            font=("Arial", 12),
            placeholder_text="Ingresa tu contraseña",
            show="●"
        )
        self.entrada_password_login.pack(fill="x", pady=(0, 10))
        
        # Mensaje de error/éxito
        self.label_mensaje_login = ctk.CTkLabel(
            self.frame_contenido,
            text="",
            font=("Arial", 11),
            text_color="#F44336"
        )
        self.label_mensaje_login.pack(pady=10)
        
        # Botón de login
        btn_login = ctk.CTkButton(
            self.frame_contenido,
            text="Iniciar Sesión",
            command=self.hacer_login,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        btn_login.pack(fill="x", pady=(10, 20))
        
        # Separador
        ctk.CTkLabel(
            self.frame_contenido,
            text="─────────  o  ─────────",
            text_color="#666666"
        ).pack(pady=10)
        
        # Botón cambiar a registro
        btn_registro = ctk.CTkButton(
            self.frame_contenido,
            text="Crear Nueva Cuenta",
            command=self.mostrar_registro,
            height=40,
            font=("Arial", 12),
            fg_color="transparent",
            border_width=2,
            border_color="#4FC3F7",
            hover_color="#2d2d2d"
        )
        btn_registro.pack(fill="x")
        
        # Bind Enter
        self.entrada_password_login.bind("<Return>", lambda e: self.hacer_login())
    
    def mostrar_registro(self):
        """Muestra el formulario de registro"""
        self.limpiar_frame()
        
        # Campo Nombre Completo
        ctk.CTkLabel(
            self.frame_contenido,
            text="Nombre Completo",
            font=("Arial", 12)
        ).pack(anchor="w", pady=(10, 5))
        
        self.entrada_nombre = ctk.CTkEntry(
            self.frame_contenido,
            height=40,
            font=("Arial", 12),
            placeholder_text="Tu nombre completo"
        )
        self.entrada_nombre.pack(fill="x", pady=(0, 15))
        
        # Campo Usuario
        ctk.CTkLabel(
            self.frame_contenido,
            text="Usuario",
            font=("Arial", 12)
        ).pack(anchor="w", pady=(0, 5))
        
        self.entrada_usuario_registro = ctk.CTkEntry(
            self.frame_contenido,
            height=40,
            font=("Arial", 12),
            placeholder_text="Elige un nombre de usuario"
        )
        self.entrada_usuario_registro.pack(fill="x", pady=(0, 15))
        
        # Campo Contraseña
        ctk.CTkLabel(
            self.frame_contenido,
            text="Contraseña",
            font=("Arial", 12)
        ).pack(anchor="w", pady=(0, 5))
        
        self.entrada_password_registro = ctk.CTkEntry(
            self.frame_contenido,
            height=40,
            font=("Arial", 12),
            placeholder_text="Crea una contraseña segura",
            show="●"
        )
        self.entrada_password_registro.pack(fill="x", pady=(0, 10))
        
        # Mensaje de error/éxito
        self.label_mensaje_registro = ctk.CTkLabel(
            self.frame_contenido,
            text="",
            font=("Arial", 11),
            text_color="#F44336"
        )
        self.label_mensaje_registro.pack(pady=10)
        
        # Botón de registro
        btn_crear = ctk.CTkButton(
            self.frame_contenido,
            text="Crear Cuenta",
            command=self.hacer_registro,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        btn_crear.pack(fill="x", pady=(10, 20))
        
        # Botón volver al login
        btn_volver = ctk.CTkButton(
            self.frame_contenido,
            text="← Volver al Login",
            command=self.mostrar_login,
            height=40,
            font=("Arial", 12),
            fg_color="transparent",
            hover_color="#2d2d2d"
        )
        btn_volver.pack(fill="x")
        
        # Bind Enter
        self.entrada_password_registro.bind("<Return>", lambda e: self.hacer_registro())
    
    def hacer_login(self):
        """Procesa el inicio de sesión"""
        usuario = self.entrada_usuario_login.get().strip()
        password = self.entrada_password_login.get().strip()
        
        if not usuario or not password:
            self.label_mensaje_login.configure(
                text="⚠ Por favor completa todos los campos",
                text_color="#FF9800"
            )
            return
        
        exito, resultado = auth.verificar_login(usuario, password)
        
        if exito:
            self.usuario_logueado = resultado
            self.ventana.quit()
            self.ventana.destroy()
        else:
            self.label_mensaje_login.configure(
                text=f"✗ {resultado}",
                text_color="#F44336"
            )
    
    def hacer_registro(self):
        """Procesa el registro de usuario"""
        nombre = self.entrada_nombre.get().strip()
        usuario = self.entrada_usuario_registro.get().strip()
        password = self.entrada_password_registro.get().strip()
        
        if not usuario or not password:
            self.label_mensaje_registro.configure(
                text="⚠ Usuario y contraseña son obligatorios",
                text_color="#FF9800"
            )
            return
        
        if len(password) < 4:
            self.label_mensaje_registro.configure(
                text="⚠ La contraseña debe tener al menos 4 caracteres",
                text_color="#FF9800"
            )
            return
        
        exito, mensaje = auth.registrar_usuario(usuario, password, nombre)
        
        if exito:
            self.label_mensaje_registro.configure(
                text="✓ Cuenta creada! Iniciando sesión...",
                text_color="#4CAF50"
            )
            # Esperar 1 segundo y hacer login automático
            def auto_login():
                try:
                    # Verificar que la ventana aún existe
                    if self.ventana and self.ventana.winfo_exists():
                        exito_login, resultado = auth.verificar_login(usuario, password)
                        if exito_login:
                            self.usuario_logueado = resultado
                            self.ventana.quit()
                            self.ventana.destroy()
                except:
                    pass
            
            # Verificar que la ventana existe antes de programar el callback
            if self.ventana and self.ventana.winfo_exists():
                callback_id = self.ventana.after(1000, auto_login)
                self.callbacks_pendientes.append(callback_id)
        else:
            self.label_mensaje_registro.configure(
                text=f"✗ {mensaje}",
                text_color="#F44336"
            )
    
    def ejecutar(self):
        """Ejecuta la ventana de login"""
        try:
            self.ventana.mainloop()
        finally:
            # Cancelar callbacks pendientes al cerrar
            for callback_id in self.callbacks_pendientes:
                try:
                    self.ventana.after_cancel(callback_id)
                except:
                    pass
            self.callbacks_pendientes.clear()
        
        return self.usuario_logueado
