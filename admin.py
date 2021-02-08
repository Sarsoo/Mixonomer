#!/usr/bin/env python3
import shutil
import os
from pathlib import Path
import sys
import subprocess
from cmd import Cmd

stage_dir = '.music-tools'
scss_rel_path = Path('src', 'scss', 'style.scss')
css_rel_path = Path('build', 'style.css')

folders_to_ignore = ['venv', 'docs', '.git', '.idea', 'node_modules']


class Admin(Cmd):
    intro = 'Music Tools Admin... ? for help'
    prompt = '> '

    locals = ['spotframework', 'fmframework', 'spotfm']

    def prepare_stage(self):
        print('>> freezing dependencies')
        self.export_filtered_dependencies()

        # Now done via online repos, not static injection
        # print('>> backing up a directory')
        # os.chdir(Path(__file__).absolute().parent.parent)

        # print('>> deleting old deployment stage')
        # shutil.rmtree(stage_dir, ignore_errors=True)

        # print('>> copying main source')
        # shutil.copytree('playlist-manager' if Path('playlist-manager').exists() else 'Music-Tools',
        #                 stage_dir,
        #                 ignore=lambda path, contents:
        #                     contents if any(i in Path(path).parts for i in folders_to_ignore) else []
        #                 )

        # for dependency in Admin.locals:
        #     print(f'>> injecting {dependency}')
        #     shutil.copytree(
        #         Path(dependency, dependency),
        #         Path(stage_dir, dependency)
        #     )

        # os.chdir(stage_dir)
        subprocess.check_call('gcloud config set project sarsooxyz', shell=True)

    def prepare_frontend(self):
        print('>> building css')
        subprocess.check_call(f'sass --style=compressed {str(scss_rel_path)} {str(css_rel_path)}', shell=True)

        print('>> building javascript')
        subprocess.check_call('npm run build', shell=True)

    def prepare_main(self, path):
        print('>> preparing main.py')
        shutil.copy(f'main.{path}.py', 'main.py')

    def deploy_function(self, name, timeout: int = 60, region='europe-west2'):
        subprocess.check_call(
            f'gcloud functions deploy {name} '
            f'--region {region} '
            '--runtime=python38 '
            f'--trigger-topic {name} '
            '--set-env-vars DEPLOY_DESTINATION=PROD '
            f'--timeout={timeout}s', shell=True
        )

    def do_all(self, args):
        # self.prepare_frontend()
        self.prepare_stage()

        self.prepare_main('api')
        print('>> deploying api')
        subprocess.check_call('gcloud app deploy', shell=True)

        self.prepare_main('update_tag')
        print('>> deploying tag function')
        self.deploy_function('update_tag')

        self.prepare_main('run_playlist')
        print('>> deploying playlist function')
        self.deploy_function('run_user_playlist')

    def do_api(self, args):
        self.prepare_frontend()

        self.prepare_stage()
        self.prepare_main('api')

        print('>> deploying')
        subprocess.check_call('gcloud app deploy', shell=True)

    def do_tag(self, args):
        self.prepare_stage()
        self.prepare_main('update_tag')

        print('>> deploying')
        self.deploy_function('update_tag')

    def do_playlist(self, args):
        self.prepare_stage()
        self.prepare_main('run_playlist')

        print('>> deploying')
        self.deploy_function('run_user_playlist')

    # all playlists cron job
    def do_playlist_cron(self, args):
        self.prepare_stage()
        self.prepare_main('cron')

        print('>> deploying')
        self.deploy_function('run_all_playlists')

    # all stats refresh cron job
    def do_playlist_stats(self, args):
        self.prepare_stage()
        self.prepare_main('cron')

        print('>> deploying')
        self.deploy_function('run_all_playlist_stats')

    # all tags cron job
    def do_tags_cron(self, args):
        self.prepare_stage()
        self.prepare_main('cron')

        print('>> deploying')
        self.deploy_function('run_all_tags')

    # redeploy all cron job functions
    def do_all_cron(self, args):
        self.prepare_stage()
        self.prepare_main('cron')

        print('>> deploying playlists')
        self.deploy_function('run_all_playlists')
        print('>> deploying stats')
        self.deploy_function('run_all_playlist_stats')
        print('>> deploying tags')
        self.deploy_function('run_all_tags')

    def do_exit(self, args):
        exit(0)

    def do_sass(self, args):
        subprocess.check_call(f'sass --style=compressed {str(scss_rel_path)} {str(css_rel_path)}', shell=True)

    def do_watchsass(self, args):
        subprocess.check_call(f'sass --style=compressed --watch {str(scss_rel_path)} {str(css_rel_path)}', shell=True)

    def do_rename(self, args):
        from music.model.user import User
        from music.model.playlist import Playlist

        username = input('enter username: ')
        user = User.collection.filter('username', '==', username).get()

        if user is None:
            print('>> user not found')

        name = input('enter playlist name: ')
        playlist = Playlist.collection.parent(user.key).filter('name', '==', name).get()

        if playlist is None:
            print('>> playlist not found')

        new_name = input('enter new name: ')
        playlist.name = new_name
        playlist.update()

    def do_depend(self, args):
        return subprocess.check_output('poetry export -f requirements.txt --output requirements.txt', shell=True, text=True)

    def do_filt_depend(self, args):
        self.export_filtered_dependencies()

    def export_filtered_dependencies(self):
        string = subprocess.check_output('poetry export -f requirements.txt --without-hashes', shell=True, text=True)

        depend = string.split('\n')
        
        # filtered = [i for i in depend if not any(i.startswith(local) for local in Admin.locals)]
        # filtered = [i for i in filtered if '==' in i]
        # filtered = [i[:-2] for i in filtered] # get rid of space and slash at end of line
        filtered = [i.split(';')[0] for i in depend]

        with open('requirements.txt', 'w') as f:
            f.write("\n".join(filtered))

def test():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service.json'
    subprocess.check_call("python -u -m unittest discover -s tests", shell=True)

if __name__ == '__main__':
    console = Admin()
    if len(sys.argv) > 1:
        console.onecmd(' '.join(sys.argv[1:]))
    else:
        console.cmdloop()
