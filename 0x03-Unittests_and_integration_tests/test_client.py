#!/usr/bin/env python3
"""Test Client Module"""

import unittest
from parameterized import parameterized, parameterized_class
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """ TestGithubOrgClient class that inherits from unittest.TestCase.
    """
    @parameterized.expand([
        "google",
        "abc"])
    @patch("client.get_json")
    def test_org(self, name_org, mock_url):
        """ Method for test GithubOrgClient.org"""
        endpoint = "https://api.github.com/orgs/{}".format(name_org)
        get_org = GithubOrgClient(name_org)
        self.assertEqual(get_org.org, mock_url.return_value)
        mock_url.assert_called_once_with(endpoint)

    def test_public_repos_url(self):
        """ Method for testing GithubOrgClient._public_repos_url """
        mock_url = "www.someurl.com"
        the_payload = {"repos_url": mock_url}
        with patch('client.GithubOrgClient.org',
                   PropertyMock(return_value=the_payload)):
            res = GithubOrgClient("somewhere")
            self.assertEqual(res._public_repos_url, mock_url)

    @patch("client.get_json")
    def test_public_repos(self, repo_mock):
        """ To unit-test GithubOrgClient.public_repos. """
        the_payload = [{"name": "someone"}, {"name": "Betty"}]
        repo_mock.return_value = the_payload
        with patch("client.GithubOrgClient._public_repos_url",
                   new_callable=PropertyMock) as mock_client:
            test_name = GithubOrgClient("someone").public_repos()
            self.assertEqual(test_name, ['someone', 'Betty'])
            mock_client.assert_called_once()
            repo_mock.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, key, expected_return):
        """Method for testing GithubOrgClient.has_license. """
        self.assertEqual(
            GithubOrgClient.has_license(repo, key), expected_return)


@parameterized_class([{"org_payload": TEST_PAYLOAD[0][0],
                       "repos_payload": TEST_PAYLOAD[0][1],
                       "expected_repos": TEST_PAYLOAD[0][2],
                       "apache2_repos": TEST_PAYLOAD[0][3]}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Class for testing GithubOrgClient integration"""
    @classmethod
    def setUpClass(cls):
        """ The setupClass should mock requests.get to return example
            payloads found in the fixtures. """
        cls.get_patcher = patch('requests.get', side_effect=[
            cls.org_payload, cls.repos_payload
        ])
        cls.mock_test = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher method"""
        cls.get_patcher.stop()
