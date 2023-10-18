## Modulo 2 : Verificación de estado de los productos vendidos
from functions.api_dynamics import ApiDynamics
import shutil
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
from functions.enviar_correos import EnviarCorreos
import pandas as pd

class Modulo2:
    
    api = None

    def __init__(self) -> None:
        pass
    
    def Start(self):
        self.api = ApiDynamics()
        
        print("-- Iniciando proceso de verificación MODULO 2")
        ##
        status_product = pd.DataFrame({})
        ###
        tipo_verificacion = []
        
        ## Verificando estado de productos
        print("-- Verificando estado de productos")
        try:
            status_product = self.api.verifyProductsInStateActive()
        except:
            print("ERROR: Ocurrió un error al momento de verificar los codigos de barra")
        
        ####
        seed_cell_excel = 10
        shutil.copy("./assets/model_reporte.xlsx",f"./temp/ReporteEstadoProductos.xlsx")
        data_sheet = openpyxl.load_workbook(f"./temp/ReporteEstadoProductos.xlsx")
        sheet = data_sheet.active
        sheet['C5']= datetime.now()
        ####
        colum_l=['D','E']
        count_f = 0
        ####
        if status_product.empty != True:
            ##
            tipo_verificacion.append("STATUS_ACTIVE")
            ##
            rows = dataframe_to_rows(status_product,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "PRODUCTOS INACTIVOS VENDIDOS"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1
        ####
        data_sheet.save(f"./temp/ReporteEstadoProductos.xlsx")
        ####
        if len(tipo_verificacion) != 0:
            p_attach = "./temp/ReporteEstadoProductos.xlsx"
            correo = EnviarCorreos(tipo_verificacion,p_attach)
            correo.enviarCorreo()
        ####