import numpy as np
import pandas as pd

try:
	data = pd.read_csv("training_data.csv")
except Exception as e:
	print("Training data not found.")
	print("Error (CSV):", e)

# Activation functions
def sigmoid(Z):
	A = 1 / (1 + np.exp(-Z))  
	return A

def ReLU(Z):
	return np.maximum(Z, 0)

def softmax(Z):
	A = np.exp(Z) / sum(np.exp(Z))
	return A

class NNlayer:
	w = None
	b = None
	z = None

	def __init__(self, shape=[1, 1]):
		self.w = np.random.random(shape)
		self.b = np.zeros(shape, dtype=float)
		
		# holds previous layer's output value
		self.z = self.w

class Network:
	layers = []

	def __init__(self, layer_count = 1, shapes=[[1, 1],
												[1, 1],
												[1, 1]]):
		if layer_count < 1:
			print("Enter valid layer count")
			return None
		elif layer_count > 1 and shapes == [[1, 1],
											[1, 1],
											[1, 1]]:
			print("Enter valid layers")
			return None

		for i in range(layer_count + 2):
			self.layers.append(NNlayer(shapes[i]))

	def check(self):
		for i in self.layers:
			print(i.w)
			print(i.b)
			print(i.z)
			print()

	def forward_prop(self, l_index):
		try:
			Z = np.dot(self.layers[l_index].z, self.layers[l_index].w) + self.layers[l_index].b
			Z = sigmoid(Z)
			self.layers[l_index].z = Z
		except Exception as e:
			print("Error (invalid layer definition):", e)

def back_prop():
		pass

def gradient_descent(X, Y, iterations, alpha):
	return None

def make_predictions():
	return None
