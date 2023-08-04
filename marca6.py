import cv2
import numpy as np
import os
from moviepy.editor import VideoFileClip

def listar_archivos_multimedia(carpeta):
    archivos_multimedia = []
    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.avi')):
            archivos_multimedia.append(archivo)
    return archivos_multimedia

def agregar_marca_de_agua(archivo_multimedia, nivel_difuminado, cantidad_marcas_fotos, cantidad_marcas_videos, modificar_archivo_original):
    marca_de_agua = "@G0ST_404"
    _, extension = os.path.splitext(archivo_multimedia)

    if extension.lower() in ('.jpg', '.jpeg', '.png'):
        imagen = cv2.imread(archivo_multimedia)
        altura, ancho = imagen.shape[:2]

        # Definir el tamaño y el tipo de fuente de la marca de agua
        fuente = cv2.FONT_HERSHEY_DUPLEX
        escala_fuente = 2
        grosor_fuente = 2
        tamaño_texto, _ = cv2.getTextSize(marca_de_agua, fuente, escala_fuente, grosor_fuente)

        # Calcular el número de marcas de agua por fila y columna
        marcas_por_fila = int(np.sqrt(cantidad_marcas_fotos))
        marcas_por_columna = int(np.ceil(cantidad_marcas_fotos / marcas_por_fila))

        # Calcular el tamaño de cada región
        region_ancho = ancho // marcas_por_fila
        region_alto = altura // marcas_por_columna

        # Crear una imagen en blanco con el mismo tamaño que la original
        marca_de_agua_imagen = np.zeros_like(imagen, dtype=np.uint8)

        # Escribir la marca de agua en una posición aleatoria dentro de cada región
        for fila in range(marcas_por_columna):
            for columna in range(marcas_por_fila):
                x_random = np.random.randint(columna * region_ancho, (columna + 1) * region_ancho - tamaño_texto[0])
                y_random = np.random.randint(fila * region_alto + tamaño_texto[1], (fila + 1) * region_alto)
                cv2.putText(marca_de_agua_imagen, marca_de_agua, (x_random, y_random), fuente, escala_fuente, (255, 255, 255), grosor_fuente)

        # Difuminar la marca de agua con el nivel seleccionado
        sigma = nivel_difuminado * 2.5
        marca_de_agua_imagen = cv2.GaussianBlur(marca_de_agua_imagen, (0, 0), sigmaX=sigma, sigmaY=sigma)

        # Combinar la marca de agua con la imagen original
        resultado = cv2.addWeighted(imagen, 1, marca_de_agua_imagen, 0.5, 0)

        # Guardar el resultado en un nuevo archivo
        carpeta_salida = os.path.join(os.path.dirname(archivo_multimedia), "con_marca_de_agua")
        os.makedirs(carpeta_salida, exist_ok=True)
        nombre_archivo, _ = os.path.splitext(os.path.basename(archivo_multimedia))
        archivo_salida = os.path.join(carpeta_salida, f"{nombre_archivo}_con_marca{extension}")
        cv2.imwrite(archivo_salida, resultado)

        # Sobrescribir el archivo original si es necesario
        if modificar_archivo_original:
            os.remove(archivo_multimedia)
            os.rename(archivo_salida, archivo_multimedia)

    elif extension.lower() in ('.mp4', '.avi'):
        video = VideoFileClip(archivo_multimedia)
        duracion = video.duration

        # Solicitud al usuario si desea que la marca de agua esté estática en el centro
        mantener_estatica = input("¿Deseas que la marca de agua esté estática en el centro? (si/no): ").lower() == 'si'
        if mantener_estatica:
            cantidad_marcas_videos = 1  # Solo se agregará una marca de agua estática en el centro

        # Crear una función para agregar la marca de agua a cada frame del video
        def agregar_marca(frame):
            fuente = cv2.FONT_HERSHEY_DUPLEX
            escala_fuente = 2
            grosor_fuente = 2
            tamaño_texto, _ = cv2.getTextSize(marca_de_agua, fuente, escala_fuente, grosor_fuente)

            # Calcular el número de marcas de agua por fila y columna
            marcas_por_fila = int(np.sqrt(cantidad_marcas_videos))
            marcas_por_columna = int(np.ceil(cantidad_marcas_videos / marcas_por_fila))

            # Calcular el tamaño de cada región
            region_ancho = frame.shape[1] // marcas_por_fila
            region_alto = frame.shape[0] // marcas_por_columna

            # Crear una imagen en blanco con el mismo tamaño que el frame
            marca_de_agua_imagen = np.zeros_like(frame, dtype=np.uint8)

            # Escribir la marca de agua en una posición aleatoria dentro de cada región
            if mantener_estatica:
                # Posicionar la marca de agua en el centro del frame
                x_center = (frame.shape[1] - tamaño_texto[0]) // 2
                y_center = (frame.shape[0] + tamaño_texto[1]) // 2
                cv2.putText(marca_de_agua_imagen, marca_de_agua, (x_center, y_center), fuente, escala_fuente, (255, 255, 255), grosor_fuente)
            else:
                for fila in range(marcas_por_columna):
                    for columna in range(marcas_por_fila):
                        x_random = np.random.randint(columna * region_ancho, (columna + 1) * region_ancho - tamaño_texto[0])
                        y_random = np.random.randint(fila * region_alto + tamaño_texto[1], (fila + 1) * region_alto)
                        cv2.putText(marca_de_agua_imagen, marca_de_agua, (x_random, y_random), fuente, escala_fuente, (255, 255, 255), grosor_fuente)

            # Difuminar la marca de agua con el nivel seleccionado
            sigma = nivel_difuminado * 2.5
            marca_de_agua_imagen = cv2.GaussianBlur(marca_de_agua_imagen, (0, 0), sigmaX=sigma, sigmaY=sigma)

            # Combinar la marca de agua con el frame original
            resultado = cv2.addWeighted(frame, 1, marca_de_agua_imagen, 0.5, 0)

            return resultado

        # Procesar cada frame del video y agregar la marca de agua
        video_con_marca = video.fl_image(agregar_marca)

        # Guardar el video resultante en un nuevo archivo
        carpeta_salida = os.path.join(os.path.dirname(archivo_multimedia), "con_marca_de_agua")
        os.makedirs(carpeta_salida, exist_ok=True)
        nombre_archivo, _ = os.path.splitext(os.path.basename(archivo_multimedia))
        archivo_salida = os.path.join(carpeta_salida, f"{nombre_archivo}_con_marca{extension}")
        video_con_marca.write_videofile(archivo_salida, codec='libx264')

        # Sobrescribir el archivo original si es necesario
        if modificar_archivo_original:
            video.reader.close()
            video.audio.reader.close_proc()
            os.remove(archivo_multimedia)
            os.rename(archivo_salida, archivo_multimedia)

