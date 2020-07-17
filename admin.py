#!/usr/bin/env python3
import shutil
import os
from pathlib import Path
import sys
from cmd import Cmd

stage_dir = '_playlist-manager'
scss_rel_path = Path('src', 'scss', 'style.scss')
css_rel_path = Path('build', 'style.css')

folders_to_ignore = ['venv', 'docs', '.git', '.idea', 'node_modules']


class Admin(Cmd):
    intro = 'Music Tools Admin... ? for help'
    prompt = '> '

    def prepare_stage(self):
        print('>> backing up a directory')
        os.chdir(Path(__file__).parent.parent)

        print('>> deleting old deployment stage')
        shutil.rmtree(stage_dir, ignore_errors=True)

        print('>> copying main source')
        shutil.copytree('playlist-manager' if Path('playlist-manager').exists() else 'Music-Tools',
                        stage_dir,
                        ignore=lambda path, contents:
                            contents if any(i in Path(path).parts for i in folders_to_ignore) else []
                        )

        for dependency in ['spotframework', 'fmframework', 'spotfm']:
            print(f'>> injecting {dependency}')
            shutil.copytree(
                Path(dependency, dependency),
                Path(stage_dir, dependency)
            )

        os.chdir(stage_dir)
        os.system('gcloud config set project sarsooxyz')

    def prepare_frontend(self):
        print('>> building css')
        os.system(f'sass --style=compressed {scss_rel_path} {css_rel_path}')

        print('>> building javascript')
        os.system('npm run build')

    def prepare_main(self, path):
        print('>> preparing main.py')
        shutil.copy(f'main.{path}.py', 'main.py')

    def deploy_function(self, name, timeout: int = 60, region='europe-west2'):
        os.system(f'gcloud functions deploy {name} '
                  f'--region {region} '
                  '--runtime=python38 '
                  f'--trigger-topic {name} '
                  '--set-env-vars DEPLOY_DESTINATION=PROD '
                  f'--timeout={timeout}s')

    def do_all(self, args):
        self.prepare_frontend()
        self.prepare_stage()

        self.prepare_main('api')
        print('>> deploying api')
        os.system('gcloud app deploy')

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
        os.system('gcloud app deploy')

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

    def do_exit(self, args):
        exit(0)

    def do_sass(self, args):
        os.system(f'sass --style=compressed {scss_rel_path} {css_rel_path}')

    def do_watchsass(self, args):
        os.system(f'sass --style=compressed --watch {scss_rel_path} {css_rel_path}')

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


if __name__ == '__main__':
    console = Admin()
    if len(sys.argv) > 1:
        console.onecmd(' '.join(sys.argv[1:]))
    else:
        console.cmdloop()
