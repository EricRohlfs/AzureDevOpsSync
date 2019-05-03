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

    def test_get_missing_repos_returns_missing_item(self):
        local_folders = ["LazyRobots", "OysterToad"]
        repo_info = []
        repo_info.append(dict(name='LazyRobots'))
        repo_info.append(dict(name='OysterToad'))
        repo_info.append(dict(name='SqlTest'))

        rs = RepoSync()
        missing_repos = rs.get_missing_local_repos(local_folders, repo_info)
        test = missing_repos[0].get("name") == 'SqlTest'
        self.assertTrue(test)

    def test_make_clone_script_returns_correct_string(self):
        repo_info = []
        repo_info.append(dict(name='LazyRobots', id ="12345", web_url = "http://example.com/_git/lazy_robots"))
        repo_info.append(dict(name='OysterToad', id="3456", web_url="http://example.com/_git/oystertoad"))
        git_folder = r"c:\\azdo"
        rs = RepoSync()
        clone_cmds = rs.make_clone_script(repo_info, git_folder)
        where_to_clone = os.path.join(git_folder, repo_info[0]["name"])
        expected_0 = 'git clone {0} \"{1}\"'.format(repo_info[0]["web_url"], where_to_clone)
        self.assertEqual(expected_0, clone_cmds[0])

    def test_generate_remotes(self):
        repo_info = []
        repo_info.append(dict(name='LazyRobots',
                             id="12345",
                              web_url="noip.visualstudio.com/_git/lazy_robots"))
        repo_info.append(dict(name='OysterToad',
                              id="3456",
                              web_url="noip.visualstudio.com/_git/oystertoad"))

        no_ip_url = "noip.visualstudio.com"
        has_ip_url = "hasip.visualstudio.com"

        rs = RepoSync()
        cmds = rs.generate_remotes(repo_info, no_ip_url, has_ip_url)
        self.assertIn(no_ip_url, cmds[0]) #set first remote to noip
        self.assertIn(has_ip_url, cmds[1]) #set second remote to has ip

        self.assertIn(rs.no_ip_remote_name(), cmds[0])
        self.assertIn(rs.ip_remote_name(), cmds[1])
            
    def test_get_fetch_cmd(self):
        rs = RepoSync()
        cmd = rs.get_fetch_cmd("LazyRobots", rs.ip_remote_name())
        expected = "git --work-tree=LazyRobots --git-dir=LazyRobots/.git fetch --tags --force ip_remote"
        self.assertEqual(cmd, expected)

if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(CommentsUnitTest)
    #unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
