### Script to submit Condor jobs for LHE event generation at UCSD

### Authors:
### Ana Ovcharova
### Dustin Anderson

import os
import sys
import argparse

def submitCondorJob(proc, executable, options, infile, label, outputToTransfer=None, submit=False, proxy="/tmp/x509up_u31156", isGridpackJob=False):
    subfile = "condor_"+proc +"_"+label+".cmd"
    f = open(subfile,"w")
    f.write("Universe = vanilla\n")
    #f.write("Grid_Resource = condor cmssubmit-r1.t2.ucsd.edu glidein-collector.t2.ucsd.edu\n")
    f.write("x509userproxy={0}\n".format(proxy))
    f.write("+DESIRED_Sites=\"T2_US_UCSD\"\n")
    if isGridpackJob :
        f.write("+request_cpus=8\n")
    f.write("Executable = "+executable+"\n")
    f.write("arguments =  "+(' '.join(options))+"\n")
    f.write("Transfer_Executable = True\n")
    f.write("should_transfer_files = YES\n")
    f.write("transfer_input_files = "+infile+"\n")
    if outputToTransfer is not None:
        f.write("transfer_Output_files = "+outputToTransfer+"\n")
        f.write("WhenToTransferOutput  = ON_EXIT\n")
    f.write("Notification = Never\n")
    f.write("Log=gen_"+proc+"_"+label+".log.$(Cluster).$(Process)\n")
    f.write("output=gen_"+proc+"_"+label+".out.$(Cluster).$(Process)\n")
    f.write("error=gen_"+proc+"_"+label+".err.$(Cluster).$(Process)\n")
    f.write("queue 1\n")
    f.close()

    cmd = "condor_submit "+subfile
    print cmd
    if submit:
        os.system(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('proc', help="Names of physics model")
    parser.add_argument('--in-file', '-i', dest='infile', help="Full path to input tarball", required=True)
    parser.add_argument('--nevents', '-n', help="Number of events per job", type=int, default=25000)
    parser.add_argument('--njobs', '-j', help="Number of condor jobs", type=int, default=1)
    parser.add_argument('--no-sub', dest='noSub', action='store_true', help='Do not submit jobs')
    parser.add_argument('--proxy', dest="proxy", help="Path to proxy", default='/tmp/x509up_u31156')
    parser.add_argument('--rseed-start', dest='rseedStart', help='Initial value for random seed', 
            type=int, default=500)
    args = parser.parse_args()

    proc = args.proc
    nevents = args.nevents
    njobs = args.njobs
    infile = args.infile
    rseedStart = args.rseedStart

    script_dir = os.path.dirname(os.path.realpath(__file__))
    executable = script_dir+'/runLHEJob.sh'
    out_dir='/hadoop/cms/store/user/'+os.environ['USER']+'/mcProduction/LHE'
    print "Will generate LHE events using tarball",infile

    outdir = out_dir+'/'+proc
    options = [proc, str(nevents), outdir]
    print "Options:",(' '.join(options))
    for j in range(0,njobs):
        rseed = str(rseedStart+j)
        print "Random seed",rseed
        submitCondorJob(proc, executable, options+[rseed], infile, label=rseed, submit=(not args.noSub), proxy=args.proxy)
