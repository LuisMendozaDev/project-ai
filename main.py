import shutil
import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow,  QTableView, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog, QSizePolicy,  QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.uic import loadUi
from PIL import Image
from landingai.predict import Predictor
from landingai.visualize import overlay_predictions, overlay_bboxes
from PyQt5.QtGui import QPixmap


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        loadUi("ia_interface.ui", self)
        global image_width
        self.car_count  = 0
        self.moto_count = 0 
        self.truck_count = 0 
        self.bus_count = 0 
        self.van_count =0 
        image_width = 1000
        self.lista_imagenes = self.obtener_lista_imagenes()

        self.indice_actual = 0

        self.bt_upload.clicked.connect(self.cargar_imagen)
        self.bt_process.clicked.connect(self.process_image)
        self.bt_right.clicked.connect(self.go_next)
        self.bt_left.clicked.connect(self.go_previous)

        self.mostrar_imagen_actual()
        self.llenar_tabla()

    def cargar_imagen(self):
        opciones = QFileDialog.Options()
        # opciones |= QFileDialog.DontUseNativeDialog
        ruta_imagen, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.gif);;Todos los archivos (*)", options=opciones)
        if ruta_imagen:
            self.ruta_imagen_actual = ruta_imagen
            pixmap = QPixmap(self.ruta_imagen_actual)
            if not pixmap.isNull():  # Verifica que la imagen se haya cargado correctamente
                pixmap = pixmap.scaledToWidth(image_width)
                self.image.setPixmap(pixmap)
                self.guardar_imagen()

    def guardar_imagen(self):
        if self.ruta_imagen_actual:
            nombre_archivo = os.path.basename(self.ruta_imagen_actual)
            ruta_destino = os.path.join("images", nombre_archivo)
            shutil.copyfile(self.ruta_imagen_actual, ruta_destino)
            print(f"Imagen guardada en: {ruta_destino}")
            self.lista_imagenes = self.obtener_lista_imagenes()
    
    def llenar_tabla(self):
        # Crear el modelo de la tabla
        modelo = QStandardItemModel(self)
        # Ocultar los encabezados de las filas
        self.info_table.verticalHeader().setVisible(False)

        # Configurar el tamaño de política para la QTableView y el QVBoxLayout
        # self.info_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.info_table.setSizeAdjustPolicy(QTableView.AdjustToContents)
        # self.info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Ajusta la primera columna
        # self.info_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Ajusta la segunda columna

        # Agregar encabezados
        modelo.setHorizontalHeaderLabels(["Object", "Number"])

        # Datos de ejemplo
        datos = [("Car",  self.car_count),
                 ("Motorcycle", self.moto_count),
                 ("Truck", self.truck_count),
                 ("Bus", self.bus_count),
                 ("van ", self.van_count)]

        # Llenar la tabla con los datos
        for fila, (texto, numero) in enumerate(datos):
            item_texto = QStandardItem(texto)
            item_numero = QStandardItem(str(numero))  # Convertir el número a cadena
            modelo.appendRow([item_texto, item_numero])

        # Establecer el modelo en la QTableView
        self.info_table.setModel(modelo)

    def process_image(self):
        # Enter your API Key
        endpoint_id = "3c422a48-b6de-4170-b2a7-8ab9368d435c"
        api_key = "land_sk_bqkwlrXNHYqAWGtJ7axFuixyOjthXf6sKCOL5bPqIgfLoqsSll"
        # Abre una imagen existente

        # Load your image
        image = Image.open(self.ruta_imagen_actual)
        self.car_count = 0
        self.moto_count = 0
        self.truck_count = 0
        self.bus_count = 0
        self.van_count = 0

        # Run inference
        predictor = Predictor(endpoint_id, api_key=api_key)
        predictions = predictor.predict(image)
        for prediction in predictions:
            print(prediction)
            if(prediction.label_name == "car"):
                self.car_count += 1
            elif(prediction.label_name == "motorcycle"):
                self.moto_count += 1
            elif(prediction.label_name == "truck"):
                self.truck_count += 1
            elif(prediction.label_name == "bus"):
                self.bus_count += 1
            else: 
                self.van_count += 1
        self.llenar_tabla()
        color_dict = {"car": "red", "truck":"blue", "motorcycle":"green", "bus":"pink", "van":"cyan"}
        # Draw raw results on the original image
        frame_with_preds = overlay_predictions(predictions, image=image)

        frame_with_preds.save("tmp/image_with_result.jpg")
        # Define las nuevas dimensiones (ancho x alto)

        # Carga la imagen usando QPixmap
        # Reemplaza con la ruta de tu imagen
        result_image_path = "tmp/image_with_result.jpg"
        pixmap = QPixmap(result_image_path)
        pixmap = pixmap.scaledToWidth(image_width)

        # Crea un QLabel y establece la imagen en él

        self.image.setPixmap(pixmap)

    def obtener_lista_imagenes(self):
        archivos = os.listdir("images")
        imagenes = [archivo for archivo in archivos if archivo.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.gif'))]
        return imagenes

    def mostrar_imagen_actual(self):
        if 0 <= self.indice_actual < len(self.lista_imagenes):
            self.ruta_imagen_actual = os.path.join(
                "images", self.lista_imagenes[self.indice_actual])
            pixmap = QPixmap(self.ruta_imagen_actual)
            pixmap = pixmap.scaledToWidth(image_width)
            self.image.setPixmap(pixmap)
            self.setWindowTitle(
                f"Visor de Imágenes - {self.lista_imagenes[self.indice_actual]}")

    def go_next(self):
        self.indice_actual += 1
        if self.indice_actual >= len(self.lista_imagenes):
            self.indice_actual = 0
        self.mostrar_imagen_actual()

    def go_previous(self):
        self.indice_actual -= 1
        if self.indice_actual < 0:
            self.indice_actual = len(self.lista_imagenes) - 1
        self.mostrar_imagen_actual()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
