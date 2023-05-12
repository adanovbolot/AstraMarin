ЗАПУСК ПРОЕКТА


1. Собрать контейнер


    sudo docker-compose up --build -d

2. Зайти внутрь контейнера
    

    sudo docker exec -it django bash


3. Собрать все статические файлы

    
    python manage.py collectstatic


4. Создать админа для сервера

    
    python manage.py createsuperuser


5. Выйти из контейнера

    
    exit