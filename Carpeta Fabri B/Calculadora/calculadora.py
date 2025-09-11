import tkinter as tk

def calculadora():
    # Inicializamos la ventana principal
    root = tk.Tk()
    root.title("Calculadora Simple - Tkinter LPV")
    root.geometry("300x400")

    # Entry para mostrar los números y resultados
    # width para los caracteres, font para el tamaño y tipo de letra,
    # borderwidth y relief para el estilo del borde, justify para alinear los numeros a la derecha
    entrada = tk.Entry(root, width=16, font=('Arial', 24), borderwidth=2, relief='ridge', justify='right')
    # Acomoda la entrada en la cuadrícula. Es como una caja invisble que contiene la entrada
    # row y column para la posición, columnspan para que ocupe varias columnas
    entrada.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    # Función para manejar los botones
    def agregar_numero(numero):
        # Leemos la entrada actual
        actual = entrada.get()
        # Limpiamos la entrada y agregamos el nuevo número
        entrada.delete(0, tk.END)
        # Concatenamos el número presionado
        entrada.insert(0, actual + str(numero))

    # Función para limpiar la entrada
    def limpiar():
        # Limpiamos la entrada
        entrada.delete(0, tk.END)

    # Función para calcular el resultado
    def calcular():
        # Evaluamos la expresión en la entrada
        try:
            # Evaluamos la expresión y mostramos el resultado
            # Usamos eval para calcular la expresión ingresada
            resultado = eval(entrada.get())
            # Limpiamos la entrada
            entrada.delete(0, tk.END)
            # Insertamos el resultado en la entrada
            # Convertimos el resultado a string para mostrarlo
            entrada.insert(0, str(resultado))
        # Si hay un error en la evaluación, mostramos un mensaje de error
        except Exception as e:
            entrada.delete(0, tk.END)
            entrada.insert(0, "Error")

    # Botones de la calculadora
    # Definimos los botones y su disposición en la cuadrícula
    # Cada botón tiene un texto, una fila y una columna
    botones = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
        ('0', 4, 0), ('.', 4, 1), ('C', 4, 2), ('+', 4, 3),
        ('=', 5, 0, 4)
    ]

    # Normaliza cada tupla a 4 elementos
    # Si la tupla no tiene 4 elementos, agrega 1 como colspan por defecto
    for (text, row, col, colspan) in [(b[0], b[1], b[2], b[3] if len(b) > 3 else 1) for b in botones]:
        # Define la acción del botón según su texto
        if text == 'C':
            action = limpiar
        elif text == '=':
            action = calcular
        else:
            # Else en caso de que sea un número o un operador
            action = lambda x=text: agregar_numero(x)
        # Creamos el botón y lo colocamos en la cuadrícula
        # width y height para el tamaño del botón, command para la acción al hacer click
        tk.Button(root, text=text, width=5, height=2, command=action).grid(row=row, column=col, columnspan=colspan)

    root.mainloop() 
calculadora()