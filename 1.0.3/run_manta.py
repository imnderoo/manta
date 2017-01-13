#!/usr/bin/python

import os, sys, subprocess
import shutil
import argparse #AW: Package for parsing arguments
import re, glob

def main():
	#AW: This block of code is easy to reuse for any script that take in arguments
	#----
	parser = argparse.ArgumentParser(description = 'Script to read VCF into DB for ALBI project')
	parser.add_argument('bam_list', help = 'File containing list of bams')
	parser.add_argument('out_dir', help = 'Full path to out_directory')
	parser.add_argument('genome', help = 'Full path to the genome')
	parser.add_argument('manta_target', help = 'List of regions targeted by manta')
	parser.add_argument('bam_suffix', help = 'Unique suffix following the Sample ID in BAM file')

	args = parser.parse_args()
	
	call_manta(args.bam_list, args.out_dir, args.genome, args.manta_target, args.bam_suffix)
	
def call_manta(bam_list, out_dir, genome, manta_target, bam_suffix):

	if not os.path.isdir(out_dir):
		os.makedirs(out_dir)

	# Manta - Call CNV for each bam in the bam list.
	#manta_config_cmd = "/media/sf_resources/tools/manta-1.0.3.centos5_x86_64/bin/configManta.py"
	manta_config_cmd = "/home/biodocker/manta-1.0.3.centos5_x86_64/bin/configManta.py"
	
	for in_bam in open(bam_list,'rb'):
		in_bam = in_bam.rstrip('\r\n')
		
		sample_id = os.path.basename(in_bam.split(bam_suffix)[0])

		manta_out = os.path.join(out_dir, sample_id)
		
		if not os.path.isdir(manta_out):
			os.makedirs(manta_out)
		
		# Manta - Builds 'a python workflow.py
		subprocess.call(" ".join([manta_config_cmd, \
			"--exome", \
			"--bam="+in_bam, \
			"--referenceFasta="+genome, \
			"--runDir="+manta_out, \
			manta_target]), shell=True)
		
		# Manta - Workflow.py performs the actual analysis
		subprocess.call(" ".join(["python",manta_out+"/runWorkflow.py", "-m", "local"]), shell=True)
			
		# Gunzip and copy results to main folder
		manta_results_dir = os.path.join(manta_out,"results","variants")
		subprocess.call(" ".join(["gunzip",manta_results_dir+"/*vcf.gz"]), shell=True)	
		shutil.copy(os.path.join(manta_results_dir,"diploidSV.vcf"), os.path.join(out_dir,sample_id+".manta.cnv.vcf"))
	
main()
	
	
