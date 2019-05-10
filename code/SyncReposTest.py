"""
Unit tests for RepoSync
"""
import unittest
import os
from SyncRepos import RepoSync

class RepoSyncUnitTest(unittest.TestCase):
    """
    Unit tests for RepoSync
    """


    def get_repo_sync(self):
        no_ip = r"https://noip.example.com"
        has_ip = r"https://hasip.visualstudio.com"
        save_scripts = r"c:\\users\\eric\\documents\\git_sync_scripts\\"
        git_root = r'D:\GitSyncRoot'
        rs = RepoSync(git_root, save_scripts, no_ip, has_ip)
        return rs

    def test_get_missing_repos_returns_missing_item(self):
        local_folders = ["LazyRobots", "OysterToad"]
        repo_info = []
        repo_info.append(dict(name='LazyRobots'))
        repo_info.append(dict(name='OysterToad'))
        repo_info.append(dict(name='SqlTest'))

        rs = self.get_repo_sync()
        missing_repos = rs.get_missing_local_repos(local_folders, repo_info)
        test = missing_repos[0].get("name") == 'SqlTest'
        self.assertTrue(test)

    def test_make_clone_script_returns_correct_string(self):
        repo_info = []
        repo_info.append(dict(name='LazyRobots', id ="12345", remoteUrl = "http://example.com/_git/lazy_robots"))
        repo_info.append(dict(name='OysterToad', id="3456", remoteUrl="http://example.com/_git/oystertoad"))
        
        rs = self.get_repo_sync()
        git_folder = rs.git_root_path #r"c:\\azdo"
        clone_cmds = rs.make_clone_script(repo_info)
        where_to_clone = os.path.join(git_folder, repo_info[0]["name"])
        expected_0 = 'git clone {0} \"{1}\"'.format(repo_info[0]["remoteUrl"], where_to_clone)
        self.assertEqual(expected_0, clone_cmds[0])

    def test_generate_remotes(self):
        repo_info = []
        repo_info.append(dict(name='LazyRobots',
                             id="12345",
                              remoteUrl="https://noip.example.com/_git/lazy_robots"))
        repo_info.append(dict(name='OysterToad',
                              id="3456",
                              remoteUrl="https://noip.example.com/_git/oystertoad"))

        rs = self.get_repo_sync()
        cmds = rs.generate_remotes(repo_info)
        self.assertIn(rs.server_no_ip, cmds[0]) #set first remote to noip
        self.assertIn(rs.server_ip, cmds[1]) #set second remote to has ip

        self.assertIn(rs.no_ip_remote_name(), cmds[0])
        self.assertIn(rs.ip_remote_name(), cmds[1])
            
    def test_get_fetch_cmd(self):
        rs = self.get_repo_sync()
        cmd = rs.get_fetch_cmd("LazyRobots", rs.ip_remote_name())
        expected = 'git --work-tree=\"D:\\GitSyncRoot\\LazyRobots" --git-dir="D:\\GitSyncRoot\\LazyRobots\\.git" fetch --tags --force ip_remote'
        self.assertEqual(cmd, expected)

if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(CommentsUnitTest)
    #unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
