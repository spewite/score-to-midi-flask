# 🎼 Score-to-MIDI (Backend)

This is the **backend** for the Score-to-MIDI project. It receives sheet music images from the frontend, processes them using **Audiveris** to extract the music notation, converts the result into a MIDI file using **Music21**, and returns the generated MIDI file.

## 🛠 Technologies Used

- **Audiveris** – Optical Music Recognition (OMR) software for reading sheet music.
- **Music21** – Python library for musical score analysis and conversion.

## 📦 Installation & Setup

### Prerequisites

Ensure you have:

- [Python 3.12.3+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1️⃣ Clone the repository and install dependencies:

```bash
git clone https://github.com/spewite/score-to-midi-flask
cd score-to-midi-flask
```

2️⃣ Create a virtual environment and activate it

# On macOS and Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

# On Windows
```bash
python -m venv venv
venv\Scripts\activate
```

3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### Run the server

```bash
flask --app app.py --debug run
```



