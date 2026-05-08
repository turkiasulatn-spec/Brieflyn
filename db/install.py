import sqlite3

file = "database.db"

try:
  conn = sqlite3.connect(file)
  print("Database database.db formed.")
except:
  print("Database database.db not formed.")