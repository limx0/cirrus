#!/usr/bin/env python
"""
tests for VirtualenvPip builder plugin

"""

import unittest
import mock
import tempfile
import os

from cirrus.build import FACTORY


PYPIRC = \
"""
[distutils]
index-servers =
  pypi
  devpi

[pypi]
repository: https://pypi.python.org/pypi/
username: steve
password: stevespass

[devpi]
repository: https://localhost:4000
username: the_steve
password: stevespass

"""

class VenvPipBuilderTest(unittest.TestCase):


    @mock.patch('cirrus.builder_plugin.load_configuration')
    @mock.patch('cirrus.builder_plugin.repo_directory')
    @mock.patch('cirrus.plugins.builders.venv_pip.VirtualEnvironment')
    @mock.patch('cirrus.plugins.builders.venv_pip.local')
    @mock.patch('cirrus.builder_plugin.local')
    @mock.patch('cirrus.plugins.builders.venv_pip.build_pip_command')
    def test_builder(self, mock_pip, mock_base_local, mock_local, mock_venv_cls, mock_repo_dir, mock_load_conf):
        mock_pip.return_value = "PIP_COMMAND"
        mock_repo_dir.return_value = "REPO"

        mock_venv = mock.Mock()
        mock_venv.open_or_create = mock.Mock()
        mock_venv_cls.return_value = mock_venv
        mock_conf = mock.Mock(name="load_configuration")
        mock_conf.get = mock.Mock(return_value={
            'build': {'builder': 'conf'},
            'extra_requirements': ['test-requirements.txt', 'more-reqs.txt']
        })
        mock_load_conf.return_value = mock_conf
        plugin = FACTORY('VirtualenvPip')
        plugin.create(clean=True)
        plugin.activate()
        mock_base_local.assert_has_calls([
            mock.call('. REPO/venv/bin/activate && python setup.py develop')
        ])
        mock_local.assert_has_calls([
            mock.call('PIP_COMMAND'),
            mock.call('PIP_COMMAND'),
            mock.call('PIP_COMMAND')
        ])
        mock_base_local.reset_mock()
        plugin.create(clean=True, nosetupdevelop=True)
        self.failUnless(not mock_base_local.called)

    @mock.patch('cirrus.builder_plugin.load_configuration')
    @mock.patch('cirrus.builder_plugin.repo_directory')
    @mock.patch('cirrus.plugins.builders.venv_pip.VirtualEnvironment')
    @mock.patch('cirrus.plugins.builders.venv_pip.local')
    @mock.patch('cirrus.builder_plugin.local')
    @mock.patch('cirrus.plugins.builders.venv_pip.build_pip_command')
    def test_builder_python_bin(self, mock_pip, mock_base_local, mock_local, mock_venv_cls, mock_repo_dir, mock_load_conf):
        mock_pip.return_value = "PIP_COMMAND"
        mock_repo_dir.return_value = "REPO"

        mock_venv = mock.Mock()
        mock_venv.open_or_create = mock.Mock()
        mock_venv_cls.return_value = mock_venv
        mock_conf = mock.Mock(name="load_configuration")
        mock_conf.get = mock.Mock(return_value={
            'build': {'builder': 'conf'},
            'extra_requirements': ['test-requirements.txt', 'more-reqs.txt'],
            'python': 'python6.7'
        })
        mock_load_conf.return_value = mock_conf
        plugin = FACTORY('VirtualenvPip')
        plugin.create(clean=True)

        mock_venv_cls.assert_has_calls([
            mock.call('REPO/venv', python='python6.7', system_site_packages=False)
        ])

        # verify conda style python version works too
        mock_venv_cls.reset_mock()
        mock_conf = mock.Mock(name="load_configuration")
        mock_conf.get = mock.Mock(return_value={
            'build': {'builder': 'conf'},
            'extra_requirements': ['test-requirements.txt', 'more-reqs.txt'],
            'python': '6.7'
        })
        mock_load_conf.return_value = mock_conf
        plugin2 = FACTORY('VirtualenvPip')
        plugin2.create(clean=True)

        mock_venv_cls.assert_has_calls([
            mock.call('REPO/venv', python='python6.7', system_site_packages=False)
        ])

    @mock.patch('cirrus.builder_plugin.load_configuration')
    @mock.patch('cirrus.builder_plugin.repo_directory')
    @mock.patch('cirrus.plugins.builders.venv_pip.VirtualEnvironment')
    @mock.patch('cirrus.plugins.builders.venv_pip.local')
    @mock.patch('cirrus.builder_plugin.local')
    @mock.patch('cirrus.plugins.builders.venv_pip.build_pip_command')
    def test_builder_errors(self, mock_pip, mock_base_local, mock_local, mock_venv_cls, mock_repo_dir, mock_load_conf):
        mock_pip.return_value = "PIP_COMMAND"
        mock_repo_dir.return_value = "REPO"

        mock_venv = mock.Mock()
        mock_local.side_effect = OSError("BOOM")
        mock_venv.open_or_create = mock.Mock()
        mock_venv_cls.return_value = mock_venv
        mock_conf = mock.Mock(name="load_configuration")
        mock_conf.get = mock.Mock(return_value={
            'build': {'builder': 'conf'},
            'extra_requirements': ['test-requirements.txt', 'more-reqs.txt']
        })
        mock_load_conf.return_value = mock_conf
        plugin = FACTORY('VirtualenvPip')
        self.assertRaises(OSError, plugin.create, clean=True)

        mock_local.side_effect = [None, OSError("BOOM")]
        self.assertRaises(OSError, plugin.create, clean=True)


    @mock.patch('cirrus.builder_plugin.load_configuration')
    @mock.patch('cirrus.builder_plugin.repo_directory')
    @mock.patch('cirrus.plugins.builders.venv_pip.local')
    @mock.patch('cirrus.plugins.builders.venv_pip.os.path.exists')
    def test_builder_clean(self, mock_exists, mock_local, mock_repo, mock_conf):
        mock_exists.return_value = True
        plugin = FACTORY('VirtualenvPip')
        plugin.clean()
        self.assertTrue(mock_local.called)


if __name__ == '__main__':
    unittest.main()
