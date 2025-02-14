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
