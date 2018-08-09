import sys
from getpass import getpass
from azurebackend import *

def main():

    subID = get_input('Subscription ID: ')
    resource_group = get_input('Resource group name: ')
    appservice_name = input('App Service name (empty if it\'s the same as resource group): ')
    if appservice_name == '':
        appservice_name = resource_group
    username = get_input('Username: ')

    token = get_auth_token(username, getpass())
    prod_app = AzureInfo(resource_group, subID, token, appservice_name)

    print('\n\nInformation for app service ' + prod_app.appservice_name + '\n')
    print('Running instance count: ' + str(prod_app.instance_count))
    for name, arr in prod_app.instances.items():
        print('\t' + name + ' has ARRAffinity ' + arr)

    print('\nAll hostnames:')
    for hostname in prod_app.all_hostnames:
        print('\t' + hostname)

    print('\nCustom hostnames:')
    for hostname in prod_app.custom_hostnames:
        print('\t' + hostname)

    print('\nTesting all instances on custom URL ' + prod_app.custom_hostnames[0])
    test_instance_resptimes(prod_app.custom_hostnames[0], prod_app.instances)

def get_input(prompt):

    result = False
    while result == False:
        result = input(prompt)
        if not result:
            result = False
            print('\n Error: Empty input')

    return result

if __name__ == '__main__':
    main()