import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split

# try:
# 	data = pd.read_csv("training_data.csv")
# except Exception as e:
# 	print("Training data not found.")
# 	print("Error (CSV):", e)


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
	def __init__(self, input_dim: int, output_dim: int, hidden_dim: list[int] = []):
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


# ---------------- Training -------------------

def training(model: nn.Module, 
			 X: torch.Tensor, 
			 y: torch.Tensor, 
			 epochs: int, 
			 batch_size: int, 
			 lr: float, 
			 train_ratio: float):
	'''
	Inputs:
		model: Neural network class object, can have any custom model architecture (even non-NN technically)
		X: (N, 28, 8, 8) tensor - Set of positions, these should already be processed by the input formatting
		y: (N, ???) - Set of moves, these should also be processed based on whatever format we choose
		epochs: int
		batch_size: int
		lr: float
		train_ratio: float

	Output:
		model: Same Neural Network class object, but with trained parameters
		
	This function will fully train a model with the data, to invoke simple do:
		model = training(...)
	'''
	# TODO: Consider adding validation for correct inputs, this can include checking if the model architecture is
	# compatible with the data

	# This is important, it is also important to ensure the tensor objects you're working with are on the same hardware
	device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
	model = model.to(device)
	if device == torch.device('cpu'):
		print('[WARNING] Training being done on cpu device')

	data = TensorDataset(X, y)

	train_size = int(train_ratio * len(data))
	val_size = len(data) - train_size
	data_train, data_val = random_split(data, [train_size, val_size])

	train_loader = DataLoader(data_train, batch_size=batch_size, shuffle=True)
	val_loader = DataLoader(data_val, batch_size=batch_size, shuffle=False)

	loss_fn = nn.CrossEntropyLoss() # This is a standard loss function but can be changed
	optimizer = optim.Adam(model.parameters(), lr=lr)

	print(f'[INFO] ------- Starting training on device: {device} -------')
	for epoch in range(epochs):

		# ---------- Training Phase ----------
		model.train() # Apparently this is a thing in torch which improves training quality
		train_loss = 0.0

		for X_b, y_b in train_loader:
			X_b, y_b = X_b.to(device), y_b.to(device)

			pred = model(X_b)
			loss = loss_fn(pred, y_b)
			optimizer.zero_grad()
			loss.backward()
			optimizer.step()

			train_loss += loss.item() * X_b.size(0) # torch calculates avg loss, hence the multiply

		epoch_train_loss = train_loss / len(data_train)

		# ---------- Validation Phase ----------
		model.eval() # Apparently this is also a thing and helps improve validation quality
		val_loss = 0.0

		with torch.no_grad(): # To disable gradient tracking and speed up validation
			for X_b, y_b in val_loader:
				X_b, y_b = X_b.to(device), y_b.to(device)

				pred = model(X_b)
				loss = loss_fn(pred, y_b)

				val_loss += loss.item() * X_b.size(0)

		epoch_val_loss = val_loss / len(data_val)

		if (epoch + 1) % (epochs / 10) == 0:
			print(f'[INFO] Epoch {(epoch + 1)}/{epochs} - train_loss={epoch_train_loss:.4f} | val_loss={epoch_val_loss:.4f}')

	print('[INFO] ------- Training complete -------')
	return model


# ---------------------------------------------


# -------------- Unit Tests -------------------

if __name__ == '__main__':
	print('[INFO] ======= Neural Network models testing start =======')

	torch.manual_seed(42)

	# TODO: This line is being reused in training() as well, I'm a little lazy to fix this right now
	device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')

	# Add unit tests here as and when needed

	# ------------- FFNN Test ---------------

	X_syn = torch.randn(1000, 2)
	y_syn = (X_syn[:, 0] + X_syn[:, 1] > 0).long() # Binary classification. 1 if feat_1 + feat_2 > 0, else 0

	model = FFNN(2, 2, [8])

	training(model, X_syn, y_syn, epochs=20, batch_size=32, lr=0.01, train_ratio=0.8)

	X_test_1 = torch.tensor([-0.33, 0.77]).to(device)
	X_test_2 = torch.tensor([0.25, 0.15]).to(device)
	X_test_3 = torch.tensor([-0.5, 0.1]).to(device)

	y_pred_1, y_pred_2, y_pred_3 = torch.argmax(model(X_test_1)), torch.argmax(model(X_test_2)), torch.argmax(model(X_test_3))
	y_test_1, y_test_2, y_test_3 = 1, 1, 0

	if y_pred_1 == y_test_1: print(f'[PASS] FFNN Test-1 passed')
	else: print(f'[FAIL] FFNN Test-1 failed, expected {y_test_1} but got {y_pred_1}')
	if y_pred_2 == y_test_2: print(f'[PASS] FFNN Test-2 passed')
	else: print(f'[FAIL] FFNN Test-2 failed, expected {y_test_2} but got {y_pred_2}')
	if y_pred_3 == y_test_3: print(f'[PASS] FFNN Test-3 passed')
	else: print(f'[FAIL] FFNN Test-3 failed, expected {y_test_3} but got {y_pred_3}')

	# ----------------------------------------

	print('[INFO] ======= Neural Network models testing done =======')

# ---------------------------------------------
