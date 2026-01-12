# EMU – 16S pipeline

**Working directory:** `/mnt/Disk2/16s/emu`

## Directory organisation

### Input files and folders
1. `emu_env_original/` – conda-packed environment (locked)
2. `emu_database/` – EMU database (can be updated; check periodically for new versions)
3. `raw_data/` – input `fastq.gz` files go here  
   Each sequencing run should have its **own subfolder** inside `raw_data/` (see below).
4. `config.yml` – **editable** Snakemake configuration file
5. `snakefile` / `snakefile_v8` – Snakemake workflow (**do not edit**)

### Output folders
1. `results/` – main output folder
2. For each run folder in `raw_data/`, a matching subfolder is created in `results/`
3. `emu_results/` – EMU output (abundance + other EMU files)
4. `filtered/` – optional (can be removed during cleanup); contains Filtlong-filtered FASTQ used as EMU input
5. `QC_nanoplot/` – NanoPlot QC for the **raw** (unfiltered) FASTQ files
6. `logs/` – Snakemake bookkeeping/logging (mostly for pipeline internals)

---

## Installation and running (conda-pack based)

### 0) Install Git LFS (required)
```bash
sudo apt update
sudo apt install git-lfs
git lfs install
```

### 1) Clone the repository
```bash
git clone https://github.com/mim86/emu_ahus_pipe.git
cd emu_ahus_pipe
git lfs pull
```

### 2) Unpack the conda-packed environment
```bash
cd emu_env_original
mkdir -p emu_metagenomics_env
tar -xvzf emu_metagenomics.tar.gz -C emu_metagenomics_env
```

### 3) Activate the environment (from repo root)
```bash
source emu_env_original/emu_metagenomics_env/bin/activate
conda unpack
```

---

## Input data layout

Place samples inside `raw_data/`. Create **one folder per run**, for example:  
`raw_data/todays_run/` (or any run name you choose).

### Optional: concatenate multiple FASTQs per barcode
If your run produces multiple FASTQs per barcode, you can optionally use:
```bash
./concatenate_me.sh nanopore/example/run/fastq_pass raw_data/your_run/
```
This can generate one combined file per barcode (e.g., `barcodeXX.fastq.gz`).

---

## Config: editing `config.yml`

Below are the key settings to review.

### General
`clean: "no"`  
Controls whether the intermediate filtered reads are kept. This can also be overridden on the Snakemake command line via `--config clean=yes|no`.

`raw_data_base_dir: "/mnt/Disk2/16s/emu/raw_data"`  
Where Snakemake looks for run folders and `fastq.gz` files.

`results_base_dir: "results"`  
Name (or path) of the main results directory.

### Filtlong
- `min_length: 1200` – minimum read length kept  
- `max_length: 1600` – maximum read length kept  
- `min_mean_q: 30` – mean read quality filter  
  Rough guide: Q30 ≈ 0.1% error rate, Q20 ≈ 1% error rate. I would keep **≥20** at minimum.

### EMU
- `type: "map-ont"` – indicates ONT reads
- `min_abundance: 0.0001` – minimum abundance cutoff (0.01%)  
  See EMU docs: https://github.com/treangenlab/emu
- `db: "/mnt/Disk2/16s/emu/emu_database"` – path to EMU database
- `threads: 24` – number of cores for EMU

Additional EMU flags used here:
- `keep_files: False` – keep mapping files (SAM/BAM) if `True`
- `keep_counts: True` – keep “counts” output (read support)
- `keep_read_assignments: True` – outputs `read-assignment-distribution.tsv` (useful for investigating weird results)
- `output_unclassified: True` – outputs FASTQ of reads that mapped but could not be confidently classified (useful for quick BLAST sanity checks)

Example (structure only; keep your values as needed):
```yaml
clean: "no"
raw_data_base_dir: "/absolute/path/to/the/raw_data"
results_base_dir: "results"

filtlong:
  min_length: 1200
  max_length: 1600
  min_mean_q: 30

emu:
  type: "map-ont"
  min_abundance: 0.0001
  db: "/absolute/path/to/the/emu_database"
  N: 50
  K: "300000"
  mm2_forward_only: False
  output_basename: ""
  keep_files: False
  keep_counts: True
  keep_read_assignments: True
  output_unclassified: True
  threads: 24
```

Save the file when done.

---

## Run the pipeline

Example command:
```bash
snakemake --snakefile snakefile_v8 --configfile config_v3.yml --cores 2 --config run_name=Empyemer_07JAN26_etOH clean=yes
```

Things you typically change:
- `--cores 2`  
  How many samples/files can be processed in parallel (increase if you have resources).
- `run_name=...`  
  Must match the **folder name** under `raw_data/` (e.g., `raw_data/Empyemer_07JAN26_etOH/`).
- `clean=yes`  
  Recommended if you want filtered intermediates removed after successful completion.


# Emu results concatenation script

This script (`emu_analysis_v4.py`) merges multiple Emu result files from a sequencing run and applies the selected cutoffs, including an optional **mock abundance-based** filtering mode.

**Run it from the EMU directory:**

## Usage

### Required argument
`--current_run RUN_NAME`  
Specifies the run name. The script expects Emu result files in:  
`results/RUN_NAME/emu_results/`

### Optional arguments
`--keep species,genus,family,...`  
Keeps only the specified taxonomic level columns. **No spaces** (comma-separated only).

`--filter_by_abundance FLOAT`  
Keeps rows where abundance is greater than the given value (accepted range: 0–1).

`--filter_by_counts INT`  
Keeps rows where estimated counts are greater than the given value (integer).

`--mock_abundance barcodeXX`  
Specifies the barcode of a mock sample. Requires `--mock_key`.

`--mock_key FILE`  
Path to a file listing mock species (e.g., `mock_species.txt`). Used to derive the minimum abundance threshold from the mock sample.

## Special mock abundance processing

If `--mock_abundance` is provided:

- The script looks for `barcodeXX_filtered_rel-abundance.tsv` in:  
  `results/RUN_NAME/emu_results/`
- It reads the species list from `--mock_key`
- It identifies the **minimum abundance** among those species in the mock sample
- If `--filter_by_counts` is also provided, filtering is applied **first** on counts, then using the identified minimum mock abundance

### Important constraints
- `--mock_abundance` requires `--mock_key` **and** `--filter_by_counts`
- `--mock_abundance` cannot be used together with `--filter_by_abundance`

## Example commands

### Basic merging (no filtering)
```bash
python emu_analysis_v4.py --current_run todays_run_1
```

### Merge + keep only selected columns (no filtering)
```bash
python emu_analysis_v4.py --current_run todays_run_1 --keep species,genus,family
```

### Filtering by abundance and counts (can also be used separately)
```bash
python emu_analysis_v4.py --current_run todays_run_1 --keep species,genus,family --filter_by_abundance 0.00001 --filter_by_counts 20
```

### Mock sample-based filtering (example)
```bash
python emu_analysis_v4.py --current_run todays_run_1 --keep species,genus,family --mock_abundance barcode19 --mock_key mock_species.txt --filter_by_counts 20
```

## Output files

**Merged file:**  
`results/RUN_NAME/emu_results/RUN_NAME_all_emu_rel_abundance.tsv`

Example:  
`results/16S_prosjekt_07NOV24_2/emu_results/16S_prosjekt_07NOV24_2_all_emu_rel_abundance.tsv`

**Filtered file (if applied):**  
`results/RUN_NAME/emu_results/RUN_NAME_filtered_[conditions]_emu_rel_abundance.tsv`

Example:  
`run1_filtered_counts_20_mock_abundance_0.005_emu_rel_abundance.tsv`
