<!-- GENERAL -->
# Give full permissions to files inside folder
chmod -R 777 ./logs

<!-- PYTHON -->

# Run development enviroment 
flask --app app.py --debug run

# Create virtual enviroment 
python3 -m venv venv

# Activate / Deactivate
source venv/bin/activate
deactivate

# Install packages.
pip install -r requirements.txt

# Generate venv library list.
pip freeze > requirements.txt


<!-- DOCKER -->

# List docker images
docker images

# List running docker containers
docker ps

# List all docker containers
docker ps -a

# Build image 
docker build -t score-to-midi .

# Run image 
docker run [-d] -p 5000:5000 score-to-midi
docker run -e PYTHONUNBUFFERED=1 -p 5000:5000 score-to-midi
docker run -e PYTHONUNBUFFERED=1 -p 5000:5000 --cpus="1.0" --memory="1G" score-to-midi

# Delete stopped containers
docker container prune

# Delete images that are not used by any container
docker image prune

# Force image delete 
docker rmi -f container-id
