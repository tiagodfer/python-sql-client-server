import sqlite3
import random
import argparse
import os

def generate_random_cpf_list(quantity=10, db_path='db/basecpf.db'):
    """
    Generate a list of random CPFs and names from the database.
    
    Args:
        quantity: Number of CPF records to retrieve
        db_path: Path to the SQLite database
        
    Returns:
        Tuple of (cpf_list, name_list) where each is a list of strings
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the total count of records to determine the range for random selection
        cursor.execute("SELECT COUNT(*) FROM cpf")
        total_records = cursor.fetchone()[0]
        
        if quantity > total_records:
            print(f"Warning: Requested {quantity} records but database only has {total_records}.")
            print(f"Returning {total_records} records instead.")
            quantity = total_records
            
        # Select random records
        # Using ORDER BY RANDOM() is simple but less efficient for large databases
        cursor.execute(f"SELECT cpf, nome FROM cpf ORDER BY RANDOM() LIMIT {quantity}")
        results = cursor.fetchall()
        
        # Separate CPFs and names into distinct lists
        cpf_list = [cpf for cpf, _ in results]
        name_list = [name for _, name in results]
            
        conn.close()
        return cpf_list, name_list
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return [], []
    except Exception as e:
        print(f"Error: {e}")
        return [], []

def main():
    parser = argparse.ArgumentParser(description='Generate random CPF and name pairs from database')
    parser.add_argument('-q', '--quantity', type=int, default=10, 
                        help='Number of random CPF records to retrieve (default: 10)')
    parser.add_argument('-o', '--output', type=str,
                        help='Base output filename (without extension) to save results (optional)')
    parser.add_argument('-d', '--database', type=str, default='db/basecpf.db',
                        help='Path to the database file (default: db/basecpf.db)')
    
    args = parser.parse_args()
    
    cpf_list, name_list = generate_random_cpf_list(args.quantity, args.database)
    
    cpf_output = ','.join(cpf_list)
    name_output = ','.join(name_list)
    
    if args.output:
        try:
            cpf_filename = f"{args.output}_cpfs.csv"
            name_filename = f"{args.output}_names.csv"
            
            # Write CPF file
            with open(cpf_filename, 'w', encoding='utf-8') as f:
                f.write(cpf_output)
            
            # Write name file
            with open(name_filename, 'w', encoding='utf-8') as f:
                f.write(name_output)
                
            print(f"CPFs saved to {cpf_filename}")
            print(f"Names saved to {name_filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")
            print("CPFs:", cpf_output)
            print("Names:", name_output)
    else:
        print("CPFs:", cpf_output)
        print("Names:", name_output)

if __name__ == "__main__":
    main()