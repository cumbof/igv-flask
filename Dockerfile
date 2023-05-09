FROM python:3.7-alpine

# Create app directory
WORKDIR /igv

# Install app dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir igv-flask

# Bundle app source
COPY . .

EXPOSE 5000