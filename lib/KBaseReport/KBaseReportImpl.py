#BEGIN_HEADER



import uuid
from biokbase.workspace.client import Workspace

#END_HEADER


class KBaseReport:
    '''
    Module Name:
    KBaseReport

    Module Description:
    Module for a simple WS data object report type.
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.1.0"
    GIT_URL = "git@github.com:msneddon/KBaseReport"
    GIT_COMMIT_HASH = "1568720b8e6a3cc5ab136cfca930cc6083acc215"
    
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.workspaceURL = config['workspace-url']
        #END_CONSTRUCTOR
        pass
    

    def create(self, ctx, params):
        # ctx is the context object
        # return variables are: info
        #BEGIN create

        print('Creating KBase Report.')

        # check that the basic parameters are set
        if 'report' not in params:
            raise ValueError('Field "report" must be defined to save a report')
        if 'workspace_name' not in params:
            raise ValueError('Field "workspace_name" must be defined to save a report')

        # setup proper provenance for the report
        provenance = [{}]
        if 'provenance' in ctx:
            provenance = ctx['provenance']

        # generate a random report name
        reportName = 'report_'+str(uuid.uuid4())
        if 'prefix' in params:
            reportName = params['prefix'] + reportName


        print('Report Name' + reportName)

        # let any workspace errors just percolate up for now
        ws = Workspace(self.workspaceURL, token=ctx['token'])
        report_info = ws.save_objects({
                'workspace':params['workspace_name'],
                'objects':[
                    {
                        'type':'KBaseReport.Report',
                        'data':params['report'],
                        'name':reportName,
                        'meta':{},
                        'hidden':1,
                        'provenance':provenance
                    }
                ]
            })[0]

        info = {
            'ref'  : str(report_info[6]) + '/' + str(report_info[0]) + '/' + str(report_info[4]),
            'name' : report_info[1]
        }

        #END create

        # At some point might do deeper type checking...
        if not isinstance(info, dict):
            raise ValueError('Method create return value ' +
                             'info is not type dict as required.')
        # return the results
        return [info]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
