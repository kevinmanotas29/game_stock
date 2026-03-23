from gui.login import VentanaLogin
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Iniciando GameStock...")

# Mostrar ventana de login
logger.info("Mostrando ventana de login...")
login = VentanaLogin()
usuario = login.ejecutar()

# Si el usuario se logueó correctamente, abrir la aplicación principal
if usuario:
    logger.info(f"Usuario logueado: {usuario['nombre_completo'] or usuario['usuario']}")
    print(f"✓ Bienvenido {usuario['nombre_completo'] or usuario['usuario']}")
    
    # Importar la interfaz DESPUÉS del login para evitar que se cree antes
    logger.info("Cargando interfaz principal...")
    from gui import interfaz
    interfaz.inicializar_interfaz()
    interfaz.usuario_actual = usuario
    interfaz.actualizar_usuario()
    logger.info("Interfaz principal inicializada")
    interfaz.ventana.mainloop()
    logger.info("Aplicación cerrada por el usuario")
else:
    logger.warning("Login cancelado por el usuario")
    print("Login cancelado")

logger.info("GameStock finalizado")
