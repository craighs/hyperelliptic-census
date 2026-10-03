import itertools

def generate_2b_file(filename="2b.txt"):
    # Generate all 256 combinations of 0s and 1s for 8 positions
    combinations = itertools.product([0, 1], repeat=8)
    
    with open(filename, 'w') as f:
        for combo in combinations:
            # Convert the tuple of ints to a space-separated string
            line = " ".join(str(val) for val in combo)
            f.write(line + "\n")
            
    print(f"Successfully generated {filename} with 256 combinations!")

if __name__ == "__main__":
    generate_2b_file()
