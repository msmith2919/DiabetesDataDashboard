from sqlalchemy import create_engine

# Replace <SQLAlchemy Database URI> with your actual URI
engine = create_engine('mssql+pyodbc://test:1234@CIT-SP-23\SQLEXPRESS/Nightscout?driver=ODBC+Driver+17+for+SQL+Server')

# Test the connection
try:
    connection = engine.connect()
    print('* * * Connection successful! * * *')
    connection.close()
except Exception as e:
    print('* * * CONNECTION FAILED * * *')
    print(e)