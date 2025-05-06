import os
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping

from utils import load_data, split_data, create_model

batch_size = 64
epochs = 100

def train_mode():
    """
    Training Phase
    """

    try:

        print("load the dataset")
        X, y = load_data()

        if type(X) == bool:
            print("Load data Error")
            return

        print("split the data into training, validation and testing sets")
        data = split_data(X, y, test_size=0.1, valid_size=0.1)

        print("construct the model")
        model = create_model()

        print("use tensorboard to view metrics")
        tensorboard = TensorBoard(log_dir="logs")

        print(f"define early stopping to stop training after 5 epochs of not improving")
        early_stopping = EarlyStopping(mode="min", patience=5, restore_best_weights=True)

        """
        print("train the model using the training set and validating using validation set")
        model.fit(
            data["X_train"],
            data["y_train"],
            epochs=epochs, 
            batch_size=batch_size, 
            validation_data=(data["X_valid"], data["y_valid"]),
            callbacks=[tensorboard, early_stopping]
            )

        print("save the model to a file")
        model.save("results/model.h5")

        print(f"Evaluating the model using {len(data['X_test'])} samples...")
        loss, accuracy = model.evaluate(data["X_test"], data["y_test"], verbose=0)

        print(f"Loss: {loss:.4f}")
        print(f"Accuracy: {accuracy*100:.2f}%")
        """

    except Exception as e:
        print("Training Error ".format(e))


if __name__ == '__main__':
    train_mode()
    