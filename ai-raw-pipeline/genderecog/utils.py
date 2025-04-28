import os
import tqdm
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout


label2int = {
    "male": 1,
    "female": 0
}


def load_data(vector_length=128):
    """
    A function to load gender recognition dataset from `data` folder
    After the second run, this will load from results/features.npy and 
    results/labels.npy files as it is much faster!
    """

    try:
        # make sure results folder exists
        if not os.path.isdir("data/results"):
            print("make results directory")
            os.mkdir("data/results")

        if os.path.isfile("results/features.npy") and os.path.isfile(
            "results/labels.npy"):
            print("features & labels already loaded individually and bundled"), 
            X = np.load("data/results/features.npy")
            y = np.load("data/results/labels.npy")
            return X, y

        # make sure results folder exists
        if not os.path.isdir("data/combined.csv"):
            print("make combined CSV")
            with open('data/train.tsv', 'r') as fp:
                combi = fp.read()

            combi = combi.replace("common_", "data/train/common_").replace(
                ".mp3", ".npy")

            with open('data/combined.csv', 'w') as fp:
                fp.write(combi)

        # print("read combined dataframe")
        df = pd.read_csv("data/combined.csv")

        # print("get total samples")
        n_samples = len(df)

        # print("get total male samples")
        n_male_samples = len(df[df['gender'] == 'male'])

        # print("get total female samples")
        n_female_samples = len(df[df['gender'] == 'female'])

        print("Total samples:", n_samples)
        print("Total male samples:", n_male_samples)
        print("Total female samples:", n_female_samples)

        # print("initialize an empty array for all audio features")
        X = np.zeros((n_samples, vector_length))

        # print("initialize an empty array for all audio labels (1 for male and 0 for female)")
        y = np.zeros((n_samples, 1))

        for i, (filename, gender) in tqdm.tqdm(enumerate(zip(
            df['path'], df['gender'])), "Loading data", total=n_samples):
            pass
            features = np.load(filename)
            X[i] = features
            y[i] = label2int[gender]

        print("save the audio features and labels into files")

        np.save("data/results/features", X)
        np.save("data/results/labels", y)

        return X, y
    except Exception as e:
        print("Load Data Error {}".format(e))

    return False


def split_data(X, y, test_size=0.1, valid_size=0.1):
    """
    split dataset here
    """

    try:
        print("split training set and testing set")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=7)

        print("split training set and validation set")

        X_train, X_valid, y_train, y_valid = train_test_split(
            X_train, y_train, test_size=valid_size, random_state=7)

        print("return a dictionary of values")
        return {
            "X_train": X_train,
            "X_valid": X_valid,
            "X_test": X_test,
            "y_train": y_train,
            "y_valid": y_valid,
            "y_test": y_test
        }
    except Exception as e:
        print("Split Data Error {}".format(e))

    return {}


def create_model(vector_length=128):
    print("5 hidden dense layers from 256 units to 64, not the best model, but not bad.")

    model = Sequential()
    model.add(Dense(256, input_shape=(vector_length,)))
    model.add(Dropout(0.3))
    model.add(Dense(256, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(128, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.3))
    # one output neuron with sigmoid activation function, 0 means female, 1 means male
    model.add(Dense(1, activation="sigmoid"))
    # using binary crossentropy as it's male/female classification (binary)
    model.compile(loss="binary_crossentropy", metrics=["accuracy"], optimizer="adam")
    # print summary of the model
    model.summary()
    
    return model

if __name__ == '__main__':
    load_data()
    