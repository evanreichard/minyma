# Build Container
FROM python:3.11-slim

# Install App
WORKDIR /app
COPY . /app

# Install Curl
RUN apt-get update -y
RUN apt-get install curl -y

# Install Chroma Dependencies
RUN mkdir -p /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/
RUN curl https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz --output /root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz

# Install App & Gunicorn
RUN pip install .
RUN pip3 install gunicorn

# Cleanup
RUN rm -rf /app

# Start Application
ENTRYPOINT ["gunicorn"]
EXPOSE 5000
CMD ["minyma:create_app()", "--bind", "0.0.0.0:5000", "--threads=4", "--access-logfile", "-"]
