import pyawr.mwoffice as mwo
from pyawr_utils import schematic_utils, vss_utils, graph_utils, common_utils, misc_utils
import time as tm
import numpy as np
#
_Schematics = schematic_utils._Schematics
_SystemDiagrams = vss_utils._SystemDiagrams
_Graphs = graph_utils._Graphs
_DataFiles = misc_utils._DataFiles
_Optimization = misc_utils._Optimization
_GlobalDefinitions = misc_utils._GlobalDefinitions
_CommonTools = common_utils._CommonTools
#
def establish_link(version_str: str ='', clsid_str:str ='') -> object:
    '''
    returns object variable object that is the AWRDE instance
    
    Parameters
    ----------
    version_str: string, optional
            Revision number of AWRDE. Must be in form Major Revision.Minor Revision. For
            instance, AWRDE version 16.02 would be a version_str value of 16.0
            Default is empty string
    clsid_str: string, optional
           Unique identifier for AWRDE instance. This number can be found using VBA script command
           Debug.Print MWOffice.InstanceCLSID
           Only include the CLSID number in this format:
                5BF3163E-6734-4FB4-891E-FD9E3D4A2CFA
           Do not inlcude brackets: {}
           Default is empty string
    Returns
    -------
    awrde: object variable
    
    Note
    ----
    If only one instance of AWRDE is currently opened then CLSID is not required. CLSID is only required
    to link to a specific opened AWRDE instance
    
    If only one version of AWRDE is currently installed, then version_str is not required
    
    See Also
    --------
    https://kb.awr.com/display/awrscripts/AWR+Scripting+in+Python%3A+Using+the+AWRDE+API+Scripting+Guide
    '''
    
    if not isinstance(version_str, str):
        raise TypeError('version_str must be a string type')
    if not isinstance(clsid_str, str):
        raise TypeError('clsid_str must be a string type')
    #end if
    #
    if version_str == '' and clsid_str == '':
        try:
            awrde = mwo.CMWOffice()
        except:
            raise RuntimeError('Link between Python and AWRDE could not be established')
        #end try
    elif clsid_str != '':
        try:
            awrde = mwo.CMWOffice(clsid='{'+clsid_str+'}')
        except:
            print('CLSID Number: ' + clsid_str)
            raise RuntimeError('Link between Python and AWRDE using CSLID could not be established')
        #end try
    elif version_str != '':
        try:
            awrde = mwo.CMWOffice(version=version_str)
        except:
            print('Version_str: ' + version_str)
            raise RuntimeError('Link between Python and AWRDE using Version could not be established')
        #end try
    #end if
    return awrde
    #
