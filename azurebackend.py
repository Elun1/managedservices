import requests
from azure.common.credentials import UserPassCredentials

'''
Requires the azure python SDK. Can be a hassle to install, but works with pip3 version 18.0
pip3 install azure
'''

class AzureInfo(object):


    def __init__(self, resource_group, subID, access_token, appservice_name=False):

        self.resource_group = resource_group
        self.subID = subID
        self.access_token = access_token
        if appservice_name == True:
            self.appservice_name = appservice_name
        else:
            self.appservice_name = self.resource_group
        self.get_instance_info()
        self.instance_count = len(self.instances)
        self.get_hostnames()

    def get_instance_info(self):

        self.arraffinity_values = []
        self.instances = {}

        azureURL = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/instances?api-version=2017-04-01'.format(
                   self.subID,
                   self.resource_group,
                   self.appservice_name)

        r = requests.get(azureURL, headers={'Authorization':self.access_token})

        data = r.json()
        data = data['value']

        for x in data:
            self.arraffinity_values.append(x['name'])

        kuduURL = 'https://{}.scm.azurewebsites.net/Env.cshtml'.format(self.appservice_name)

        for arraffinity_value in self.arraffinity_values:
            r = requests.get(kuduURL, headers={'Authorization':self.access_token}, cookies={'ARRAffinity':arraffinity_value})
            data = str(r.content).split('\\r\\n')

            for d in data:
                if 'Machine name' in d:
                    machine_name = d.split(' ')
                    machine_name = machine_name[-1].replace('</li>', '')
            
            self.instances[machine_name] = arraffinity_value

    def get_hostnames(self):

        azureURL = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/sites/{}/hostNameBindings?api-version=2018-02-01'.format(
                   self.subID,
                   self.resource_group,
                   self.appservice_name)

        r = requests.get(azureURL, headers={'Authorization':self.access_token})

        data = r.json()
        self.all_hostnames = []
        self.custom_hostnames = []

        for x in data['value']:
            tmp_list = x['id'].split('/')
            self.all_hostnames.append(tmp_list[-1])

        for hostname in self.all_hostnames:
            if 'azurewebsites' not in hostname and 'episerver' not in hostname:
                self.custom_hostnames.append(hostname)

def get_auth_token(username, passwd):

    '''
        returns access_token as a string, can be used as value for Authorization header
    '''
    credentials = UserPassCredentials(
        username,
        passwd
    )

    return credentials.token['token_type'] + ' ' + credentials.token['access_token']

def test_instance_resptimes(hostname, instance_info, timeout=30):

    for name, arraffinity_value in instance_info.items():
        cookie = {'ARRAffinity':arraffinity_value}
        r = requests.get('http://' + hostname, cookies=cookie, timeout=timeout)
        time = r.elapsed.total_seconds()
        print('\tinstance ' + name + 
              ' responded in ' + str(time) + 
              ' seconds with status code ' + str(r.status_code))