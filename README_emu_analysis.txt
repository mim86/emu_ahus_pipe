README: Emu Results Concatenation Script


This script (emu_analysis_v4.py) merges multiple Emu results files from a sequencing run and applies the specified set of cutoffs, including a special mock abundance-based filtering.

The script must be run in the emu directory:
1. Open terminal
2. cd /mnt/Disk2/projects/16s/emu/

## Usage

### Required Argument

--current_run RUN_NAME : Specifies the run name, the directory where the Emu result files are results/RUN_NAME/emu_results/.

### Optional Arguments

--keep species,genus,family,etc : Keeps the columns of the specified taxonomic levels (No spaces between the column names only commas!!!)

--filter_by_abundance FLOAT : Keeps rows where abundance is greater than the given value (accepted vaues 0-1).

--filter_by_counts INT : Keeps rows where estimated counts is greater than the given value (accepted values integer).

--mock_abundance barcodeXX : Specifies the barcode of a mock sample, requires --mock_key to be specified

--mock_key FILE : Path to a file listing species in the mock sample. Used to determine the minimum abundance threshold for filtering.

### Special Mock Abundance Processing

If --mock_abundance is provided:

The script looks for barcodeXX_filtered_rel-abundance.tsv in results/RUN_NAME/emu_results/.

It reads the species list from --mock_key (for example species.txt)

It identifies the minimum abundance for these species in the mock sample.

If --filter_by_counts is also provided, filtering is applied first on estimated counts, then using the identified minimum abundance.

Important Constraints

--mock_abundance requires --mock_key and --filter_by_counts.

--mock_abundance cannot be used with --filter_by_abundance.


Example Commands

### Basic merging no filtering

python emu_analysis_v4.py --current_run 16S_prosjekt_07NOV24_2

### Basic merging keeping only selected columns, no filtering

python emu_analysis_v4.py --current_run run1 --keep species,genus,family

### Filtering by Abundance and Counts (they can be used seprately)************ this oneeeeee :) 

python emu_analysis_v4.py --current_run Flongle_MAB_31OKT25_35 --keep species,genus,family --filter_by_abundance 0.00001 --filter_by_counts 20

### Mock Sample-Based Filtering (exaple)

python emu_analysis_v4.py --current_run Flongle_MAB_31OKT25_35 --keep species,genus,family --mock_abundance barcode19 --mock_key mock_species.txt --filter_by_counts 20

#### Output Files

Merged file: results/16S_prosjekt_07NOV24_2/emu_results/16S_prosjekt_07NOV24_2_all_emu_rel_abundance.tsv

Filtered file (if applied): results/RUN_NAME/emu_results/RUN_NAME_filtered_[conditions]_emu_rel_abundance.tsv

Example: run1_filtered_counts_20_mock_abundance_0.005_emu_rel_abundance.tsv

