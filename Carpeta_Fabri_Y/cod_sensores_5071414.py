import tkinter as tk
import serial
import serial.tools.list_ports

# ---------- Config ----------
POLL_MS = 100         # cada 100 ms leo el puerto
DEFAULT_BAUD = "9600" # baud por defecto
LINE_END = b'\n'      # fin de línea que manda el Arduino

# ---------- Estado global ----------
ser = None
rx_buffer = bytearray()

# ---------- Parser sencillo "K:V,K:V" ----------
def parse_line(line_str):
    # ejemplo: "PIR:1,LDR:523,REED:0,RELAY:0"
    data = {}
    for part in line_str.strip().split(','):
        if ':' in part:
            k, v = part.split(':', 1)
            data[k.strip().lower()] = v.strip()
    return data

# ---------- UI ----------
root = tk.Tk()
root.title("Cerradura - Sensores y Relé (Serial)")

# fila 0: puerto + botón actualizar
tk.Label(root, text="Puerto:").grid(row=0, column=0, sticky="e")
puerto_var = tk.StringVar()
puerto_entry = tk.Entry(root, textvariable=puerto_var, width=18)
puerto_entry.grid(row=0, column=1, sticky="w", padx=4)

def listar_puertos():
    puertos = [p.device for p in serial.tools.list_ports.comports()]
    if puertos:
        puerto_var.set(puertos[0])
    estado.set("Puertos: " + ", ".join(puertos) if puertos else "Sin puertos")
tk.Button(root, text="Actualizar puertos", command=listar_puertos).grid(row=0, column=2, padx=4)

# fila 1: baud + conectar
tk.Label(root, text="Baud:").grid(row=1, column=0, sticky="e")
baud_var = tk.StringVar(value=DEFAULT_BAUD)
tk.Entry(root, textvariable=baud_var, width=8).grid(row=1, column=1, sticky="w", padx=4)

estado = tk.StringVar(value="Desconectado")
tk.Label(root, textvariable=estado).grid(row=1, column=2, sticky="w")

def conectar():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(puerto_var.get(), int(baud_var.get()), timeout=0)
        estado.set("Conectado")
        root.after(POLL_MS, mostrar_datos)
    except Exception as e:
        estado.set(f"Error: {e}")

tk.Button(root, text="Conectar", command=conectar).grid(row=1, column=3, padx=4)

# fila 2-4: labels de sensores
pir_var   = tk.StringVar(value="—")
ldr_var   = tk.StringVar(value="—")
reed_var  = tk.StringVar(value="—")
relay_var = tk.StringVar(value="—")

row_base = 2
tk.Label(root, text="PIR (mov):").grid(row=row_base+0, column=0, sticky="e")
tk.Label(root, textvariable=pir_var).grid(row=row_base+0, column=1, sticky="w")

tk.Label(root, text="LDR (luz):").grid(row=row_base+1, column=0, sticky="e")
tk.Label(root, textvariable=ldr_var).grid(row=row_base+1, column=1, sticky="w")

tk.Label(root, text="Reed (puerta):").grid(row=row_base+2, column=0, sticky="e")
tk.Label(root, textvariable=reed_var).grid(row=row_base+2, column=1, sticky="w")

tk.Label(root, text="Relé:").grid(row=row_base+3, column=0, sticky="e")
tk.Label(root, textvariable=relay_var).grid(row=row_base+3, column=1, sticky="w")

# fila 6: texto crudo (log)
texto = tk.Text(root, height=10, width=60)
texto.grid(row=row_base+4, column=0, columnspan=4, pady=6)

# fila 7: botones abrir/cerrar
def send_cmd(cmd):
    if ser and ser.is_open:
        ser.write((cmd + "\n").encode())

tk.Button(root, text="Abrir",  command=lambda: send_cmd("OPEN")).grid(row=row_base+5, column=0, pady=4)
tk.Button(root, text="Cerrar", command=lambda: send_cmd("CLOSE")).grid(row=row_base+5, column=1, pady=4)

# ---------- Lectura periódica ----------
def mostrar_datos():
    if not (ser and ser.is_open):
        estado.set("Desconectado")
        return
    try:
        data = ser.read(ser.in_waiting or 1)
        if data:
            global rx_buffer
            rx_buffer.extend(data)
            # procesar líneas completas
            while True:
                idx = rx_buffer.find(LINE_END)
                if idx == -1:
                    break
                line = rx_buffer[:idx].decode(errors="ignore")
                del rx_buffer[:idx+1]
                # log crudo
                texto.insert("end", line + "\n")
                texto.see("end")
                # parse y actualizar labels
                parsed = parse_line(line)
                if 'pir' in parsed:
                    pir_var.set("Detectado" if parsed['pir'] == '1' else "Quieto")
                if 'ldr' in parsed:
                    l = parsed['ldr']
                    ldr_var.set(l)
                if 'reed' in parsed:
                    reed_var.set("Cerrada" if parsed['reed'] == '1' else "Abierta")
                if 'relay' in parsed:
                    relay_var.set("ON" if parsed['relay'] == '1' else "OFF")
    except Exception as e:
        estado.set(f"Error lectura: {e}")
    finally:
        root.after(POLL_MS, mostrar_datos)

# arranque
listar_puertos()
root.mainloop()