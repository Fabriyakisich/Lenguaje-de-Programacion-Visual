# Fernando Arréllaga 4695843

import paramiko

def connect_to_raspberry_pi(hostname, username, password, command):
    try:
        # Crear un cliente SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Conectar al Raspberry Pi
        print(f"Conectando a {hostname}...")
        client.connect(hostname, username=username, password=password)
        print("Conexión exitosa.")
        
        # Ejecutar un comando remoto
        stdin, stdout, stderr = client.exec_command(command)
        print("Salida del comando:")
        print(stdout.read().decode())
        print("Errores (si los hay):")
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error al conectar: {e}")
    finally:
        client.close()
        print("Conexión cerrada.")

# Configuración
hostname = "172.16.232.76"  # Cambia esto por la IP de tu Raspberry Pi
username = "pi"             # Cambia esto por el usuario de tu Raspberry Pi
password = "raspberry"      # Cambia esto por la contraseña de tu Raspberry Pi

while True:
    command = input("Introduce un comando para ejecutar en la Raspberry Pi (o 'exit' para salir): ")
    if command.lower() == 'exit':
        print("Saliendo...")
        break
    if not command.strip():
        print("Por favor, introduce un comando válido.")
        continue
    # Validar el comando para evitar inyecciones de comandos
    if any(char in command for char in [';', '&', '|', '`', '$', '>', '<']):
        print("Comando no permitido por razones de seguridad.")
        continue
    # Ejecutar el comando
    connect_to_raspberry_pi(hostname, username, password, command)


# Lista de comandos que puedes ejecutar en tu Raspberry Pi:

# 1. "ls"
#    Descripción: Lista los archivos y directorios en el directorio actual.
#    Ejemplo: "ls"

# 2. "pwd"
#    Descripción: Muestra el directorio de trabajo actual.
#    Ejemplo: "pwd"

# 3. "df -h"
#    Descripción: Muestra el uso del disco en formato legible para humanos.
#    Ejemplo: "df -h"

# 4. "free -m"
#    Descripción: Muestra el uso de la memoria en megabytes.
#    Ejemplo: "free -m"

# 5. "uname -a"
#    Descripción: Muestra información sobre el sistema operativo.
#    Ejemplo: "uname -a"

# 6. "top"
#    Descripción: Muestra los procesos en ejecución y el uso de recursos en tiempo real.
#    Ejemplo: "top"

# 7. "cat /proc/cpuinfo"
#    Descripción: Muestra información sobre la CPU.
#    Ejemplo: "cat /proc/cpuinfo"

# 8. "cat /proc/meminfo"
#    Descripción: Muestra información sobre la memoria del sistema.
#    Ejemplo: "cat /proc/meminfo"

# 9. "ifconfig"
#    Descripción: Muestra información sobre las interfaces de red.
#    Ejemplo: "ifconfig"

# 10. "reboot"
#     Descripción: Reinicia el Raspberry Pi.
#     Ejemplo: "reboot"

# 11. "sudo shutdown now"
#     Descripción: Apaga el Raspberry Pi de forma inmediata.
#     Ejemplo: "sudo shutdown now"

# Crear un archivo .txt con contenido "FFF"

# Nota: Algunos comandos pueden requerir permisos de superusuario (sudo).

## Comandos de profe:
# 1. "pwd" # Muestra el directorio actual
# 2. "ls"  # Lista los archivos y carpetas en el directorio actual
# 3. "cd Downloads" # Cambia al directorio Downloads
# 4. "cd .."
#    Descripción: Cambia al directorio anterior (directorio padre).
#    Ejemplo: "cd .."
# 5. "mkdir nueva_carpeta" # Crea una nueva carpeta llamada nueva_carpeta
# 6. "rm -rf nueva_carpeta" # Elimina la carpeta nueva_carpeta y su contenido
# 7. "touch nuevo_archivo.txt" # Crea un nuevo archivo llamado nuevo_archivo.txt
# 8. "rm nuevo_archivo.txt" # Elimina el archivo nuevo_archivo.txt
# 9. "nano archivo.txt" # Abre el editor de texto nano para editar archivo.txt
# 10. "cat archivo.txt" # Muestra el contenido del archivo archivo.txt
# 11. "scp archivo.txt pi@

# 12. "nano archivo.txt" # Abre el editor de texto nano para editar archivo.txt
#     Descripción: Abre el editor de texto nano para editar un archivo.
#     Ejemplo: "nano archivo.txt"

