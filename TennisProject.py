import requests
import mysql.connector
from mysql.connector import Error

def Extracting_Data_From_Api(url, headers):
    print('Fetching Started...')
    try:
        
        response = requests.get(url, headers)
        # Check for request errors
        response.raise_for_status()
        print(f"Status code: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error Occurred While Fetching the data from API. Refer: {e}')

def connecting_to_database(host,user,password,database):
    try:

        connection=mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print('Connected to MySQl...')
        else:
            print('Not Able to Connect to MySQL please find the below Reference too see what happened')

        return connection
    except Error as e:
        print('"Error raised while connecting to MySQL:',e)

def InsertData(cursor,Tablename,data):
    try:
        columnnames=', '.join(data.keys())
        values=', '.join(['%s'] * len(data)) 
        query=f'INSERT INTO {Tablename} ({columnnames}) values({values})'
        cursor.execute(query,tuple(data.values()))
        print(f"Inserted into {Tablename}: {data}")
    except Exception as e:
        print(f'Error occured while inserting into the Table {Tablename}: {data}',e)

def Inserting_DataFrom_Api1(data,cursor,connection):
    try:
        #Insert Categories
        for competition in data.get("competitions",[]):
            categorydata={
                "category_id": competition["category"]["id"],
                 "category_name ": competition["category"]["name"]
            }
            InsertData(cursor, "Categories", categorydata)
            #Insert Competitions
            competitiondata={
                "competition_id": competition["id"],
                "competition_name": competition["name"],
                "parent_id":competition.get("parent_id", None),
                "type": competition["type"],
                "gender": competition["gender"],
                "category_id": competition["category"]["id"]
            }
            InsertData(cursor, "Competitions", competitiondata)
            connection.commit()
    except KeyError as e:
        print(f"KeyError in API 1 data: Missing key {e}")
    except Error as e:
        print(f"Database error in API 1 handler: {e}")


def Inserting_DataFrom_Api2(data, cursor, connection):
    try:
        print('API 2 processing started')
        
        for complex in data.get("complexes", []):
            print(f"Processing Complex: {complex}")
            
            # Insert Complex
            complexdata = {
                "complex_id": complex["id"],
                "complex_name": complex["name"]
            }
            InsertData(cursor, "Complexes", complexdata)
            print(f"Inserted Complex: {complexdata}")
            
            # Insert Venues
            for venue in complex.get("venues", []):
                print(f"Processing Venue: {venue}")
                venuedata = {
                    "venue_id": venue["id"],
                    "venue_name": venue["name"],
                    "city_name": venue["city_name"],
                    "country_name": venue["country_name"],
                    "country_code": venue["country_code"],
                    "timezone": venue["timezone"],
                    "complex_id": complex["id"]
                }
                InsertData(cursor, "Venues", venuedata)
                print(f"Inserted Venue: {venuedata}")
        
        # Commit after processing
        connection.commit()
        print("Data committed successfully for API 2.")
    
    except KeyError as e:
        print(f"KeyError in API 2 data: Missing key {e}")
        
    except Error as e:
        print(f"Database error in API 2 handler: {e}")
       


def Inserting_DataFrom_Api3(data,cursor,connection):
    try:
        for ranking in data.get("rankings", []):
            for competitor_ranking in ranking.get("competitor_rankings", []):
                competitor = competitor_ranking["competitor"]
                #Insert Competitor Table
                competitor_data = {
                    "competitor_id": competitor["id"],
                    "name": competitor["name"],
                    "country": competitor["country"],
                    "country_code": competitor.get("country_code",None),
                    "abbreviation": competitor["abbreviation"]
                }
                InsertData(cursor, "Competitors", competitor_data)
                print(f"Inserted Competitor: {competitor_data}")
                
                #  Insert Competitor Rankings Table
                competitor_ranking_data = {
                    "`rank`": competitor_ranking["rank"],
                    "movement": competitor_ranking["movement"],
                    "points": competitor_ranking["points"],
                    "competitions_played": competitor_ranking["competitions_played"],
                    "competitor_id": competitor["id"],  # Linking to Competitor table
                }
                InsertData(cursor, "Competitor_Rankings", competitor_ranking_data)
        
        # Commit after processing
        connection.commit()
        print("Data committed successfully for API 3.")
    except KeyError as e:
        print(f"KeyError in API 3 data: Missing key {e}")
    except Error as e:
        print(f"Database error in API 3 handler: {e}")


def Main():
    

    # Connecting _to MySQL
    connection=connecting_to_database(
        host='localhost',
        user='root',
        password='',
        database='TennisStatsPro'
     )
    if connection.is_connected():

        cursor=connection.cursor()

        # Call the function to extract data

        #Handle Api 1
        api1 = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=8TrhAKqcBxgUZ7D1Isz3IeR3Wkvnzo87PfrTbDZl"
        Headers = {"accept": "application/json"}
        ResponseFromApi1 = Extracting_Data_From_Api(api1, Headers)
        if ResponseFromApi1:
            Inserting_DataFrom_Api1(ResponseFromApi1,cursor,connection)
        else:
            print('No data was received in the API response. ')
        
        #Handle Api2
        api2 = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=8TrhAKqcBxgUZ7D1Isz3IeR3Wkvnzo87PfrTbDZl"
        Headers = {"accept": "application/json"}
        ResponseFromApi2 = Extracting_Data_From_Api(api2, Headers)
        print(ResponseFromApi2)
        if ResponseFromApi2:
            Inserting_DataFrom_Api2(ResponseFromApi2,cursor,connection)
        else:
            print('No data was received in the API response.')

        #Handle Api 3
        api3 = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=8TrhAKqcBxgUZ7D1Isz3IeR3Wkvnzo87PfrTbDZl"
        Headers = {"accept": "application/json"}
        ResponseFromApi3 = Extracting_Data_From_Api(api3, Headers)
        print(ResponseFromApi3)
        if ResponseFromApi3:
            Inserting_DataFrom_Api3(ResponseFromApi3,cursor,connection)
        else:
            print('No data was received in the API response.')
        

        cursor.close()
        connection.close()
    else:
        print('Connection to the MySql is Failed...')
  



# Entry point for script execution
if __name__ == "__main__":  
    Main()
