EMU - 16s pipeline

working directory: /mnt/Disk2/16s/emu

Directory organisation:

	Input files and folders
	
	1. emu_env - locker conda environment
	2. emu_database - emu database - can be updated (remind me from time to time to check for new versions).
	3. raw_data - input fastq.gz should be put here - each run should have its own folder in the raw_data (continue reading)
	4. config.yml - snakemake editable file
	5. snakefile - snakemake non-editable file
	
	Output folder
	1. Main output folder results/
	2. For each input folder with the fastq file in the raw_data, a specific subfolder with the same name will be generated here
	3.  emu_results - the abundance file and the rest of the emu files (continue reading)
	4. filtered (optional can be removed in a clean up) - contains the filtlong filtered fastq files that goes into the emu. 
	5. QC_nanoplot - quality check-ups for all the non-filtered fastq files (raw reads)
	6. logs - not important, used only by snakemake for to signal that the file is processed
	
	

How to run:
 0. Enter the directory
 
 cd /mnt/Disk2/16s/emu/

 1. Activate conda environment
 
 source emu_env/bin/activate
 
 
 2. Open folder raw_data (ikke terminal)
 
 3. Make a new folder (ctrl+shift+n) - name it with a run identifier
 
 4. Gå tilbake til terminalen
 
 5. run the script ./concatenate_me.sh
 ./concatenate_me.sh /media/miks/Seagate_Backup_Plus_Drive/Empyemer_07JAN26_etOH/fastq_pass raw_data/Empyemer_07JAN26_etOH/
 
 FOLDER_NAME_INPUT - replace it with the actual folder name in on the hard drive
 FOLDER_NAME_OUTPUT - replace it with the actual folder name with that you made in the raw_data (step 3.) 
 
 6. Go back to main direcotry (emu, not in terminal) and open the config.yml file.
 
 clean: "no" - do not change this is only default - to avoid piling up of useless files, the filtered read files are removed after the run
 
raw_data_base_dir: "/mnt/Disk2/projects/16s/emu/raw_data" - where snakemake looks for fastq file - do not change

results_base_dir: "results" - the name of the main result folder 
 
 
 filtlong: 
  min_length: 1200 - minimum length of reads to be kept 
  max_length: 1600 - maximum lenght of reads to be kept
  min_mean_q: 30 - quality of reads - 30 indicates to keep reads that has lass than 0.01% to have errors, 20 would be 0.1%, I would keep it at 20 at least
  
  emu:
  type: "map-ont" - indication that we have ONT reads
  min_abundance: 0.0001 - minimum abundance cutoff for a species to be reported by emu - 0.0001 corresponds to 0.01 % - it can be increased but we need to test! 
  
  db: "/mnt/Disk2/projects/16s/emu/emu_database" - the location od emu database
  
  N: 50 - do not change
  K: "300000" - do not change
  mm2_forward_only: False - do not change
  output_basename: "" - do not change
  keep_files: False - If set to True - it will keep the mapping files (sam/bam)
  keep_counts: True - Keeps the "absolute counts" - they are not really really absolute but rather how many reads had a high likelihood to be mapped to the correct species
  keep_read_assignments: True - this outputs the table read-assignemnt-distribution.tsv in the emu results folder - shows the name of the read and to which species it maps to. These files are important when some "crazy" results appear and should be investigated further - can be turned off by writing  False
  output_unclassified: True - If True, it outputs the fastq files with reads that were mapped but could not be classified with high likelihood. If the abundance results do look "crazy" these reads should be investigated further (for example quick blast)
  threads: 24 - number of cores - lets keep it like this for now :)
  
  Save the changes!
  
  7. run the pipe
  snakemake --snakefile snakefile_v8 --configfile config_v3.yml --cores 2 --config run_name=Empyemer_07JAN26_etOH clean=yes

  changables:
  	--cores - max 2! 
  	run_name=todays_run - replace the "todays_run" with the name of the folder where you placed the fastq.gz files
	clean=yes - yes to remove the filtered files (recommended) :)
  
