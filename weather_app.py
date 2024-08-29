

import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

app = Flask(__name__)


def connect_to_db():
    try:
        return  psycopg2.connect(
            host=os.getenv('HOSTNAME'),
            database=os.getenv('WEATHER_DATABASE'),
            user=os.getenv('USERNAME'),
            password= os.getenv('PASSWORD'),
            port = os.getenv('PORT')

        )
    except(Exception, psycopg2.Error) as error:
        print("Error while connecting to postgresql", error)
        return "f Error while connecting to postgresql", {error}

def create_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS weather (id Serial PRIMARY KEY, city varchar(255), '
                   'country varchar(255), temperature FLOAT, description TEXT,  date TIMESTAMP DEFAULT NOW())')
    conn.commit()
    cursor.close()

create_table()



@app.route('/weather', methods= ['POST'])
def get_weather():
        data = request.get_json()
        city = data['city']
        if not city:
            return "f Enter a correct city name "

        try:
           api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("API_KEY")}"

           response = requests.get(api_url)
           if response.json()['cod'] == 200:
               description = response.json()['weather'][0]['description']
               country = response.json()['sys']['country']
               temperature = response.json()['main']['temp']
           else:
               return "Error while fetching data from the Weather Api, Check the city spellings"

        except Exception as e:
           return f"f Error while fetching data from api {e}"

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO weather (city,  country, temperature, description) VALUES (%s, %s, %s, %s)",
                       (city, country, temperature, description))

            conn.commit()
            cursor.close()
            conn.close()
            return ({
                "data": response.json(),
                "message": f'f weather of {city} added successfully',
                "status": 201
            })

        except Exception as e:
            return f"f Error while adding to the database {e}"


@app.route('/weather', methods=['GET'])
def get_students():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weather ORDER BY city")
        results = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        weather = []
        for result in results:
            weather.append({
                "id": result[0],
                "city": result[1],
                "country": result[2],
                "description": result[4],
                "temperature": result[3]
            })
        return jsonify({
            "data": weather,
            "message": 'weather fetched successfully',
            "status": 200
        }
        )
    except Exception as e:
        return f"f Error while retrieving form the database {e}"

if __name__ == '__main__':
    app.run(debug=True)