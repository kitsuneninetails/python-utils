import unittest

from python_utils.shell.cli import LinuxCLI
from python_utils.tests.utils.test_utils import run_unit_test


class CLITest(unittest.TestCase):
    def test_write_file(self):
        LinuxCLI().rm('tmp-test')
        LinuxCLI().write_to_file('tmp-test', 'test1\n')
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'test1\n')
        LinuxCLI().write_to_file('tmp-test', 'test2\n', append=True)
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'test1\ntest2\n')
        LinuxCLI(priv=True).write_to_file('tmp-test', 'test3\n', append=True)
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'test1\ntest2\ntest3\n')
        LinuxCLI().rm('tmp-test')

    def test_replace_in_file(self):
        LinuxCLI().write_to_file(
            'tmp-test',
            'easy\n"harder"\n#"//[({<hardest>}).*]//"')
        LinuxCLI().replace_text_in_file(
            'tmp-test', 'easy', 'hard')
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'hard\n"harder"\n#"//[({<hardest>}).*]//"')
        LinuxCLI().replace_text_in_file(
            'tmp-test', '"harder"', '(not-so-hard)')
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'hard\n(not-so-hard)\n#"//[({<hardest>}).*]//"')
        LinuxCLI().replace_text_in_file(
            'tmp-test', '#"//[({<hardest>}).*]//"',
            '"{[(*pretty*-<darn>-.:!hard!:.)]}"')
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'hard\n(not-so-hard)\n"{[(*pretty*-<darn>-.:!hard!:.)]}"')

        LinuxCLI().write_to_file(
            'tmp-test',
            'global-testglobal-test\nglobal-test\n\nhere '
            'globally is a global-test but global')
        LinuxCLI().replace_text_in_file(
            'tmp-test', 'global', 'local')
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'local-testglobal-test\nlocal-test\n\nhere locally '
            'is a global-test but global')
        LinuxCLI().replace_text_in_file('tmp-test', 'global', 'local')
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'local-testlocal-test\nlocal-test\n\nhere locally '
            'is a local-test but global')

        LinuxCLI().write_to_file(
            'tmp-test',
            'global-testglobal-test\nglobal-test\n\nhere globally '
            'is a global-test but global')
        LinuxCLI().replace_text_in_file(
            'tmp-test', 'global', 'local', line_global_replace=True)
        self.assertEqual(
            LinuxCLI().read_from_file('tmp-test'),
            'local-testlocal-test\nlocal-test\n\nhere locally '
            'is a local-test but local')

    def test_wc(self):
        cli = LinuxCLI()
        cli.rm('tmp')
        try:
            cli.write_to_file('tmp', 'foo\nbar\nbaz\nbamf zap\n')
            ret = cli.wc('tmp')
            self.assertEqual(4, ret['lines'])
            self.assertEqual(5, ret['words'])
            self.assertEqual(21, ret['chars'])
        finally:
            cli.rm('tmp')

    def test_cmd(self):
        cli = LinuxCLI(priv=False)

        try:
            with open('test-file1', mode='w') as file1:
                cli.cmd([['ls'],  ['grep', 'py']], stdout=file1)

            data = cli.read_from_file('test-file1')
            self.assertNotEqual(0, len(data))

        finally:
            cli.rm('test-file1')

    def test_pipes(self):
        cli = LinuxCLI(priv=False)
        ret = cli.cmd([['ls'], ['grep', 'py']])
        self.assertEqual('ls|grep py', ret.command)
        self.assertNotEqual(0, len(ret.stdout))

        ret2 = cli.cmd([['ls'], ['grep', 'py']], blocking=False)
        self.assertEqual('ls|grep py', ret2.command)
        self.assertIsNotNone(ret2.process)
        o, e = ret2.process.communicate()
        self.assertEqual(0, ret2.process.returncode)
        self.assertNotEqual(0, len(o))

        ret3 = cli.cmd([['ls']])
        self.assertEqual('ls', ret3.command)
        self.assertNotEqual(0, len(ret3.stdout))

        try:
            with open('test-file4', mode='w') as file4:
                ret4 = cli.cmd([['ls'], ['grep', 'py']],
                               blocking=False, stdout=file4)

            self.assertIsNotNone(ret4.process)
            ret4.process.communicate()

            data4 = cli.read_from_file('test-file4')
            self.assertNotEqual(0, len(data4))
        finally:
            cli.rm('test-file4')

        try:
            with open('test-file5', mode='w') as file5:
                ret5 = cli.cmd([['ls']], blocking=False, stdout=file5)
                self.assertIsNotNone(ret5.process)
                ret5.process.communicate()

            data5 = cli.read_from_file('test-file5')
            self.assertNotEqual(0, len(data5))
        finally:
            cli.rm('test-file5')

        try:
            ret6 = cli.cmd([['ls'], ['tee', 'test-file6']],
                           blocking=False)
            self.assertIsNotNone(ret6.process)
            ret6.process.communicate()

            data6 = cli.read_from_file('test-file6')
            self.assertNotEqual(0, len(data6))
        finally:
            cli.rm('test-file6')

    def test_pid_functions(self):
        cli = LinuxCLI()
        root_pids = cli.get_process_pids("root")
        pids = cli.get_running_pids()
        ppids = cli.get_parent_pids("1")

        self.assertTrue(len(root_pids) > 0)
        self.assertTrue(len(pids) > 0)
        self.assertTrue(len(ppids) > 0)

    def test_grep_count(self):
        cli = LinuxCLI()
        try:
            cli.write_to_file('test-grep-count',
                              'foo\nfoo\nbar\nfoo bar\nfoo foo\n')
            count = cli.grep_count('cat test-grep-count', 'foo')
            self.assertEqual(4, count)
            count2 = cli.grep_count('cat test-grep-count', 'baz')
            self.assertEqual(0, count2)
            count3 = cli.grep_count(
                ['cat', 'test-grep-count'], 'foo')
            self.assertEqual(4, count3)
            count4 = cli.grep_count(
                ['cat', 'test-grep-count'], 'baz')
            self.assertEqual(0, count4)
        finally:
            cli.rm('test-grep-count')

    def tearDown(self):
        LinuxCLI().rm('tmp-test')

run_unit_test(CLITest)
