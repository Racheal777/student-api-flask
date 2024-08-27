
import os
import psycopg2
from flask import Flask, request, jsonify
from dotenv import  load_dotenv

load_dotenv()

app = Flask(__name__)

def connect_to_db():
    try:
        return  psycopg2.connect(
            host=os.getenv('HOSTNAME'),
            database=os.getenv('DATABASE'),
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
    cursor.execute('CREATE TABLE IF NOT EXISTS students (id Serial PRIMARY KEY, name varchar(255), age int, grade decimal)', )
    conn.commit()
    cursor.close()

create_table()


@app.post('/add-students')
def add_student():

    data = request.get_json()
    name = data['name']
    age = data['age']
    grade = data['grade']

    conn = connect_to_db()
    cursor = conn.cursor()
    query =  cursor.execute("INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)", (name, age, grade) )
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "data": query,
        "message": 'Student added',
        "status": 201
    }

@app.get('/students')
def get_students():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students" )
    results = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    students = []
    for result in results:
        students.append({
            "id": result[0],
            "name": result[1],
            "age": result[2],
            "grade": result[3]
        })
    return jsonify({
        "data": students,
        "message": 'Students fetched successfully',
        "status": 200
    }
)


@app.get('/students/<student_id>')
def get_student(student_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    if not student_id:
        print('Enter an id')
        return {
            "message": 'ID not available',
            "status": 400

        }
    find_student = cursor.execute('SELECT * from students WHERE id = %s', student_id,)
    result = cursor.fetchone()


    if not result:
        print(f" student with the id {student_id} does not exist")
        return {
            "message": 'Student not found',
            "status": 404

        }
    data= {'id': result[0], 'name': result[1], 'age': result[2], 'grade': result[3]}

    return {
        "data": data,
        "message": 'Students fetched successfully',
        "status": 200
    }




@app.put('/students/<student_id>')
def update_student(student_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    student = get_student(student_id)

    data = request.get_json()
    name = data['name']
    age = data['age']
    grade = data['grade']

    cursor.execute("UPDATE students SET name = %s, age = %s, grade = %s WHERE id = %s",
                   (name, age, grade, student_id))

    conn.commit()
    print(f"student with id   {student_id}  status has been updated ")
    cursor.close()

    return jsonify({
        "data": student.get('data'),
        "message": 'Student updated successfully',
        "status": 200
    }
)


@app.delete('/students/<student_id>')
def delete_student(student_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    student = get_student(student_id)

    cursor.execute("DELETE FROM students WHERE id = %s",
                   student_id)

    conn.commit()
    print(f"student with id   {student_id}  status has been deleted ")

    cursor.close()

    return jsonify({
        "data": '',
        "message": 'Student deleted successfully',
        "status": 200
    }
    )


if __name__ == "__main__":
    app.run()
