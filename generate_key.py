import pickle
from pathlib import Path

from streamlit_authenticator.utilities.hasher import Hasher

names = ["Peter Parker"]
usernames = ["peterparker"]
passwords = ["spiderman"]

hashed_passwords =Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as f:
    pickle.dump(hashed_passwords, f)