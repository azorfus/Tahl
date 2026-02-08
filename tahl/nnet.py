import numpy as np
import pandas as pd

data = pd.read_csv("training_data.csv")

# Activation functions
def ReLU(Z):
	return np.maximum(Z, 0)

def softmax(Z):
	A = np.exp(Z) / sum(np.exp(Z))
	return A

class nn_layer:
	w = np.array()
	b = np.array()

class network:
	inl = nn_layer()
	outl = nn_layer()
	hiddenl = []

	def __init__(self, hidden_no = 1):
		for i in range(hidden_no):
			hiddenl.append(nn_layer())

	def forward_prop(self):

	def back_prop(self);

def gradient_descent(X, Y, iterations, alpha):
	return None

def make_predictions():
	return None
