import requests, json
import datetime
import pandas as pd
import re

class ApiDynamics:
    
    #Definiendo variables
    url = "https://mistr.operations.dynamics.com/"
    extracto=""
    transaccion=""
    msg_error=""
    lista_productos={}
    productos=""
    
    ##
    productsBarcode = None
    categoryProducts = None
    translationProducts = None
    AllProducts = None
    listProviders = None
    listProductsSell = None
    productsInactive = None
    unitConvertionProducts = None
    
    #Inicializando 
    def __init__(self):
        
        ## 
        self.productsBarcode = pd.read_json(json.dumps(self.getBarcodeProduct()))
        self.categoryProducts = pd.read_json(json.dumps(self.getCategoryProduct()))
        self.translationProducts = pd.read_json(json.dumps(self.getTraslationProduct()))
        self.AllProducts = pd.read_json(json.dumps(self.getAllProducts()))
        self.listProviders = pd.read_json(json.dumps(self.getListProvidersProducts()))
        self.listProductsSell = pd.read_json(json.dumps(self.getProductsSell()))
        self.productsInactive = pd.read_json(json.dumps(self.getAllProductsInactive()))
        self.unitConvertionProducts = pd.read_json(json.dumps(self.getUnitConversionProducts()))
        ##
    
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
    
    #region Obtener Todos Productos Vendidos
    def getProductsSell(self): 
        #Definir url
        path = f"{self.url}/data/RetailTransactionSalesLinesV2"
        
        token = self.get_Token()
        
        #Date Now
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        
        #Queries
        query = f"?$count=true&$select=ItemId,Unit&$filter=TransactionDate eq {fecha_actual}"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    ######
    def verifyExistsBarCode(self):
        df1 = self.AllProducts
        df2 = self.productsBarcode
        df3 = self.categoryProducts
        #print(df2)
        consult = df1[~df1['ItemNumber'].isin(df2['ItemNumber'])]
        result = df1[df1['ItemNumber'].isin(consult['ItemNumber'])]
        result_filter = result[~result["SearchName"].str.contains("BONI",na=False)]
        result_filter_mayoristas = df3[df3["ProductCategoryHierarchyName"].str.contains("Catalogo Mayorista",na=False)]
        result_filter_ventas = result_filter[result_filter["ItemNumber"].isin(df3["ProductNumber"]) & (df3["ProductCategoryHierarchyName"].str.contains("Catalogo Ventas",na=False))]
        result_final = result_filter_ventas[~result_filter_ventas['ItemNumber'].isin(result_filter_mayoristas['ProductNumber'])]
        x , y = result_final.shape

        if x>0:
            print("-- Total prod. codigo_barra encontrado:" ,x)
            data = result_final[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyUnitSymbol(self):
        df1 = self.AllProducts
        inventory_filter_symbol = df1[(df1["InventoryUnitSymbol"]=="U") | (df1["InventoryUnitSymbol"]=="LTR") | (df1["InventoryUnitSymbol"]=="SA") | (df1["InventoryUnitSymbol"]=="KGM") | (df1["InventoryUnitSymbol"]=="UND") | (df1["PurchaseUnitSymbol"]=="U.") | (df1["PurchaseUnitSymbol"]=="LTR.") | (df1["PurchaseUnitSymbol"]=="SA.") | (df1["PurchaseUnitSymbol"]=="KGM.") | (df1["InventoryUnitSymbol"]=="UND.")]
        x , y = inventory_filter_symbol.shape
        
        if x>0:
            print("-- Total prod. con problemas en unidades de conversion encontrado:" ,x)
            data = inventory_filter_symbol[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
        
    def verifyEquiUnitSymbol(self):
        df1 = self.unitConvertionProducts
        df2 = self.AllProducts
        df1["from_u"] = df1["FromUnitSymbol"].apply(lambda x: re.findall(r'\d+',x))
        df1["from_u"] = df1["from_u"].apply(lambda x: int(x[0]) if len(x) > 0 else 1)
        df1["to_u"] = df1["ToUnitSymbol"].apply(lambda x: re.findall(r'\d+',x))
        df1["to_u"] = df1["to_u"].apply(lambda x: int(x[0]) if len(x) > 0 else 1)
        #temp_result = df1[~(df1["to_u"].astype(int) * df1["Factor"].astype(int) == df1["from_u"].astype(int))]
        temp_result = df1[~(df1["to_u"].astype(float) * df1["Factor"].astype(float) == df1["from_u"].astype(float))]
        result = pd.merge(df2,temp_result,left_on='ItemNumber',right_on='ProductNumber')
        result["error"] = result["ToUnitSymbol"].astype(str) +' / '+ result["Factor"].astype(str) +' / '+ result["FromUnitSymbol"].astype(str)
        x , y = result.shape
        
        if x>0:
            print("-- Total prod. con problemas en unidades de conversion encontrado:" ,x)
            data = result[["ItemNumber","SearchName","error"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyCodeSunat(self):
        df1 = self.AllProducts
        codigo_sunat = pd.read_csv("./assets/codigo_sunat.csv")
        consult = df1[~df1['DPCodProductSUNAT_PE'].isin(codigo_sunat['CODIGO PRODUCTO'])]
        consult_2 = consult[~(consult["DPCodProductSUNAT_PE"].astype(str).str[6:] == "00")]
        x,y = consult_2.shape
        if x>0:
            print("-- Total prod. sunat encontrado:" ,x)
            data = consult_2[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyAssignProvider(self):
        df1= self.AllProducts
        df2 = self.listProviders
        result  = df1[~df1['ItemNumber'].isin(df2['ItemNumber'])]
        #print(result) ##Esperar a verificar
        x,y = result.shape
        if x>0:
            print("-- Total prod. sin proveedor encontrados:" ,x)
            data = result[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
        
    def verifyCatalogVentas(self):
        df1 = self.AllProducts
        df3 = self.categoryProducts
        df3_filter = df3[df3["ProductCategoryHierarchyName"].str.contains("Catalogo Ventas",na=False)]
        #print(df2)
        result = df1[~df1["ItemNumber"].isin(df3_filter["ProductNumber"])]
        #print(result)
        x,y = result.shape
        if x>0:
            print("-- Total prod. sin catalogo encontrados:" ,x)
            data = result[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyTranslationProduct1(self):
        df1 = self.AllProducts
        df2 = self.translationProducts
        df_es = df2[df2["LanguageId"].str.contains("es",na=False)]
        result1 = df1[~df1["ItemNumber"].isin(df_es["ProductNumber"])] # Solo los que tienen registrado el idioma MX
        x1 ,y1 = result1.shape
        
        if x1>0:
            print("-- Total prod. sin traducciones1 encontrados:" ,x1)
            data = result1[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyTranslationProduct2(self):
        df1 = self.AllProducts
        df2 = self.translationProducts
        df_mx = df2[df2["LanguageId"].str.contains("es-MX",na=False)]
        result2 = df1[~df1["ItemNumber"].isin(df_mx["ProductNumber"])] # Solo los que tienen registrado el idioma ES
        x2 ,y2 = result2.shape
        if x2>0:
            print("-- Total prod. sin traducciones2 encontrados:" ,x2)
            data = result2[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyTranslationProduct3(self):
        df1 = self.AllProducts
        df2 = self.translationProducts
        result3= df1[~df1["ItemNumber"].isin(df2["ProductNumber"])] # No esta registrado ni MX ni ES para el product
        x3 ,y3 = result3.shape
        if x3>0:
            print("-- Total prod. sin traducciones3 encontrados:" ,x3)
            data = result3[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    
    def verifyProductsInStateActive(self):
        df1 = self.AllProducts
        df2 = self.listProductsSell
        df3 = self.productsInactive
        result = df2[~df2["ItemId"].isin(df1["ItemNumber"])]
        result_1 = df3[df3["ItemNumber"].isin(result["ItemId"])]
        x , y = result.shape
        if x>0:
            print("-- Total prod. vendidos con estado activo encontrados:" ,x)
            data = result_1[["ItemNumber","SearchName"]] 
            return data
        else: 
            return pd.DataFrame({})
    ######
    
    #region AllProducts
    def getAllProducts(self):
        #Definir url
        path = f"{self.url}/data/ReleasedProductsV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$filter=ProductLifecycleStateId eq 'ACTIVO' &$select=ItemNumber,ItemModelGroupId,ProductSubType,InventoryUnitSymbol,ProductLifecycleStateId,PurchaseUnitSymbol,ProductGroupId,DPCodProductSUNAT_PE,SearchName"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region AllProductsInactive
    def getAllProductsInactive(self):
        #Definir url
        path = f"{self.url}/data/ReleasedProductsV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$filter=ProductLifecycleStateId eq 'INACTIVO' &$select=ItemNumber,SearchName"
        
        #Headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetBarcode
    def getBarcodeProduct(self):
        #Definir url
        path = f"{self.url}/data/ProductBarcodesV2"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true&$select=ItemNumber,ProductQuantityUnitSymbol,BarcodeSetupId,Barcode,ProductDescription"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetCategoriesProduct
    def getCategoryProduct(self):
        #Definir url
        path = f"{self.url}/data/ProductCategoryAssignments"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetCategoriesProduct
    def getTraslationProduct(self):
        #Definir url
        path = f"{self.url}/data/ProductTranslations"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetCategoriesProduct
    def getListProvidersProducts(self):
        #Definir url
        path = f"{self.url}/data/ProductApprovedVendors"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
    
    #region GetUnitConvertionProducts
    def getUnitConversionProducts(self):
        #Definir url
        path = f"{self.url}/data/ProductSpecificUnitOfMeasureConversions"
        
        token = self.get_Token()
        
        #Queries
        query = f"?$count=true"
        
        #Headers
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        path=path+query
        response = requests.get(path,headers=headers)
        if response.status_code == 200:
            temp1= response.json()
            #
            count = int(int(temp1["@odata.count"])/10000)
            if count > 0 :
                result= temp1["value"]
                for i in range(count):
                    query_update = f"{path}&$top=10000&$skip={int(i)+1}0000"
                    response = requests.get(query_update,headers=headers)
                    if response.status_code == 200:
                        result.extend(response.json()["value"])
                return result
            else:
                return temp1["value"]
    #endregion
