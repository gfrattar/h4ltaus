import ROOT
import sys

class Analysis():
  
  t = []
  infile = []
  inputFileName = ''
  outputFileName = 'out.root'
  channels = ['4tau','2tau2e']
  debug = True
  maxEvents = 1e6
  histo = {}
  directory = {}
  branch = {}
  sumOfWeights = {}
  sumOfWeights['nominal'] = 0.
  sumOfWeights['raw'] = 0.
  weight = 0.  
  
  preselectedObjects = {}
  preselectedObjects['electrons'] = []
  preselectedObjects['muons'] = []
  preselectedObjects['taus'] = []  #hadronic taus: jets labelled 15
  preselectedObjects['bjets'] = [] #jets labelled 5
  preselectedObjects['2lep_cand'] = []
  preselectedObjects['4lep_cand'] = []
  
  #--------------------------#
  # Normalization parameters #
  #--------------------------#
  luminosity = 160e3 #160/pb
  xsec = 52.230 #ggF->H cross-section in pb
  BR= 2.745E-04 #BR H to 4 leptons --> TODO: check value
  filterEfficiencyTaus = 5.441420E-01 # Filter efficiency from MC generation
  
  #===================================================================================================#
  #Core functions
  #===================================================================================================#
  
  def Initialize(self):

    self.infile = ROOT.TFile.Open(self.inputFileName)
    if(not ROOT.xAOD.Init().isSuccess()): print("Failed xAOD.Init()")
    #--Technical part to open the file and treat it as it was an ntuple--# 
    treeName = "CollectionTree" # default when making transient tree anyway
    # Make the "transient tree":
    self.t = ROOT.xAOD.MakeTransientTree( self.infile, treeName, ROOT.xAOD.TEvent.kClassAccess)
    # Print some information:
    if self.debug: print( "Number of input events: %s" % self.t.GetEntries() )

    #Prepare the output file
    self.outputfile = ROOT.TFile('outputs/'+self.outputFileName,'RECREATE')
    self.CreateHistograms()

    
  #****************************************#

  def Process(self):
    #Here we have the event loop
    for entry in range(0, self.t.GetEntries()):
      if entry > self.maxEvents: break
      self.t.GetEntry( entry )
      self.AssignBranches()
      self.FetchWeights()
      
      # print("Event weight = {}".format(self.weight))
      
      self.PreselectObjects()
      
      #*************************#
      # Particle level analysis #
      #*************************#
      self.ParticleLevelAnalysis()
      
      #*********************#
      # True level analysis #
      #*********************#
      self.TrueLevelAnalysis()
    
  #****************************************# 

  def Finalize(self):
    print("Running finalize")
    self.FillWeightsHistos()
    self.outputfile.Write()


  #===================================================================================================#
  #Functions  
  #===================================================================================================#

  def FillWeightsHistos(self):
    self.histo['Metadata'].SetBinContent(1,self.sumOfWeights['raw'])
    self.histo['Metadata'].SetBinError(1,0)
    self.histo['Metadata'].SetBinContent(2,self.sumOfWeights['nominal'])
    self.histo['Metadata'].SetBinError(2,0)
    

  def TrueLevelAnalysis(self):
    print("Welcome to the TrueLevelAnalysis")
    #******#
    # TODO #
    #******#
    #Implement the true level analysis checking the barcode / parents of particles
    #Remember that this can be done only for the signal for now. 
    #For the background we can check if this can be done for non Sherpa samples.


  def ParticleLevelAnalysis(self):
    print("Welcome to the ParticleLevelAnalysis")
    #******#
    # TODO #
    #******#
    #self.PerformOverlapRemoval()
    # --> remove all leptons within 0.3 of a jet
    # --> require all leptons to have delta R > 0.1
  
    # Define a function that given a list of preselected objects prints out them and their properties

    # Complete the code development
    # self.CreateDileptonCandidates()
    # --> create all possible candidates excluding using the same lepton twice
    # --> include selections on the sign (for el and muons) via check of the abs pdgid
    # --> not allow invariant mass below 5 GeV

    # self.CreateFourLeptonCandidates()
    # --> create all possible candidates excluding using the same dilepton twice

    # self.OrderFourLeptonCandidates()
    # --> set the dilepton closer to the Z peak as the Z, and the other as Z* -- TBD what to do with the 2tau2l final states

    # self.SelectHiggsCandidates()
    # --> select the higgs candidate based on what we decide as priority on the objects
    # --> apply lepton pT selections and fill selected objects containers
    # Decision: to take decision what to do if we have multiple higgs candidates but the first one does not pass the selections --> Shubham check of reco level code?

    #Example of filling, to be adapted
    self.FillKinematicPlotsPL('4tau')
    
  
  def FillKinematicPlotsPL(self,channel):
    self.histo[channel+'_n_electrons'].Fill(1,self.weight)
      
      
  def PreselectObjects(self):
    #Iterate over leptons and fill preselected objects "containers"
    self.preselectedObjects['electrons'] = [tp for tp in self.branch['Electrons'] if (tp.status() == 1 and tp.pt() > 5000. and abs(tp.eta()) < 2.5)]
    self.preselectedObjects['muons'] = [tp for tp in self.branch['Muons'] if (tp.status() == 1 and tp.pt() > 5000. and abs(tp.eta()) < 2.5)]
    self.preselectedObjects['taus'] = [tp for tp in self.branch['Jets'] if (tp.pt() > 20000. and abs(tp.eta()) < 2.5) and tp.getAttribute['int']('ConeTruthLabelID')]
        
  def CreateHistograms(self):

    #Histograms to take care of sample normalisation when plotting the outputs
    self.histo['Metadata'] = ROOT.TH1F('Metadata',';;;Sum of weights',2,0,2)
    self.histo['Metadata'].GetXaxis().SetBinLabel(1,'Raw')
    self.histo['Metadata'].GetXaxis().SetBinLabel(2,'Nominal')
        
    for ch in self.channels:
      self.directory[ch] = self.outputfile.mkdir('histos_'+ch)
      self.directory[ch].cd()
      
      #---- Here define the histograms we fill ----#
      self.histo[ch+'_n_electrons'] = ROOT.TH1F('n_electrons',';n. electrons all;events',10,0,10)
      self.histo[ch+'_n_presel_electrons'] = ROOT.TH1F('n_presel_electrons',';n. preselected electrons;events',10,0,10)
      self.histo[ch+'_n_sel_electrons'] = ROOT.TH1F('n_sel_electrons',';n. selected electrons;events',10,0,10)
      #*********************************#
      # TODO : add the other histograms #
      #*********************************#

      #--------------------------------------------#

      #Reset the path where the histos are created
      self.outputfile.cd("../")


  def AssignBranches(self):    
    self.branch['Electrons'] = self.t.TruthElectrons
    self.branch['Muons']     = self.t.TruthMuons
    self.branch['Photons']   = self.t.TruthPhotons
    self.branch['Taus']      = self.t.TruthTaus
    self.branch['Jets']      = self.t.AntiKt4TruthDressedWZJets
    #Add extra branches if needed. To see the available branches check one input file
    #and do CollectionTree->Print()
    
    
  def FetchWeights(self):
    self.weight = self.t.EventInfo.mcEventWeights()[0]
    self.sumOfWeights['nominal'] += self.weight #sum of nominal event weights to normalise the events
    self.sumOfWeights['raw'] += 1      
    self.weight *= self.xsec * self.BR * self.filterEfficiencyTaus * self.luminosity
          
#=====================================================================================================#
#Main function  
#=====================================================================================================#
  
if __name__ == "__main__":
   
    '''
    To add:
      - opzione runnnare in parallelo su più segnali
    '''

    myanalysis = Analysis()
    myanalysis.maxEvents = 10 #To add function to pass this from command line with --nevents ; use python argparser
    myanalysis.inputFileName  = sys.argv[1] #To modify with the parser and using --input or -i
    myanalysis.outputFileName = sys.argv[2] #same of above but doing with --output or -o

    myanalysis.Initialize()
    
    myanalysis.Process()
    
    myanalysis.Finalize()
