FROM python:3.6

EXPOSE 5000

WORKDIR /app

# Set proxy variables to enable pip install
ENV HTTP_PROXY "http://proxy.cat.com:80"
ENV HTTPS_PROXY "http://proxy.cat.com:80"
ENV NO_PROXY "localhost"

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY app.py /app
COPY templates /app/templates

CMD python app.py
