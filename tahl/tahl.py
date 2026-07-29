import sys

from ingestion import *
from nnet import *
from excretion import mimic_output

input_dim = 28*8*8
output_dim = 64*73

# Main pipeline 
def pipeline():
    if len(sys.argv) <= 1:
        print("[!] Expected file name!")
        return

    if sys.argv[1] == 'F':
        F = sys.argv[2]
        pgn_data = PGNMatter(F, True)
    else:
        F = sys.argv[1]
        pgn_data = PGNMatter(F, False)
    
	# DATA CONVERSION
    conv_data, pgn_array = alms(pgn_data, quantity = 50)

    # NEURAL NETWORK TRAINING
    brain = FFNN(input_dim, output_dim, [14*8*8, 64*28, 64*56])

    Y = mimic_output(conv_data, pgn_array)

    # trained_brain = brain.training(conv_data, Y, epochs, batch_size, lr, train_ratio)
    # store_brain(trained_brain, storagefile_location)

if __name__ == "__main__":
    pipeline()