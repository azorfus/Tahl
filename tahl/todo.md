### AZORFUS

## In `ingestion.py`
- `process_pgn` and `PGNMatter` individually are fine, but their functionalities are very similar and do not need to be kept separate, look to execute their functionalities simultaneously. Basically create bitboards as you parse the pgn files
- Every other function in this file is doubtful in terms of correctness, look at what is truly needed and refine their implementations (drop whatever functions end up being redundant)
- When writing functions, use type-hinting to pass the datatypes of arguments and return values, helps in seeing the expected types and return types when calling them
- Use any built-in functions from the `chess` library whenever possible, look up documentation or just google from time to time
- Ensure that overall ingestion returns two tensors, the bitboards (N x 28 x 8 x 8) and the moves (N x 4672)

- Include pawn promotion information in the bitboard layers (Pawn promotion information is encoded in the move not the bitboard, that we should indeed ensure. UCI format move strings encode this via a 5th character at the end, use that - lookup UCI format move encoding if needed)

## In `excretion.py`
- Polish the fetch_move() func
- Write the coordtomove() func

## **Complete the main pipeline**