import sys

from ingestion import *
from nnet import *

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
    conv_data = alms(pgn_data)

    Y = torch.tensor()

    # NEURAL NETWORK TRAINING
    brain = FFNN(input_dim, output_dim, [14*8*8, 64*28, 64*56])

    # need to write a mapping function for input to output format



if __name__ == "__main__":
	pipeline();