1. This is a Django project, so to run this code, you need a Django environment (If you use Pycharm, I believe you just need to open the project). 
2. The database which this project connects to is MySQL, but I didn't build any model for this project, so you don't need to change settings.py.
3. Please make sure your MySQL is open, then go to /data/analysis/set_database.py, replace the user name, password and database name in the file with yours, and then run it.
4. Maybe you should pay attention to pymsql and seaborn. If you don't have these two packages, please install them.
5. Then run Django, python manage.py runserver
6. I do push the secret file for twitter and reddit, this is just for your convenience. Please just use it. 
