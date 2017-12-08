### Welcome to Flasky-and-Friends
*Thank you for visiting!*

Miguel Grinberg's [Flasky](https://github.com/miguelgrinberg/flasky) helped inspire this FrankenStack repository that has allowed me to test & learn an evergrowing set of features. 

Flasky relies upon a SQLAlchemy database that has been modified to allow users to add dogs :dog::dog::dog: to their account profile. 

Flasky and friends also includes
* Kafka via python-kafka 
* Natural Language Processing via Delbot (https://github.com/shaildeliwala/delbot)
* Spark via pyspark (...coming soon!)



### How to run yourself: 

Note - Instructions below are for Ubuntu & python 2.7 w/ pip & virtualenv already installed
 
```bash
virtualenv venv

source venv/bin/activate

pip install requirements.txt
```

Configure SQLAlchemyDB.

See [Miguel's blog about SQLAlchemy](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database-legacy) if you're new to this kinda thing
```bash
python manage.py db 
```
Start Kafka Utilities

**Required**: You'll need to start zookeeper and create a topic if you want to interact with this module.

*If you're like me, you may find it frustrating that Kafka requires so many pre-req steps. Check out [the /kafka-utils folder](kafka-utils) to take a shortcut starting the utilities*

Start the Server:
```bash
python manage.py runserver
```
Open browser & go to: http://127.0.0.1:5000


