from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'
    

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('SignIn.html')

@app.route("/check", methods=['POST'])
def check():
    cursor=db_conn.cursor()
    em=request.form['email']
    pas=request.form['password']
    d=cursor.execute("SELECT *  FROM emp_login where email=%s and password=%s",(em,pas))
    details = cursor.fetchall()
   # print("abc")
    
    #print ('<table border="0"><tr><th>order</th><th>name</th><th>type</th><th>description</th></tr>')
    #print ('<tbody>')
    #counter = 0
    #for field in details:
    #    counter = counter + 1
    #    name = field[0]
    #    pas = field[1]
    #    print('<tr><td>' + str(counter) + '</td><td>' + name + '</td><td>' + pas + '</td><td></td></tr>')
    #print ('</tbody>')
    #print ('</table>')
    
    return render_template('Hme_Pge.html')


@app.route("/get_emp_info", methods=['GET', 'POST'])
def get_emp_info():
    return render_template("GetEmp.html")

@app.route("/ins_emp_info", methods=['GET', 'POST'])
def ins_emp_info():
    return render_template("AddEmp.html")

@app.route("/about", methods=['POST'])
def about():
    return render_template('https://github.com/Vyshkk')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route("/fetchdata", methods=['POST'])
def fetch():
    emp_id=request.form['emp_id']
    get_sql=("SELECT * from employee where emp_id=%s")
    cursor = db_conn.cursor()
    cursor.execute(get_sql, (emp_id))
    details=cursor.fetchall()
    print(details[0][0])
    print(details[0][1])
    emp_id=details[0][0]
    f_name=details[0][1]
    l_name=details[0][2]
    pri_skill=details[0][3]
    location=details[0][4]
    #for detail in details:
    #    var = detail
    return render_template('GetEmpOutput.html',emp_id=emp_id)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
