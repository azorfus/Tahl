import numpy as np
import pandas as pd

data = pd.read_csv("training_data.csv")

class nn_layer:
	w = np.array()
	b = np.array()

# Activation functions
def ReLU(Z):
	return np.maximum(Z, 0)

def softmax(Z):
	A = np.exp(Z) / sum(np.exp(Z))
	return A

def init_params():
	layer1 = nn_layer()
	layer2 = nn_layer()
	layer3 = nn_layer()

	return layer1, layer2, layer3

def forward_prop(layer1, layer2, layer3):
	return None

def back_prop():
	return None

def update_params():
	return None

def gradient_descent(X, Y, iterations, alpha):
	return None

def make_predictions():
	return None
