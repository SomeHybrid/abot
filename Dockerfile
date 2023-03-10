FROM python:3.11.1

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
    
COPY . .

CMD [ "python", "./main.py" ]