# Solicitud de la carpeta y listado de archivos multimedia disponibles
carpeta = input("Por favor, introduce la ruta de la carpeta con los archivos multimedia: ")
archivos_disponibles = listar_archivos_multimedia(carpeta)

# Mostrar la lista de archivos multimedia disponibles al usuario
print("Archivos multimedia disponibles:")
for i, archivo in enumerate(archivos_disponibles, start=1):
    print(f"{i}. {archivo}")

# Solicitud del nivel de difuminado de la marca de agua
nivel_difuminado_input = input("Ingresa el nivel de difuminado de la marca de agua (1 al 10) [Deja en blanco para predeterminado]: ")
if nivel_difuminado_input:
    nivel_difuminado = int(nivel_difuminado_input)
    nivel_difuminado = max(1, min(10, nivel_difuminado))  # Asegurar que el valor esté entre 1 y 10
else:
    nivel_difuminado = 5  # Valor predeterminado

# Solicitud de la cantidad de marcas de agua para las fotos y los videos
cantidad_marcas_fotos = int(input("Selecciona la cantidad de marcas de agua para las fotos (1: 1 sola marca, 2: cantidad intermedia, 3: muchas marcas): "))
cantidad_marcas_videos = int(input("Selecciona la cantidad de marcas de agua para los videos (1: 1 sola marca, 2: cantidad intermedia, 3: muchas marcas): "))

# Solicitud de selección de opción por parte del usuario
print("Selecciona una opción:")
print("1. Agregar marca de agua a todos los archivos de la carpeta")
print("2. Agregar marca de agua solo a los archivos de video de la carpeta")
print("3. Agregar marca de agua solo a los archivos de fotos de la carpeta")
print("4. Agregar marca de agua a un solo archivo")
opcion = int(input("Ingrese el número de la opción: "))

if opcion == 1:
    # Agregar marca de agua a todos los archivos de la carpeta
    modificar_archivo_original = input("¿Deseas modificar los archivos originales? (si/no): ").lower() == 'si'
    for archivo in archivos_disponibles:
        archivo_multimedia = os.path.join(carpeta, archivo)
        if archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
            agregar_marca_de_agua(archivo_multimedia, nivel_difuminado, cantidad_marcas_fotos, cantidad_marcas_videos, modificar_archivo_original)
        elif archivo.lower().endswith(('.mp4', '.avi')):
            agregar_marca_de_agua(archivo_multimedia, nivel_difuminado, cantidad_marcas_fotos, cantidad_marcas_videos, modificar_archivo_original)
elif opcion == 2:
    # Agregar marca de agua solo a los archivos de video de la carpeta
    modificar_archivo_original = input("¿Deseas modificar los archivos originales? (si/no): ").lower() == 'si'
    for archivo in archivos_disponibles:
        if archivo.lower().endswith(('.mp4', '.avi')):
            archivo_multimedia = os.path.join(carpeta, archivo)
            agregar_marca_de_agua(archivo_multimedia, nivel_difuminado, 1, cantidad_marcas_videos, modificar_archivo_original)
elif opcion == 3:
    # Agregar marca de agua solo a los archivos de fotos de la carpeta
    modificar_archivo_original = input("¿Deseas modificar los archivos originales? (si/no): ").lower() == 'si'
    for archivo in archivos_disponibles:
        if archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
            archivo_multimedia = os.path.join(carpeta, archivo)
            agregar_marca_de_agua(archivo_multimedia, nivel_difuminado, cantidad_marcas_fotos, 1, modificar_archivo_original)
elif opcion == 4:
    # Agregar marca de agua a un solo archivo
    archivo_seleccionado = int(input("Selecciona el número del archivo multimedia para agregar la marca de agua: "))
    if 1 <= archivo_seleccionado <= len(archivos_disponibles):
        archivo_multimedia = os.path.join(carpeta, archivos_disponibles[archivo_seleccionado - 1])
        modificar_archivo_original = input("¿Deseas modificar el archivo original? (si/no): ").lower() == 'si'
        agregar_marca_de_agua(archivo_multimedia, nivel_difuminado, cantidad_marcas_fotos, cantidad_marcas_videos, modificar_archivo_original)
    else:
        print("Opción inválida. Por favor, selecciona un número de archivo válido.")
else:
    print("Opción inválida. Por favor, selecciona una opción válida.")
