import requests, json

class ApiDynamics:
    
    #Definiendo variables
    url =""
    username=""
    top=0
    extracto=""
    transaccion=""
    msg_error=""
    lista_productos={}
    productos=""
    
    #Inicializando 
    def __init__(self, i_url,i_username,i_top=0):
        self.url = i_url
        self.username= i_username
        self.top = i_top
    
    
    def get_Token(self):
        env = {
                "client_id":"53f3c906-9bfc-4a5d-89d8-30ce9a672481",
                "client_secret":"zNA3~9-5wuywwiflFbAP52cgJ_5wQ__Y48",
                "resource":f"{self.url}",
                "grant_type":"client_credentials"
            }
        endp = 'https://login.microsoftonline.com/ceb88b8e-4e6a-4561-a112-5cf771712517/oauth2/token'
        
        req = requests.post(endp,env)
        
        if req.status_code == 200:
            token = req.json()['access_token']
            return 'Bearer {0}'.format(token)
        else:
            return None
    
    #region Obtener Trabajos por Lotes
    def get_Trabajo_Lotes(self):
        
        #Definir url
        path = f"{self.url}/data/BatchJobs"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$filter=ExecutingBy%20eq%20'{self.username}'&$select=JobDescription,Status&$orderby=StartDateTime%20desc&$top={str(self.top)}"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        print(path)
        response = requests.get(path,headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        
    #endregion
    #region ObtenerProductos
    def get_Products_List(self):
        #Definir url
        path = f"{self.url}/data/RetailTransactionSalesLinesV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$filter=TransactionNumber eq '{self.transaccion}' &$select=ItemId,Unit"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            return response.json()
    #endregion
    #region ObtenerTransaccionesError
    def get_Transaction_Error(self):
        #Definir url
        path = f"{self.url}/data/TRURetailEodTransactions"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$filter=StatementId eq '{self.extracto}' and PostingErrorCode eq Microsoft.Dynamics.DataEntities.RetailEodTransactionPostingErrorCode'Error' &$select=TransactionId"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        resultList = {}
        if response.status_code == 200:
            resultList[self.extracto] = {}
            for i in response.json()["value"]:
                resultList[self.extracto][i["TransactionId"]]={}
                ##
                self.transaccion=i["TransactionId"]
                temp_list = self.get_Products_List()["value"]
                for y in temp_list:
                    print("Obteniendo resultados...")
                    resultList[self.extracto][i["TransactionId"]][y["ItemId"]] = self.get_Unidad_Venta_Final(y["ItemId"],y["Unit"])
                    ##
                    if y["ItemId"] not in self.lista_productos:
                        self.lista_productos[y["ItemId"] ]= self.get_Unidad_Venta_Final(y["ItemId"],y["Unit"])
                        if self.productos == "":
                            self.productos = self.productos+ y["ItemId"]
                        else:
                            self.productos = self.productos + "," + y["ItemId"]
            return resultList
        else:
            return resultList
    #endregion
    
    #region ObtenerUnidadVenta por Producto
    def get_Unidad_Venta_Final(self,product,unidad_venta_final,grupo_tiendas=1):
        
        # Asignamos grupo de tiendas elegidas
        tiendas_seleccionadas =[]
        tiendas_minoristas = ["MD01_LUZ","MD02_JRC","MD03_CRH","MD04_SUC","MD05_CRZ","MD06_BOL","MD07_CEN"]
        tiendas_mayoristas = ["AD01_RAY","AD02_CRH","AD03_CRZ","AD04_TCE"]
        if grupo_tiendas == 1:
            tiendas_seleccionadas = tiendas_minoristas
        elif grupo_tiendas == 2:
            tiendas_seleccionadas = tiendas_mayoristas
        elif grupo_tiendas == 3:
            tiendas_seleccionadas = tiendas_minoristas.extend(tiendas_mayoristas)
            
        ## Verificamos Unidades de Conversion
        if self.verificar_Unidades_Conversion(product,unidad_venta_final):
            #Definir url
            path = f"{self.url}/data/SalesPriceAgreements"
            
            token = self.get_Token()
            
            #Queries
            query = f"?$filter=ItemNumber eq '{product}' &$select=PriceWarehouseId"
            
            #Headers
            headers = {
                "Authorization": token,
                "Content-Type": "application/json"
            }
            
            path=path+query
            response = requests.get(path,headers=headers)
            result_list ={}
            if response.status_code == 200:
                for item in response.json()["value"]:
                    if item["PriceWarehouseId"] in tiendas_seleccionadas:
                        if unidad_venta_final in result_list:
                            result_list[unidad_venta_final].append(item["PriceWarehouseId"])
                        else:
                            result_list[unidad_venta_final]=[]
                            result_list[unidad_venta_final].append(item["PriceWarehouseId"])
                return result_list
            else:
                return result_list
        else:
            return result_list
    #endregion
    #region ObtenerUnidadConversion por Producto
    def verificar_Unidades_Conversion(self,product,unidad_venta):
        #Definir url
        path = f"{self.url}/data/ProductUnitOfMeasureConversions"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$filter=ProductNumber eq '{product}' &$select=FromUnitSymbol,ToUnitSymbol"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        count_errors=0
        self.msg_error=""
        temp_unidad_existe=0
        if response.status_code == 200:
            for unit in response.json()["value"]:
               ##Verificando configuración correcta entre unidades
                if unit["FromUnitSymbol"] == unit["ToUnitSymbol"]:
                   count_errors = count_errors +1
                
                ## Verificando configuracion correcta en unidad de venta
                if unit["FromUnitSymbol"] == "U.":
                    count_errors = count_errors + 1
                
                ## Verificando configuracion correcta en unidad de venta
                if unit["FromUnitSymbol"] == unidad_venta:
                    temp_unidad_existe = temp_unidad_existe+  1
                    
                
            if temp_unidad_existe == 0:
                count_errors = count_errors + 1
                    
            if count_errors > 0:
                self.msg_error=self.msg_error + f"\n ERROR: En configuración de Unidades del producto {product} - VERIFICAR"
                return False
            else:
                return True
        else:
            return False
    #endregion
    
    def _getListaProductos(self):
        return self.lista_productos
    
    def _getProductos(self):
        return self.productos
    
    def _getErrores(self):
        return self.msg_error