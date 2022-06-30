import git
import os, fnmatch
from pathlib import Path
import glob
import re
from git import repo # pip install GitPython
import sys
import ruamel.yaml



currentdirectoy=os.getcwd()
rootfolder = f"{currentdirectoy}/k8s-applications/teams"
#rootfolder=r'c:\windows'
my_update_branch="feat_add_argo_rbac"
filelookuppattern = "/**/_projects/templates/*.yaml"
yamlfilefolder = "_projects/templates"
cookiecutterjsonfile = "./cookiecutterplain.json"
scriptlogfile = "scriptlogfile.log"
actiontoadd=["get","action/apps/Deployment/restart","action/apps/StatefulSet/restart","action/apps/CronJob/resume","action/apps/CronJob/suspend","action/apps/Deployment/ScaleToZero","action/apps/StatefulSet/ScaleToZero"]
developerrolename="developer"

class Role:
    groups = []
    name = ""
    description = ""
    policies = []


print(f"working from directory {rootfolder}")

def updateyamlfiles(file):
    
    with open(file,"r+") as wf:
        new_wf = wf.readlines()
        wf.seek(0)
        for line in new_wf:
            if "# A role which provides read-only access to all applications in the project" not in line:
                wf.write(line)
        wf.truncate()
    wf.close()
       
    with open(file) as oldfile:
        yaml = ruamel.yaml.YAML()
        appproj = yaml.load(oldfile)
    projectname = appproj['metadata']['name']
    #print(f"working with {projectname}")
    #print(appproj)
    if (appproj['kind'] == "AppProject") and (appproj["spec"]["roles"][0]["name"] == "read-only"):
        policies=[]
        for action in actiontoadd:
            policies.append(f"p, proj:{projectname}:{developerrolename}, applications, {action}, {projectname}/*, allow")
       #print(policies)
        role = Role()
        role.name = developerrolename
        role.description = "Developer privileges to project"
        role.groups = appproj["spec"]["roles"][0]["groups"][0]
        groupname = appproj["spec"]["roles"][0]["groups"][0]
       # print(f"group name is {groupname}")
        role.policies = policies
       # print(role.description)
        appproj["spec"]["roles"].yaml_set_start_comment("A role which provides developer access to specific resources in the project", indent =2)
        appproj["spec"].yaml_set_comment_before_after_key("roles",after="A role which provides developer access to specific resources in the project")
        appproj["spec"]["roles"][0]["groups"][0]
        appproj["spec"]["roles"][0]["name"] = developerrolename
        appproj["spec"]["roles"][0]["description"] = "Developer privileges to project"
        appproj["spec"]["roles"][0]["groups"][0] = groupname
        appproj["spec"]["roles"][0]["policies"] = policies
        #yaml.dump(appproj,sys.stdout)
        with open(file,"r+") as newfile:
            new_file = newfile.readlines()
            newfile.seek(0)
            yaml.width = 500
            yaml.dump(appproj,newfile)


#updateyamlfiles("/home/a559871/learngo/py-yaml/k8s-applications/teams/webinfrastructure/_projects/templates/Logstash-F5.yaml")
#updateyamlfiles("resource_demand.yaml")

def getyamlfiles(path,pattern):
    yamlfiles = []
    for file in glob.glob(f"{path}{pattern}", recursive=True):
        #print(f"adding new file {file}")
        yamlfiles.append(file)
    return yamlfiles

allyamlfiles = getyamlfiles(rootfolder,filelookuppattern)

for yamlfile in allyamlfiles:
    print(yamlfile)
    updateyamlfiles(yamlfile)
