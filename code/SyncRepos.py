"""
Syncs repos between two TFS/VSTS/AzureDevOps repos
"""
import configparser
import os
from multiprocessing import Pool
from ProjectsTeamsUsers import ProjectsTeamsUsersWorker
from Repositories import RepositoriesWorker
from VSTSInfo import VstsInfo

class RepoSync(object):
    """
    RepoSync helps get a list of Repos to later sync
    """

    git_root_path = ""
    save_scripts_path = ""
    server_no_ip= ""
    server_ip = ""

    def __init__(self, git_root_path, save_scripts_path, server_no_ip, server_ip):
        """
        :param git_root_path:  where to save all the git repos locally
        :param save_scripts_path: in some cases powershell scripts wont run in the same place as where the repos are saved (citrix mounted drives)
        :param server_no_ip: server name/url/ip of the server without a public ip address
        :param server_ip: server with public ip address
        """
        self.git_root_path = git_root_path
        self.save_scripts_path = save_scripts_path
        self.server_no_ip = server_no_ip
        self.server_ip = server_ip

    def no_ip_remote_name(self):
        """
        returns the git remote name for the no ip server
        """
        return "no_ip_remote"

    def ip_remote_name(self):
        """
        returns the git remote name for the server with a public ip address
        """
        return "ip_remote"

    def set_repo_store(self, project_info, store):
        """
        Gets the url for a git clone
        """
        url = REPO_WORKER.build_url(project_info.get("id"))
        repo_data = VSTS.make_request(url)
        for repo in repo_data["value"]:
            repo_info = {}
            repo_info["web_url"] = repo.get("url")
            repo_info["name"] = repo.get("name")
            repo_info["id"] = repo.get("id")
            repo_info["remoteUrl"] = repo.get("remoteUrl")
            store.append(repo_info)

    def save_cmd_list(self, cmds, filename):
        """
        saves a list to a file
        """
        with open(filename, 'w') as file:
            for item in cmds:
                file.write("%s\n" % item)


    def swap_fqdn(self, repo_list, old_fqdn, new_fqdn):
        """
        swaps out the fqdn's
        """
        changed = []
        for url in repo_list:
            changed.append(url.replace(old_fqdn, new_fqdn))
        return changed

    def make_clone_script(self, repo_list):
        """
        Makes a clone script to run in a batch file
        """
        clone = []
        for repo in repo_list:
            repo_name = repo.get("name")
            url = repo.get("remoteUrl")
            where_to_clone = os.path.join(self.git_root_path, repo_name)
            cmd = 'git clone {0} \"{1}\"'.format(url, where_to_clone)
            clone.append(cmd)
        return clone

    def get_local_git_repos(self, git_root):
        """
        Crawls a folder, gets the list of folder names
        The folder names should be the same as the repo names
        """
        #repos = [x[0] for x in os.walk(git_root)]
        repos = os.listdir(git_root)
        return repos

    def get_repo_name_from_url(self, url):
        """
        given a git clone url, get the name of the repo
        """
        full = len(url)
        idx = url.find("_git/") + 5
        name = url[idx:full]
        return name

    def get_missing_local_repos(self, local_folders, repos):
        """
        Compares the list of repo names in AzureDevOps to local git folders and returns the difference or missing ones
        :param array local_folders: The list of folders on the computer this script is run from
        :param array repos: List of git repositories from AzureDevOps api call
        :return: array of missing repository information
        """
        missing_repos = []
        for repo in repos:
            repo_name = repo.get("name")
            if repo_name not in local_folders:
                missing_repos.append(repo)

        return missing_repos

    def build_remote_cmd(self, repo_name, remote_name, remote_url):
        """
        creates a git set remote command for the repo from a parent folder suitable for a script
        """
        #cmd = "git --work-tree={0} --git-dir={0}/.git  remote add {2} {1}".format(repo_name, remote_url, remote_name)
        git_full_project_path = os.path.join(self.git_root_path, repo_name)
        cmd = 'git --work-tree=\"{0}\" --git-dir=\"{0}\.git\"  remote add {2} {1}'.format(git_full_project_path, remote_url, remote_name)
        return cmd

    def generate_remotes(self, no_ip_store):
        """
        git --work-tree=repo_name --git-dir=repo_name/.git
            remote add noip https://noip.visualstudio.com/foo/_git/repo_name
        """
        results = []
        for noips in no_ip_store:
            repo_name = noips.get("name")
            repo_url = noips.get("remoteUrl")
            no_ip_cmd = self.build_remote_cmd(repo_name, self.no_ip_remote_name(), repo_url)
            results.append(no_ip_cmd)
            
            url_ip = repo_url.replace(self.server_no_ip, self.server_ip)
            ip_cmd = self.build_remote_cmd(repo_name, self.ip_remote_name(), url_ip)
            results.append(ip_cmd)
        return results

    def get_fetch_cmd(self, repo_name, remote_name):
        """
        fetches from the public ip address repo
        git --work-tree=repo_name --git-dir=repo_name/.git
            fetch  https://noip.visualstudio.com/foo/_git/repo_name
        """

        git_full_project_path = os.path.join(self.git_root_path, repo_name)
        fetch = 'git --work-tree=\"{0}\" --git-dir=\"{0}\.git\" fetch --tags --force {1}'.format(git_full_project_path, remote_name)
        return fetch

    def get_push_cmd(self, repo_name, remote_name):
        """
        creates a git push command suitable from running form a big batch file
        """
        pull = "git --work-tree={0} --git-dir={0}\.git push --all {1} ".format(repo_name, remote_name)
        return pull

