from fileinput import filename
import os
import pandas as pd  # pip install pandas
from re import search
import mysql.connector
from mysql.connector import Error
import zipfile
import shutil
from dateutil.parser import parse
##https://www.csvplot.com/

## Esta version 4.0 logra que el programa sea escalable, ya que es necesario tener los zips en una carpeta y solo con poner el mes formatea
## documentos y los sube a la base.




con = mysql.connector.connect(
    host='localhost', user='root', password='', database='proyectoenergia') ## Conexion a la base de datos xampp


##cursor = con.cursor() ## Cursor de la base de datos

print('en este formato AAAAMM\n')
decompressed_folder = input('Introduce nombre de carpeta a descomprimir y subir a la BD?\n') ## clave para las funciones ya que las carpetas se llamaran como este mes


data_file_folder = './tiempos/'+decompressed_folder ## Folder en donde se van a encontrar los nuevos datos ya descomprimidos

folder_weather = './clima'

casas = ['Casa1', 'Casa6', 'Casa10', 'Casa8','Casa_7'] ## Identificador casa
intervalos = ['15MIN', '1H', '1DAY'] ## Identificador Intervalos
##houses = ['house1', 'house6', 'house10', 'house8']

month = data_file_folder[-2:] 
year = data_file_folder[-6:-2]
end = year+"-"+month+"-10 23:45:00" ##compara con mask el mes con el mes ingresado
date_1 = parse(end)


def conexion(): ## En esta Funcion se realiza y comprueba que estas conectado a la base de datos. 

    if con.is_connected():
        print("Estas conectado a la base de datos")
    conexion()


def encuentra_bd():
    for file in os.listdir(data_file_folder):
        if file.endswith('.csv'):
            file_path = os.path.join(data_file_folder, file)
            df = pd.read_csv(file_path, parse_dates=["Time Bucket (America/Chicago)"])
            mask = (df['Time Bucket (America/Chicago)'].dt.month) == date_1.month
            df = df.loc[mask]

            for x in casas:
                if x == 'Casa6':
                    n = '6'
                if x == 'Casa10':
                    n = '10'
                if x == 'Casa1':
                    n = '1'
                if x == 'Casa8':
                    n = '8'
                if x == 'Casa_7':
                    n = '7'            
                for y in intervalos:
                    opc = x+'-'+y+'.csv'
                    if x == 'Casa6':
                        id = '6'
                    if x == 'Casa10':
                        id = '10'
                    if x == 'Casa1':
                        id = '1'
                    if x == 'Casa8':
                        id = '8'
                    if x == 'Casa_7':
                        id = '7'
                    
                    df["id"] = id
                    df.head()

                    if opc in file:
                        new_file_path = os.path.join(data_file_folder, opc)
                        df.to_csv(new_file_path, index=False, header=False)
                        print('Hecho: ' + new_file_path)
                        print(x)
                    qry = "LOAD DATA INFILE './tiempos/"+decompressed_folder+"/"+opc+"' INTO TABLE "'houseteh'+n+'_'+y+" FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'" ## Query para subir datos a la bd
                    print(qry)
                    cursor.execute(qry) ## ejecuta query 
                    con.commit()

def encuentraclima():
    for file in os.listdir(folder_weather): ## Encuentra el archivo en la bd
     if file.startswith('ambient'):
        filePath = folder_weather+'/'+file
        df = pd.read_csv(filePath)
        reversed_df = df.iloc[::-1]
        climanombre = 'ambient2-'+decompressed_folder+'.csv'  
        reversed_df.to_csv('./clima/'+climanombre,header=False,index=False)
        print('clima')
        qry="LOAD DATA INFILE './clima/ambient2-"+decompressed_folder+".csv' INTO TABLE ambient_weather FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n'"
        print(qry)
        cursor.execute(qry) ## ejecuta query 
        con.commit()
    ## inverit columnas, las de abajo van hasta arriba, fechas de la segunda columna
    ## dejar vacio folder clima para que no haga duplicados!!!!



def descomprimir(): ## En esta funcion se descomprime el primer zip de fecha y el de cada casa2

    with zipfile.ZipFile('./'+decompressed_folder+'.zip', 'r') as zip_ref: ## descomprime el zip inicial
        zip_ref.extractall('./tiempos')
    for file in os.listdir('./tiempos/'+decompressed_folder):
      if file.endswith('.zip'):
       ## os.chdir('./tiempos/'+decompressed_folder)
        file_name = os.path.abspath('./tiempos/'+decompressed_folder+'/'+file) ## descomprime el zip de cada casa
        print(file_name)
        zip_ref = zipfile.ZipFile(file_name)
        zip_ref.extractall('./tiempos/'+decompressed_folder) 
        zip_ref.close()

def mueveclima(): ## mueve ambient-weather a la carpeta de clima y elimina el archivo para poder operar los de las casas bien.
    for file in os.listdir(data_file_folder):
        if file.startswith('ambient'):
            filePath = data_file_folder+'/'+file
            df = pd.read_csv(filePath)
            df.to_csv('./tiempos/'+decompressed_folder+'/ambient-'+decompressed_folder+'.csv',index=False) ##crea archivo llamado ambient + el mes de la carpeta
            print('hecho ambient')
            shutil.move('./tiempos/'+decompressed_folder+'/ambient-'+decompressed_folder+'.csv','./clima' )
            if filePath.startswith('./tiempos/'+decompressed_folder+'/ambient-'):
                os.remove(filePath)


                ## cualquier cosa checar programa original en esta parte

def borra(): ##borra 1 segundo y 1 minuto
    for file in os.listdir(data_file_folder):
        if file.endswith('1SEC.csv') or file.endswith('1MIN.csv'):
            file_path = os.path.join(data_file_folder, file)
            os.remove(file_path)



## clima con intervalo de cada 10 minutos hasta el 30 de sept llenar toda la tabla por -1
## mandar archivos mergidos 
## documentacion mandar script y comentarios
## subir bd al servidor.

        

descomprimir()
mueveclima()
borra()
encuentraclima()
encuentra_bd()
con.close() ## cierra la conexion a la base

        