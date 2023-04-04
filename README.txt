Python version == 3.10.10

1. craete env

command on cmd
python3.10 -m venv env

2. activate env
env\scripts\activete

3. install all reqirements from  requirements.txt
pip install -r requirements.txt

4. create migrations file using
python manage.py makemigrations or python manage.py makemigrations mainapp


5. create database table
python manage.py migrate


6. runserver
python manage.py runserver

7. run this command on brwoser
http://127.0.0.1:8000/graphql

8. check query.txt for Graphql query