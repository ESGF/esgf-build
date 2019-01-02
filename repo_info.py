'''    '''
# SCRIPT DEFAULT INFO
# SCRIPT_MAJOR_VERSION = '2.5'
# SCRIPT_RELEASE = 'Midgard'
# SCRIPT_VERSION = 'v2.5.8-master-release'

SCRIPT_INFO = {'script_major_version': '2.5',
               'script_release': 'Helheim',
               'script_version': 'v2.5.13-master-release'}

REPOS_TO_EXCLUDE = ['esgf-installer', 'esgf-publisher-resources', 'esg-publisher', 'esgf-desktop']

ALL_REPO_URLS = {"esgf-dashboard": 'https://github.com/ESGF/esgf-dashboard.git',
                 "esgf-getcert": 'https://github.com/ESGF/esgf-getcert.git',
                 "esgf-idp": 'https://github.com/ESGF/esgf-idp.git',
                 "esgf-node-manager": 'https://github.com/ESGF/esgf-node-manager.git',
                 "esgf-publisher-resources": 'https://github.com/ESGF/esgf-publisher-resources.git',
                 "esgf-security": 'https://github.com/ESGF/esgf-security.git',
                 "esg-orp": 'https://github.com/ESGF/esg-orp.git',
                 "esg-publisher": 'https://github.com/ESGF/esg-publisher.git',
                 "esg-search": 'https://github.com/ESGF/esg-search.git',
                 "esgf-stats-api": 'https://github.com/ESGF/esgf-stats-api.git'
                 }


REPO_LIST = [
    'esgf-dashboard',
    'esgf-getcert',
    'esgf-idp',
    'esgf-node-manager',
    'esgf-security',
    'esg-orp',
    'esg-search',
    'esgf-stats-api'
]
########################################################################
#last minute solution for "esgf-installer" does not exist problem
#this list creates all local mirrors and tarballs, but does not build all
CREATE_DIRECTORY_LIST = [
    'esgf-dashboard',
    'esgf-getcert',
    'esgf-idp',
    'esgf-installer',
    'esgf-node-manager',
    'esgf-security',
    'esg-orp',
    'esg-search',
    'esgf-stats-api'
]
#########################################################################
REPO_MENU = 'Repository menu:\n'\
'----------------------------------------\n'\
'0: esgf-dashboard\n'\
'1: esgf-getcert\n'\
'2: esgf-idp\n'\
'3: esgf-node-manager\n'\
'4: esgf-security\n'\
'5: esg-orp\n'\
'6: esg-search\n'\
'7: esgf-stats-api\n'\
"To select a repo, enter the appropriate number.\n"\
"To select multiple repos, seperate each number with a comma.\n"\
"Example: '0, 3, 5'\n"
