#Code to run multicore parallelisation
import os
import glob
import subprocess
import multiprocessing

def execute_command(inputFileName,outputFileName):
    command = f'python h4ltaus.py {inputFileName} {outputFileName}'
    print(command)
    subprocess.run(command, shell=True)

def main():
    
    arguments = []
    num_cores = 14

    outputFileName = ''    
    outTag = 'h4ltaus'
    inputDirectory = '/scratch/gfrattar/hzz_tau/Signal/'
    inputFiles = glob.glob(inputDirectory+'/*.root')
    
    if not os.path.exists('./outputs/'):
        os.makedirs('./outputs')

    for i,fn in enumerate(inputFiles):
        outputFileName = 'output_'+outTag+'_'+str(i)+'.root'
        arguments.append([fn,outputFileName])

    with multiprocessing.Pool(processes=num_cores) as pool:
        pool.starmap(execute_command, arguments)
    
if __name__ == '__main__':
    main()