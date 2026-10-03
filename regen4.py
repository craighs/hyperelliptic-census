import itertools

def generate_4b_file(filename="4b.txt"):
    # Generate all 65,536 combinations of 0, 1, 2, 3 for 8 positions
    combinations = itertools.product([0, 1, 2, 3], repeat=8)
    
    with open(filename, 'w') as f:
        for combo in combinations:
            # Convert the tuple of ints to a space-separated string
            line = " ".join(str(val) for val in combo)
            f.write(line + "\n")
            
    print(f"Successfully generated {filename} with 65,536 combinations!")

if __name__ == "__main__":
    generate_4b_file()
