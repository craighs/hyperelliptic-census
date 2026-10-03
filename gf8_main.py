import multiprocessing as mp
from gf8_worker import process_branch

if __name__ == '__main__':
    print("Starting Multiprocessing Exhaustive Search for GF(8)...")
    print("Splitting 16.7 million combinations across 4 CPUs.")
    
    # Generate the 8 starting branches (i = 0 through 7)
    branches = list(range(8))
    
    # Launch the pool of 4 workers
    with mp.Pool(processes=4) as pool:
        results = pool.map(process_branch, branches)
        
    print("\n" + "="*40)
    print("ALL PROCESSES COMPLETE!")
    for res in results:
        print(res)
