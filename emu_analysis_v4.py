import os
import argparse
import pandas as pd
import glob

def concatenate_emu_results(current_run, keep, filter_by_abundance, filter_by_counts, mock_abundance, mock_key):
    # Define the directory and output file
    emu_results_dir = f"results/{current_run}/emu_results"
    output_file = f"{emu_results_dir}/{current_run}_all_emu_rel_abundance.tsv"
    
    # Find all matching files
    file_pattern = os.path.join(emu_results_dir, "barcode*_filtered_rel-abundance.tsv")
    tsv_files = sorted(glob.glob(file_pattern))
    
    if not tsv_files:
        print("No files found! Exiting...")
        return
    
    # Validate arguments
    if mock_abundance and not mock_key:
        raise ValueError("Error: --mock_abundance requires --mock_key!")
    if mock_key and not mock_abundance:
        raise ValueError("Error: --mock_key requires --mock_abundance!")
    if mock_abundance and filter_by_abundance is not None:
        raise ValueError("Error: --mock_abundance and --filter_by_abundance cannot be used together!")
    if mock_abundance and filter_by_counts is None:
        raise ValueError("Error: --mock_abundance requires --filter_by_counts!")
    
    dataframes = []
    valid_columns = ["species", "genus", "family", "order", "class", "phylum", "clade", "superkingdom", "subspecies"]
    default_columns = ["tax_id", "abundance", "estimated counts"]  # Default columns (fixed order)
    
    selected_columns = ["barcode"] + default_columns  # Start with barcode and defaults
    if keep:
        keep_list = [col.strip() for col in keep.split(",") if col.strip() in valid_columns]
        selected_columns = ["barcode"] + keep_list + default_columns  # Order per user input
    
    mock_abundance_value = None
    mock_file_path = os.path.join(emu_results_dir, f"{mock_abundance}_filtered_rel-abundance.tsv") if mock_abundance else None
    
    if mock_abundance:
        print(f"Mock abundance file expected: {mock_file_path}")
        print(f"Mock key file loaded: {mock_key}")
    
    for file in tsv_files:
        # Extract barcodeXX from filename
        barcode = os.path.basename(file).split("_")[0].replace("barcode", "")
        
        # Read TSV file
        df = pd.read_csv(file, sep="\t")
        
        # Remove rows where tax_id is "unmapped" or "mapped_unclassified"
        df = df[~df["tax_id"].isin(["unmapped", "mapped_unclassified"])]
        
        # Add barcode column as the first column
        df.insert(0, "barcode", barcode)
        
        # Keep only selected columns in the correct order
        df = df[[col for col in selected_columns if col in df.columns]]
        
        # If this is the mock sample, determine the minimum abundance for filtering
        if mock_abundance and os.path.basename(file) == os.path.basename(mock_file_path):
            print(f"Processing mock abundance file: {file}")
            if "species" not in df.columns:
                raise ValueError("Error: The mock file does not contain a 'species' column!")
            
            # Load species list from the mock key file
            with open(mock_key, "r") as f:
                mock_species_list = set(line.strip() for line in f if line.strip())
            
            print(f"Species in mock key ({len(mock_species_list)} entries): {mock_species_list}")
            
            # Print species in the mock abundance file
            print(f"Species present in mock file: {df['species'].unique().tolist()}")
            
            # Filter only matching species
            matching_mock_species = df[df["species"].str.strip().isin(mock_species_list)]
            print(f"Matching species in mock abundance file: {matching_mock_species['species'].tolist()}")
            
            if not matching_mock_species.empty:
                mock_abundance_value = matching_mock_species["abundance"].min()
                print(f"Identified minimum abundance threshold for filtering: {mock_abundance_value}")
    
        dataframes.append(df)
    
    # Concatenate all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Save to output file
    combined_df.to_csv(output_file, sep="\t", index=False)
    print(f"Merged file saved as: {output_file}")
    
    # Apply filtering
    if filter_by_counts is not None:
        combined_df = combined_df[combined_df["estimated counts"] > filter_by_counts]
    if mock_abundance_value is not None:
        combined_df = combined_df[combined_df["abundance"] > mock_abundance_value]
    elif filter_by_abundance is not None:
        combined_df = combined_df[combined_df["abundance"] > filter_by_abundance]
    
    # Save filtered file if any filtering was applied
    if filter_by_abundance is not None or filter_by_counts is not None or mock_abundance_value is not None:
        filter_suffix = "_filtered"
        if mock_abundance_value is not None:
            filter_suffix += f"_mock_abundance_{mock_abundance_value}"
        elif filter_by_abundance is not None:
            filter_suffix += f"_abundance_{filter_by_abundance}"
        if filter_by_counts is not None:
            filter_suffix += f"_counts_{filter_by_counts}"
        filtered_output_file = f"{emu_results_dir}/{current_run}{filter_suffix}_emu_rel_abundance.tsv"
        combined_df.to_csv(filtered_output_file, sep="\t", index=False)
        print(f"Filtered file saved as: {filtered_output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate Emu Results")
    parser.add_argument("--current_run", required=True, help="Run name")
    parser.add_argument("--keep", type=str, help="Comma-separated list of columns to keep (e.g., 'species,genus')")
    parser.add_argument("--filter_by_abundance", type=float, help="Filter rows with abundance greater than given value")
    parser.add_argument("--filter_by_counts", type=int, help="Filter rows with estimated counts greater than given value")
    parser.add_argument("--mock_abundance", type=str, help="Barcode of the mock sample")
    parser.add_argument("--mock_key", type=str, help="File containing correctly identified species for the mock sample")
    args = parser.parse_args()
    
    concatenate_emu_results(args.current_run, args.keep, args.filter_by_abundance, args.filter_by_counts, args.mock_abundance, args.mock_key)