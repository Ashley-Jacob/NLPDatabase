import mysql.connector
import pandas as pd
import numpy as np
import os


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="INSERT PASSWORD", # change to correct pw
  database="INSERT DB NAME" # change to correct name; exclude if creating DB for first time
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE testgenedata")

directory = 'C:/CSE3800/ReportData/' # change path as needed
# mycursor.execute("CREATE TABLE Samples (Sample_ID INT PRIMARY KEY AUTO_INCREMENT, Sample VARCHAR(255) NOT NULL);")

for folder in os.listdir(directory):
    cluster_num = 0
    sql = "INSERT INTO Samples (Sample) VALUES (%s)"
    val = [folder]
    mycursor.execute(sql, val)

    for file in os.listdir(directory + folder):
        table_name = folder + "_cluster" + str(cluster_num)
        mycursor.execute("CREATE TABLE " + table_name + " (GeneA VARCHAR(255) NOT NULL, GeneB VARCHAR(255) NOT NULL, weight DECIMAL(4,3) NOT NULL, Primary Key (GeneA, GeneB));")
        data = pd.read_csv(directory + folder + '/' + file)
        for index, cell in data.iterrows():
            sql = "INSERT INTO " + table_name+ "(GeneA, GeneB, weight) VALUES (%s, %s, %s)"
            val = cell['GeneA'], cell['GeneB'], cell['weight']
            mycursor.execute(sql, val)

        cluster_num += 1
        print(folder + "/" + file)

mydb.commit()