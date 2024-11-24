# Proyecto Django

## Pasos para Configurar el Entorno

### 1. Crear un Entorno Virtual

### Primero, crea un entorno virtual con el siguiente comando

venv\Scripts\activate

### 2.Mira el archivo requirements.txt y verifica si tienes esos módulos instalados con el siguiente comando

pip list

### 3. instala cada una de las dependencias

### 4. realiza las migraciones para la base de datos con el comando

python manage.py makemigrations

python manage.py migrate

### 5. ejecuta el comando para correr el servidor

python manage.py runserver

### por ultimo verifica que el servidor este funcionando no te preocupes si sale 404 o error en el navegador es normal
