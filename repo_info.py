'''    '''
# SCRIPT DEFAULT INFO
# SCRIPT_MAJOR_VERSION = '2.5'
# SCRIPT_RELEASE = 'Midgard'
# SCRIPT_VERSION = 'v2.5.8-master-release'

SCRIPT_INFO = {'script_major_version': '2.5',
               'script_release': 'Midgard',
               'script_version': 'v2.5.8-master-release'}

REPOS_TO_EXCLUDE = ['esgf-installer', 'esgf-publisher-resources', 'esg-publisher', 'esgf-desktop']

ALL_REPO_URLS = [
    'https://github.com/ESGF/esgf-dashboard.git',
    'https://github.com/ESGF/esgf-getcert.git',
    'https://github.com/ESGF/esgf-idp.git',
    'https://github.com/ESGF/esgf-installer.git',
    'https://github.com/ESGF/esgf-node-manager.git',
    'https://github.com/ESGF/esgf-publisher-resources.git',
    'https://github.com/ESGF/esgf-security.git',
    'https://github.com/ESGF/esg-orp.git',
    'https://github.com/ESGF/esg-publisher.git',
    'https://github.com/ESGF/esg-search.git',
    'https://github.com/ESGF/esgf-stats-api.git'
]

REPO_LIST = [
    'esgf-dashboard',
    'esgf-getcert',
    'esgf-idp',
    'esgf-installer',
    'esgf-node-manager',
    'esgf-publisher-resources',
    'esgf-security',
    'esg-orp',
    'esg-publisher',
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
'3: esgf-installer\n'\
'4: esgf-node-manager\n'\
'5: esgf-publisher-resources\n'\
'6: esgf-security\n'\
'7: esg-orp\n'\
'8: esg-publisher\n'\
'9: esg-search\n'\
'10: esgf-stats-api\n'\
"To select a repo, enter the appropriate number.\n"\
"To select multiple repos, seperate each number with a comma.\n"\
"Example: '0, 3, 5'\n"
