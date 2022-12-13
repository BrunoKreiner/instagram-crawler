# Use python 3.8
FROM python:3.8-slim

# Create directory for project.
WORKDIR /app

# Copy root folder to container /project folder.
COPY . .

# Add our code to the Python path.
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install the dependencies.
RUN pip install -r requirements.txt

# Set python as the default program to execute in the container.
ENTRYPOINT [ "python", "crawl.py" ]

# Run the crawler.
CMD [ "-account-name", "elonmusk" ]