if __name__ == '__main__':
    print("starting Repo Sync")

    CONFIG = configparser.ConfigParser()
    CONFIG.read_file(open('default.cfg'))

    IS_TRUE = ['True', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

    RUN_MULTITHREADED = CONFIG['RepoSync']['RunMultiThreaded'] in IS_TRUE
    SERVER_NO_IP = CONFIG['RepoSync']['ServerNoIp'] 
    SERVER_IP = CONFIG['RepoSync']['ServerIp']
    GIT_ROOT_FOLDER_PATH = CONFIG['RepoSync']['GitRootFolderPath']
    SAVE_SCRIPTS_FOLDER = CONFIG['RepoSync']['SaveScriptsFolderPath']
    IGNORE_VSTS_CACHE = CONFIG['RepoSync']["IgnoreVstsCache"] in IS_TRUE

    #for this script we always want to ignore the cache
    VSTS = VstsInfo(None, None, ignore_cache=IGNORE_VSTS_CACHE )

    PTU_WORKER = ProjectsTeamsUsersWorker(VSTS.get_request_settings(), VSTS.project_whitelist, VSTS)
    PROJECTS_URL = PTU_WORKER.get_vsts_projects_url()
    RAW = PTU_WORKER.vsts.make_request(PROJECTS_URL)
    PROJECTS = RAW["value"]

    REPO_WORKER = RepositoriesWorker(VSTS.get_request_settings(), VSTS)

    REPO_SYNC = RepoSync(GIT_ROOT_FOLDER_PATH, SAVE_SCRIPTS_FOLDER, SERVER_NO_IP, SERVER_IP)
    LOCAL_REPOS = REPO_SYNC.get_local_git_repos(GIT_ROOT_FOLDER_PATH)

    REPO_NOIP_STORE = []

    if RUN_MULTITHREADED:
        with Pool(5) as p:
            p.map(REPO_SYNC.set_repo_store, PROJECTS, REPO_NOIP_STORE)
    else:
        for PROJ in PROJECTS:
            REPO_SYNC.set_repo_store(PROJ, REPO_NOIP_STORE)

    #generate bat file to clome missing repos
    LOCAL_MISSING = REPO_SYNC.get_missing_local_repos(LOCAL_REPOS, REPO_NOIP_STORE)
    CLONE_MISSING = REPO_SYNC.make_clone_script(REPO_NOIP_STORE)

    CLONE_PATH = os.path.join(SAVE_SCRIPTS_FOLDER, "git_clone_missing.ps1")
    REPO_SYNC.save_cmd_list(CLONE_MISSING, CLONE_PATH)

    #set both remotes
    REMOTES_PATH = os.path.join(SAVE_SCRIPTS_FOLDER, "git_set_remotes.ps1")
    SET_REMOTES = REPO_SYNC.generate_remotes(REPO_NOIP_STORE)
    REPO_SYNC.save_cmd_list(SET_REMOTES, REMOTES_PATH)

    #fetch from SERVER_IP AND PUSH TO NO_IP, including tags
    #may need tweaking if no_ip_server updates any code
    FETCH_PUSH_CMDS = []
    for REPO_INFO in REPO_NOIP_STORE:
        REPO_NAME = REPO_INFO.get("name")

        fetch_has_ip = REPO_SYNC.get_fetch_cmd(REPO_NAME, REPO_SYNC.ip_remote_name())
        FETCH_PUSH_CMDS.append(fetch_has_ip)

        push_no_ip = REPO_SYNC.get_push_cmd(REPO_NAME, REPO_SYNC.no_ip_remote_name())
        FETCH_PUSH_CMDS.append(push_no_ip)

    FETCH_PATH = os.path.join(SAVE_SCRIPTS_FOLDER, "git_fetch_push.ps1")
    REPO_SYNC.save_cmd_list(FETCH_PUSH_CMDS, FETCH_PATH)
