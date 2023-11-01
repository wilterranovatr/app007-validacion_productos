## Modulo 1 : Verificación de todos los productos emitidos existentes
from functions.api_dynamics import ApiDynamics
import shutil
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
from functions.enviar_correos import EnviarCorreos
import pandas as pd

class Modulo1:
    
    api = None
    
    def __init__(self) -> None:
        pass
    
    def Start(self):
        
        self.api = ApiDynamics()
        
        print("-- Iniciando proceso de verificación MODULO 1")
        ##
        bar_code = pd.DataFrame({})
        unit = pd.DataFrame({})
        unit_eq = pd.DataFrame({})
        sunat = pd.DataFrame({})
        provider = pd.DataFrame({})
        catalogo = pd.DataFrame({})
        traduc1 = pd.DataFrame({})
        traduc2 = pd.DataFrame({})
        traduc3 = pd.DataFrame({})
        ###
        tipo_verificacion = []
        
        ## Verificando codigo de barras
        print("-- Verificando codigo de barras")
        try:
            bar_code = self.api.verifyExistsBarCode()
        except:
            print("ERROR: Ocurrió un error al momento de verificar los codigos de barra")
        
        ## Verificando unidades de conversion
        print("-- Verificando codigo unidades de conversión")
        try:
            unit = self.api.verifyUnitSymbol()
        except:
            print("ERROR: Ocurrió un error al momento de verificar la unidades de conversion")
        
        ## Verificando unidades de conversion - equivalencias
        print("-- Verificando codigo unidades de conversión")
        try:
            unit_eq = self.api.verifyEquiUnitSymbol()
        except:
            print("ERROR: Ocurrió un error al momento de verificar la unidades de conversion - equivalencias")
        
        ## Verificando codigo sunat
        print("-- Verificando codigo SUNAT")
        try:
            sunat = self.api.verifyCodeSunat()
        except Exception as e:
            print("ERROR: Ocurrió un error al momento de verificar el codigo SUNAT")
            print(e)
            
        ## Verificando codigo proveedor
        print("-- Verificando asignacion de proveedores")
        try:
            provider = self.api.verifyAssignProvider()
        except:
            print("ERROR: Ocurrió un error al momento de verificar asignacion de proveedores")
            
        ## Verificando catalogo de productos
        print("-- Verificando asignacion de catalogo de productos")
        try:
            catalogo = self.api.verifyCatalogVentas()
        except:
            print("ERROR: Ocurrió un error al momento de verificar la asignacion de categoria de productos")
            
        ## Verificando traducciones
        print("-- Verificando campos de traducciones")
        try:
            traduc1 = self.api.verifyTranslationProduct1()
        except:
            print("ERROR: Ocurrió un error al momento de verificar los campos de traducciones1")
        try:
            traduc2 = self.api.verifyTranslationProduct2()
        except Exception as e:
            print("ERROR: Ocurrió un error al momento de verificar los campos de traducciones2")
            print(e)
        try:
            traduc3 = self.api.verifyTranslationProduct3()
        except:
            print("ERROR: Ocurrió un error al momento de verificar los campos de traducciones2")
        
        ####
        seed_cell_excel = 10
        shutil.copy("./assets/model_reporte.xlsx",f"./temp/ReporteVerificacionProductos.xlsx")
        data_sheet = openpyxl.load_workbook(f"./temp/ReporteVerificacionProductos.xlsx")
        sheet = data_sheet.active
        sheet['C5']= datetime.now()
        ####
        colum_l=['D','E']
        count_f = 0
        ####
        if bar_code.empty != True:
            ##
            tipo_verificacion.append("BARCODE")
            ##
            rows = dataframe_to_rows(bar_code,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "ERROR EN CÓDIGO DE BARRAS"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1
        ####
        if unit.empty != True:
            ##
            tipo_verificacion.append("UNIT")
            ##
            rows = dataframe_to_rows(unit,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "ERROR EN UNIDADES DE CONVERSIÓN"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        ####
        if unit_eq.empty != True:
            ##
            tipo_verificacion.append("UNIT")
            ##
            rows = dataframe_to_rows(unit_eq,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        if count_c ==2:
                            sheet[f'C{num_row}'] = f"ERROR EN UNIDADES DE CONVERSIÓN - {str(value)}"
                        else:
                            sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        if sunat.empty != True:
            ##
            tipo_verificacion.append("SUNAT")
            ##
            rows = dataframe_to_rows(sunat,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "ERROR EN CÓDIGO SUNAT"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        if provider.empty != True:
            ##
            tipo_verificacion.append("PROVIDER")
            ##
            rows = dataframe_to_rows(provider,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "NO TIENE ASIGNADO PROVEEDOR"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        if catalogo.empty != True:
            ##
            tipo_verificacion.append("CATALOGO")
            ##
            rows = dataframe_to_rows(catalogo,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "NO TIENE ASIGNADO CATEGORÍA VENTAS"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        if traduc1.empty != True:
            ##
            if "TRANSLATION" not in tipo_verificacion:
                tipo_verificacion.append("TRANSLATION")
            ##
            rows = dataframe_to_rows(traduc1,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = 'SOLO TIENE TRADUCCIÓN PARA IDIOMA "ES-MX"'
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        if traduc2.empty != True:
            ##
            if "TRANSLATION" not in tipo_verificacion:
                tipo_verificacion.append("TRANSLATION")
            ##
            rows = dataframe_to_rows(traduc2,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = 'SOLO TIENE TRADUCCIÓN PARA IDIOMA "ES"'
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        if traduc3.empty != True:
            ##
            if "TRANSLATION" not in tipo_verificacion:
                tipo_verificacion.append("TRANSLATION")
            ##
            rows = dataframe_to_rows(traduc3,index=False)
            for r_i, row in enumerate(rows,1):
                if r_i != 1:
                    num_row = seed_cell_excel + count_f
                    sheet[f'B{num_row}'] = count_f+1
                    sheet[f'C{num_row}'] = "NO TIENE REGISTRADO NINGUNA TRADUCCIÓN"
                    count_c = 0
                    for c_i, value in enumerate(row,1):
                        sheet[f'{colum_l[count_c]}{num_row}'] = str(value)
                        count_c = count_c+1
                    count_f = count_f+1 
        ####
        data_sheet.save(f"./temp/ReporteVerificacionProductos.xlsx")
        ####
        if len(tipo_verificacion) != 0:
            p_attach = "./temp/ReporteVerificacionProductos.xlsx"
            correo = EnviarCorreos(tipo_verificacion,p_attach)
            correo.enviarCorreo()
        ####