import csv
from collections import Counter

def analyze_dataset(q):
    file_path = f'gf{q}_jacobian_groups_repaired.csv'
    
    print(f"Loading data from {file_path}...")
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Are you in the right directory?")
        return

    # 1. Aggregate Abelian Group Structures
    print(f"\n--- Jacobian Abelian Group Distribution (GF({q})) ---")
    
    # Count frequencies
    groups = [row['abelian_group_structure'] for row in rows]
    group_counts = Counter(groups)
    
    # Sort by frequency descending
    sorted_counts = group_counts.most_common()
    
    # Print the top 25 most common structures to the terminal
    print(f"{'Group Structure':<40} {'Frequency'}")
    print("-" * 55)
    for structure, count in sorted_counts[:25]:
        print(f"{structure:<40} {count}")
        
    print(f"\nTotal unique group structures found: {len(sorted_counts)}")
    print(f"Total geometric anchors analyzed: {len(rows)}")
    
    # 2. Hasse-Weil Bounds: Find the Maximal Curve(s)
    max_points = max(int(row['target_order']) for row in rows)
    maximal_curves = [row for row in rows if int(row['target_order']) == max_points]
    
    print(f"\n--- Maximal Genus 2 Curves over GF({q}) ---")
    print(f"Maximum Jacobian points (target_order): {max_points}")
    print(f"Number of maximal geometric anchors found: {len(maximal_curves)}")
    print("Maximal Curve Group Structure(s):")
    
    # Get unique group structures for the maximal curves
    maximal_structures = set(row['abelian_group_structure'] for row in maximal_curves)
    for structure in maximal_structures:
        print(f"  - {structure}")

    # 3. Save the full aggregation to a new CSV
    summary_file = f'gf{q}_group_distribution.csv'
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Group Structure', 'Frequency'])
        for structure, count in sorted_counts:
            writer.writerow([structure, count])
            
    print(f"\nFull distribution saved to {summary_file}")

if __name__ == "__main__":
    analyze_dataset(2)