class Project(_Graphs, _Schematics, _SystemDiagrams, _DataFiles, _Optimization, _GlobalDefinitions,
              _CommonTools):
    ''' 
    Highest level class in pyawr_utils. User interface to all classes,methods, properties,
    etc. are through the Project class
    
    Parameters
    ----------
    awrde: object variable 
         this variable is returned from awr_utils.establish_link()
    '''
    #
    def __init__(self, awrde, bypass_initalization=False):#-----------------------------------------------------------------------
        if not bypass_initalization:
            _Graphs.__init__(self, awrde)
            _Schematics.__init__(self, awrde.Project)
            _SystemDiagrams.__init__(self, awrde)
            _DataFiles.__init__(self, awrde)
            _Optimization.__init__(self, awrde)
            _GlobalDefinitions.__init__(self, awrde)            
        #end if
        _CommonTools.__init__(self, awrde)
        self._options_blacklist()
        self.awrde = awrde
        #
    def initialize_on_demand(self, which_initialization='all'):#----------------------------------------
        '''
        Inialize schematics, system diagrams, global defs, data files, graphs, optimization
        
        Parameters
        ----------
        which_initialization: string
                      'all'
                      'schematics'
                      'system diagrams'
                      'graphs'
                      'data files'
                      'global definitions'
                      'optimization'
        '''
        if not isinstance(which_initialization, str):
            raise TypeError('which_initialization must be string type')
        #end if
        Initialization_dict = {'schematics':False, 'system diagrams':False, 'graphs':False,
                               'global definitions':False, 'optimization':False, 'data files':False}
        #
        if which_initialization == 'all':
            for key_name in Initialization_dict.keys():
                Initialization_dict[key_name] = True
            #end for
        elif which_initialization == 'schematics':
            Initialization_dict['schematics'] = True
        elif which_initialization == 'system diagrams':
            Initialization_dict['system diagrams'] = True
        elif which_initialization == 'graphs':
            Initialization_dict['graphs'] = True
        elif which_initialization == 'global definitions':
            Initialization_dict['global definitions'] = True
        elif which_initialization == 'optimization':
            Initialization_dict['optimization'] = True
        elif which_initialization == 'data files':
            Initialization_dict['data files'] = True        
        else:
            raise RuntimeError('Invalid which_initialization: '+which_initialization)
        #end if
        #
        try:
            for key_name, do_it in Initialization_dict.items():
                if key_name=='schematics' and do_it:
                    _Schematics.__init__(self, self.awrde.Project)
                elif key_name=='system diagrams' and do_it:
                    _SystemDiagrams.__init__(self, self.awrde)
                elif key_name=='graphs' and do_it:
                    _Graphs.__init__(self, self.awrde)
                elif key_name=='global definitions' and do_it:
                    _GlobalDefinitions.__init__(self, self.awrde)
                elif key_name=='optimization' and do_it:
                    _Optimization.__init__(self, self.awrde)
                elif key_name=='data files' and do_it:
                    _DataFiles.__init__(self, self.awrde)            
                #end if
            #end for
        except:
            raise RuntimeError('Initialize on demand failed. Possible cause is that a project is not opened')
        #end try
    #
    #----------------------------Project section------------------------------------------
    #
    def save_project(self):#---------------------------------------------------------
        ''' Equivalent to File > Save '''
        try:
            self.awrde.Project.Save2(True)  #Nop propmt
        except:
            pass #project is already saved
        #end try
        #
    def save_project_as(self, Dir_n_File: str):#------------------------------------------
        '''Save Project As'''
        if not isinstance(Dir_n_File, str):
            raise TypeError('Dir_n_File must be string type')
        #end if
        #
        try:
            self.awrde.Project.SaveAs(Dir_n_File)
        except:
            raise RuntimeError('Project Save As failed')
        #end try
        #
    def save_project_as_version(self, Dir_n_File: str, version_num: int):#--------------------------------
        ''' SAve As Version'''
        if not isinstance(Dir_n_File, str):
            raise TypeError('Dir_n_File must be string type')
        #end if        
        if not isinstance(version_num, int):
            raise TypeError('version_num must be integer type')
        #end if
        try:
            self.awrde.Project.SaveAsVersion(Dir_n_File, 3, version_num)
        except:
            raise RuntimeError('Project Save As Version failed')
        #end try        
        #
    @property
    def project_name(self) -> str:#-------------------------------------------------------
        ''' returns name of currently opened project'''
        return self.awrde.Project.Name
        #
    @property
    def project_path(self) -> str:#------------------------------------------------------
        raw_path = self.awrde.Project.Path
        path = raw_path.replace('\\','/')
        return path   
        #
    def open_project(self, Dir_n_File: str):#---------------------------------------------
        '''open a project'''
        if not isinstance(Dir_n_File, str):
            raise TypeError('Dir_n_File must be string type')
        #end if
        #
        try:
            self.awrde.Project.Application.Open(Dir_n_File)
        except:
            raise RuntimeError('Open project failed. Possible cause is that a project is not opened')
        #end try
        #
    def close_project(self):#---------------------------------------------------------
        ''' close the project'''
        try:
            self.awrde.Project.Close(False, '') #Do not save change. File name is blank
        except:
            raise RuntimeError('Close project failed. Possible cause is that a project is not opened')
        #end try
        #        
    @property
    def project_frequencies(self) -> np.ndarray:#------------------------------------------------
        '''returns project frequencies in Hz as an array'''
        project_freq_list = list()
        for freq in self.awrde.Project.Frequencies:
            project_freq_list.append(freq.Value)
        #end for
        project_freq_ay = np.array(project_freq_list)        
        return project_freq_ay
        #
    def set_project_frequencies(self, project_freq_ay: np.ndarray, units_str: str = 'GHz'):#-----------------------
        '''sets project frequencies'''
        #Cannot be made as a setter property due to multiple pass parameters
        units_dict = {'Hz':1, 'kHz':1e3, 'MHz':1e6, 'GHz':1e9}
        try:
            freq_multiplier = units_dict[units_str]
        except:
            raise RuntimeError('Incorrect units: ' + units_str)
        #end try
        project_freq_ay *= freq_multiplier
        self.awrde.Project.Frequencies.Clear()  #Remove all existing frequencies
        try:
            self.awrde.Project.Frequencies.AddMultiple(project_freq_ay)  #Add new frequency arrray
        except:
            raise RuntimeError('Error in setting project frequencies')
        #end try
        #
    @property
    def environment_options_dict(self) -> dict:#----------------------------------------------
        '''returns dictionary of options found in Main Menu > Options > Environment Options'''
        env_options = self.awrde.Options
        env_options_dict = {}
        for opt in env_options:
            if opt.Name not in self._env_options_blacklist:
                env_options_dict[opt.Name] = opt.Value
            #end if
        #end for
        return env_options_dict
        #
    def set_environment_options_dict(self, environment_options_dict: dict):#--------------------------
        '''set options found in Main Menu > Options > Environment Options'''
        for opt_name, opt_value in environment_options_dict.items():
            try:
                self.awrde.Options(opt_name).Value = opt_value
            except:
                raise RuntimeError('setting environment options failed: ' + opt_name + ' , ' + str(opt_value))
            #end try
        #end for
        #
    @property
    def project_options_dict(self) -> dict:#---------------------------------------------------------
        '''returns dictionary of options found in Main Menu > Options > Project Options & Layout Options'''
        proj_options = self.awrde.Project.Options
        proj_options_dict = {}
        for opt in proj_options:
            if opt.Name not in self._project_options_blacklist:
                proj_options_dict[opt.Name] = opt.Value
            #end if
        #end for
        return proj_options_dict
        #
    def set_project_options_dict(self, project_options_dict: dict):#--------------------------
        '''set options found in Main Menu > Options > Project Options & Layout Options'''
        for opt_name, opt_value in project_options_dict.items():
            try:
                self.awrde.Project.Options(opt_name).Value = opt_value
            except:
                raise RuntimeError('setting environment options failed: ' + opt_name + ' , ' + str(opt_value))
            #end try
        #end for
        #
    @property
    def show_files_directories_dict(self) -> dict:#-------------------------------------------
        '''
        returns dictionary of project files and directories
        
        Returns
        -------
        show_files_dirs_dict: dictionary
                                    keys are the Names of the file or directory
                                    values are the file path or directory path
        '''
        show_files_dirs_dict = {}
        NumFiles = self.awrde.Project.Application.Files.Count
        NumDirectories = self.awrde.Project.Application.Directories.Count
        #
        for file_idx in range(1, NumFiles+1):
            Name = self.awrde.Project.Application.Files.Item(file_idx).Name
            Dir_n_File = self.awrde.Project.Application.Files.Item(file_idx).ValueAsString
            show_files_dirs_dict[Name] = Dir_n_File
        #end for
        #
        for dir_idx in range(1, NumDirectories+1):
            Name = self.awrde.Project.Application.Directories.Item(dir_idx).Name
            DirPath = self.awrde.Project.Application.Directories.Item(dir_idx).ValueAsString
            show_files_dirs_dict[Name] = DirPath
        #end for
        return show_files_dirs_dict
        #        
    def _options_blacklist(self):#-------------------------------------------------------------------
        ''' lists of option names that cause errors'''
        self._project_options_blacklist = ['FaceInsetOptions']
        self._env_options_blacklist = ['MouseCommandEntryMode']
        #
    #
    #-----------------------------Simulate/Analyze section----------------------------------------
    #
    def simulate_analyze(self, ping_interval = 1, max_time = 120) -> bool:
        '''
        Equivalent to Simulte > Analyze
    
        Parameters
        ----------
        awrde: object
            The AWRDE object returned from EstablishLink()
    
        ping_interval: int, optional
            Wait time in seconds before getting simulation status
            Defaul is 1 second
    
        max_time: int, optional
            Maximum simulation time in seconds
            Default is 120 seconds
    
        Returns
        -------
        measurement_done: bool
            True if simulation has completed
    
        '''
        #
        if not isinstance(ping_interval, int) and not isinstance(ping_interval, float):
            raise TypeError('ping_interval must be type int or float')
        if not isinstance(max_time, int) and not isinstance(max_time, float):
            raise TypeError('max_time must be type int or float')
        # end if
        #    
        measurement_done = False
        elapsed_time = 0
        start_time = tm.time()
        self.awrde.Project.Simulator.Analyze()
        while not measurement_done or elapsed_time>max_time:
            sim_status = self.awrde.Project.Simulator.AnalyzeState
            if sim_status == 3:
                measurement_done = True
            #end if
            tm.sleep(ping_interval)
            elapsed_time = tm.time() - start_time
        #end while
        return measurement_done
        #
    def simulate_run_system_simulator(self, ping_interval = 1, max_time = 120) -> bool:
        '''
        Equivalent to Simulate > Run/Stop System Simulators
        
        Parameters
        ----------
        awrde: object
            The AWRDE object returned from EstablishLink()
            
        ping_interval: int, optional
            Wait time in seconds before getting simulation status
            Defaul is 1 second
            
        max_time: int, optional
            Maximum simulation time in seconds
            Default is 120 seconds
            
        Returns
        -------
        measurement_done: bool
            True if simulation has completed
        
        '''    
        #
        if not isinstance(ping_interval, int) and not isinstance(ping_interval, float):
            raise TypeError('ping_interval must be type int or float')
        if not isinstance(max_time, int) and not isinstance(max_time, float):
            raise TypeError('max_time must be type int or float')
        #end if
        #
        measurement_done = False
        elapsed_time = 0
        start_time = tm.time()
        self.awrde.Project.Simulator.RunStop()
        while (not measurement_done) and (elapsed_time < max_time):
            sim_status = self.awrde.Project.Simulator.state
            if sim_status == 0:
                measurement_done = True
            #end if
            tm.sleep(ping_interval)
            elapsed_time = tm.time() - start_time
        #end while
        return measurement_done
        #
    def stop_system_simulator(self):#---------------------------------------------------
        '''Stops a running system simulation'''
        sim_status = self.awrde.Project.Simulator.state
        if sim_status != 0:  #Stop simulator if still running after maximum time
            self.awrde.Project.Simulator.stop()
        #end if    
        #

    
    