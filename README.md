# Order Tracking API (FastAPI)

Application that allows you to manage e-commerce deliveries.

Functions:
- Create product orders
- Register users
- Get product catalog
- Update delivery status and inform customer by email (using State design pattern) [*admin*]
- Modify orders (add/remove products) [*user/admin*]
- Cancel or delete orders [*user/admin*]
- Update user's contact information [*user/admin*]
 	
## Installation

Project in FastAPI and Dockerized

Run:
```
docker-compose build
docker-compose up
```

Migrate Models:
```
docker-compose run app alembic revision --autogenerate -m "new-migration"
docker-compose run app alembic upgrade head
```

  
Create administrator user:
```
docker exec -it app bash
python createdata.py
```

  
### **Email Configuration:**
(with Fastapi-mail library)

Enter email *user* and *password* as env variables in ***.env***:
```
MAIL_USERNAME=<example@hotmail.com>
MAIL_PASSWORD=<*******>
```


### **testing:**
```
docker-compose run app pytest
```