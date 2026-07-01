import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

try:
	data = pd.read_csv("training_data.csv")
except Exception as e:
	print("Training data not found.")
	print("Error (CSV):", e)


# ------------------ Helpers ------------------

def exp(Z):
	'''
	For any kind of exponentiation please use this function, DO NOT DIRECTLY USE torch.exp()
	'''
	return torch.exp(torch.clip(Z, -500, 500))

# ---------------------------------------------

# ----------- Activation functions ------------

# Considering that torch provides us with all these functions, these are probably going to be redundant, in fact I
# would discourage custom functions since it is possible to mishandle very large or very small values

def sigmoid(Z):
	A = 1 / (1 + exp(Z))  
	return A

def ReLU(Z):
	return torch.max(Z, 0)

def softmax(Z):
	A = exp(Z) / torch.sum(exp(Z))
	return A

# ---------------------------------------------

# --------- Basic feed foward network ---------
class FFNN(nn.Module):
	def __init__(self, input_dim: int, hidden_dim: list[int], output_dim: int):
		'''
		For initialization of NN, we pass the no. of input and output neurons, as well as a list containing the no. of
		neurons for each hidden layer
		'''
		super(FFNN, self).__init__()

		self.num_layers = len(hidden_dim) + 2

		# We want to store the layers in nn.ModuleList, creating a custom class for each layer is an option but torch 
		# gives us a simpler way to do it
		self.layers = nn.ModuleList()
		self.activation = nn.ReLU() # This can also be made a list technically

		# Not the best way of creation but oh well
		current_dim = input_dim
		for h in hidden_dim:
			self.layers.append(nn.Linear(current_dim, h))
			current_dim = h

		# We want to keep the final layer separate since it does not have an activation. Even if it does, a lot of times
		# the final layer activation function is distinct than the rest so this only helps
		self.output_layer = nn.Linear(current_dim, output_dim)

	def forward(self, X):
		'''
		Input: X is expected to be a tensor with shape (input_dim, )

		Observe carefully that it is NOT (input_dim, 1) but (input_dim, ). Ensure 1D tensors are of such a shape always
		'''
		# TODO: Consider adding validation to ensure input is of the right type and shape

		# Here a for loop is necessary because we are using nn.ModuleList, there is nn.Sequential as well, we can consider
		# using it later if needed (it allows a single line forward instead of a for loop like this)
		for layer in self.layers:
			X = layer(X)
			X = self.activation(X)
			
		X = self.output_layer(X)
		return X # Notice how I used the input arg directly, this is actually safe with torch tensors

# ---------------------------------------------



# ============ OLD CODE, REDUNDANT ============

# class NNlayer:
# 	w = None
# 	b = None
# 	z = None

# 	def __init__(self, shape=[1, 1]):
# 		self.w = np.random.random(shape)
# 		self.b = np.zeros(shape, dtype=float)
		
# 		# holds previous layer's output value
# 		self.z = self.w

# class Network:
# 	layers = []

# 	def __init__(self, layer_count = 1, shapes=[[1, 1],
# 												[1, 1],
# 												[1, 1]]):
# 		if layer_count < 1:
# 			print("Enter valid layer count")
# 			return None
# 		elif layer_count > 1 and shapes == [[1, 1],
# 											[1, 1],
# 											[1, 1]]:
# 			print("Enter valid layers")
# 			return None

# 		for i in range(layer_count + 2):
# 			self.layers.append(NNlayer(shapes[i]))

# 	def check(self):
# 		for i in self.layers:
# 			print(i.w)
# 			print(i.b)
# 			print(i.z)
# 			print()

# 	def forward_prop(self, l_index):
# 		try:
# 			Z = np.dot(self.layers[l_index].z, self.layers[l_index].w) + self.layers[l_index].b
# 			Z = sigmoid(Z)
# 			self.layers[l_index].z = Z
# 		except Exception as e:
# 			print("Error (invalid layer definition):", e)

# def back_prop():
# 		pass

# def gradient_descent(X, Y, iterations, alpha):
# 	return None

# def make_predictions():
# 	return None

# =============================================
