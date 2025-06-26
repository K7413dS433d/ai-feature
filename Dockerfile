
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY . .


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 8000


CMD ["uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000"]
