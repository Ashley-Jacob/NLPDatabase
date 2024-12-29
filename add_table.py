import mysql.connector
import pandas as pd
import numpy as np
import os

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Password", # change to correct pw
  database="testgenedata" # change to correct name
)

mycursor = mydb.cursor()

table_name = "Inflammation_Genes"

mycursor.execute("CREATE TABLE " + table_name + " (Gene VARCHAR(255) NOT NULL, Primary Key (Gene));")
data = pd.read_csv("C:/CSE3800/ReportData/Inflammation.csv")
for index, cell in data.iterrows():
    sql = "INSERT INTO " + table_name+ "(Gene) VALUES (%s)"
    val = [cell['Gene']]
    mycursor.execute(sql, val)

mydb.commit()