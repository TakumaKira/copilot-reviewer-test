import pickle

def load_data(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)  # unsafe deserialization
