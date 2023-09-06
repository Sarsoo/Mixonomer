#!/usr/bin/env python3
import shutil
import os
from pathlib import Path
import sys
import subprocess
from cmd import Cmd

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

stage_dir = '.music-tools'
scss_rel_path = Path('src', 'scss', 'style.scss')
css_rel_path = Path('build', 'style.css')

folders_to_ignore = ['venv', 'docs', '.git', '.idea', 'node_modules']


"""
COMPONENTS:

* App Engine
* Cloud Functions:
    run_user_playlist
    update_tag

    run_all_playlists
    run_all_playlist_stats
    run_all_tags

"""


class Admin(Cmd):
    intro = 'Mixonomer Admin... ? for help'
    prompt = '> '

    locals = ['spotframework', 'fmframework', 'spotfm']

    def do_prepare_local_stage(self, args):
        """
        Prepare local working directory for deployment using static sarsoolib injections
        """
        # Now done via online repos, not static injection
        print('>> backing up a directory')
        os.chdir(Path(__file__).absolute().parent.parent)

        print('>> deleting old deployment stage')
        shutil.rmtree(stage_dir, ignore_errors=True)

        print('>> copying main source')
        shutil.copytree('playlist-manager' if Path('playlist-manager').exists() else 'Music-Tools',
                        stage_dir,
                        ignore=lambda path, contents:
                            contents if any(i in Path(path).parts for i in folders_to_ignore) else []
                        )

        for dependency in Admin.locals:
            print(f'>> injecting {dependency}')
            shutil.copytree(
                Path(dependency, dependency),
                Path(stage_dir, dependency)
            )

        os.chdir(stage_dir)

# ADMIN

    def do_set_project(self, args):
        """
        Set project setting in gcloud console
        """
        print('>> setting project')
        subprocess.check_call(f'gcloud config set project {args.strip()}', shell=True)

    @property
    def gcloud_project(self):
        return subprocess.run(["gcloud", "config", "get-value", "project"], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
    
    def do_project(self, args):
        print(f"\"{self.gcloud_project}\"")

    def deploy_function(self, name, project_id, timeout: int = 60, region='europe-west2'):
        """
        Deploy function with required environment variables
        """
        subprocess.check_call(
            f'gcloud functions deploy {name} '
            f'--region {region} '
            f'--gen2 '
            '--runtime=python311 '
            f'--trigger-topic {name} '
            f'--set-env-vars DEPLOY_DESTINATION=PROD,GOOGLE_CLOUD_PROJECT={project_id} '
            f'--service-account {name.replace("_", "-")}-func@{self.gcloud_project}.iam.gserviceaccount.com '
            f'--timeout={timeout}s', shell=True
        )

    def do_rename(self, args):
        """
        Rename playlist in firestore
        """
        from music.model.user import User
        from music.model.playlist import Playlist

        username = input('enter username: ')
        user = User.collection.filter('username', '==', username).get()

        if user is None:
            print('>> user not found')

        name = input('enter playlist name: ')
        playlist = user.get_playlist(name)

        if playlist is None:
            print('>> playlist not found')

        new_name = input('enter new name: ')
        playlist.name = new_name
        playlist.update()

# PYTHON

    def copy_main_file(self, path):
        """
        Copy main.{path}.py file corresponding to Python build stage
        """
        print('>> preparing main.py')
        shutil.copy(f'main.{path}.py', 'main.py')

    def do_main_group(self, args):
        """
        Compile front-end and deploy to App Engine. Deploy primary functions (run_user_playlist, update_tag)
        """
        self.do_set_project(None)
        self.export_filtered_dependencies()

        self.do_app(args)
        self.do_tag(None)
        self.do_playlist(None)

    def do_app(self, args):
        """
        Compile front-end and deploy to App Engine
        """
        if not '-nb' in args.strip().split(' '):
            print(">> compiling frontend")
            self.compile_frontend()
        self.copy_main_file('api')

        print('>> deploying app engine service')
        subprocess.check_call('gcloud app deploy', shell=True)

    def function_deploy(self, main, function_id, project_id):
        """Deploy Cloud Function, copy main file and initiate gcloud command

        Args:
            main (str): main path
            function_id (str): function id to deploy to
        """

        if len(project_id) == 0:
            print("no project id provided")
            exit()
            
        self.copy_main_file(main)

        print(f'>> deploying {function_id}')
        self.deploy_function(function_id, project_id)

    def do_tag(self, args):
        """
        Deploy update_tag function
        """
        self.function_deploy('update_tag', 'update_tag', args.strip())

    def do_playlist(self, args):
        """
        Deploy run_user_playlist function
        """
        self.function_deploy('run_playlist', 'run_user_playlist', args.strip())


    # all playlists cron job
    def do_playlist_cron(self, args):
        """
        Deploy run_all_playlists function
        """
        self.function_deploy('cron', 'run_all_playlists', args.strip())

    # all stats refresh cron job
    def do_playlist_stats_cron(self, args):
        """
        Deploy run_all_playlist_stats function
        """
        self.function_deploy('cron', 'run_all_playlist_stats', args.strip())

    # all tags cron job
    def do_tags_cron(self, args):
        """
        Deploy run_all_tags function
        """
        self.function_deploy('cron', 'run_all_tags', args.strip())

    # redeploy all cron job functions
    def do_cron_functions(self, args):
        """
        Deploy background functions including cron job scheduling for update actions (run_all_playlists, run_all_playlist_stats, run_all_tags)
        """
        self.do_set_project(None)
        self.export_filtered_dependencies()
        
        self.do_playlist_cron(None)
        self.do_playlist_stats_cron(None)
        self.do_tags_cron(None)

    def do_pydepend(self, args):
        """
        Generate and export requirements.txt from Poetry manifest
        """
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

# FRONT-END

    def compile_frontend(self):
        """
        Compile sass to css and run npm build task
        """
        print('>> building css')
        subprocess.check_call(f'sass --style=compressed {str(scss_rel_path)} {str(css_rel_path)}', shell=True)

        print('>> building javascript')
        subprocess.check_call('npm run build', shell=True)

    def do_sass(self, args):
        """
        Compile sass to css
        """
        subprocess.check_call(f'sass --style=compressed {str(scss_rel_path)} {str(css_rel_path)}', shell=True)

    def do_watchsass(self, args):
        """
        Run sass compiler with watch argument to begin watching source folder for changes
        """
        subprocess.check_call(f'sass --style=compressed --watch {str(scss_rel_path)} {str(css_rel_path)}', shell=True)

    def do_run(self, args):
        """
        Run Flask app
        """
        subprocess.check_call(f'python main.api.py', shell=True)

    def do_test(self, args):
        """
        Run Python unit tests
        """
        subprocess.check_call(f'python -u -m unittest discover -s tests', shell=True)

    def do_docs(self, args):
        """
        Compile documentation using sphinx
        """
        subprocess.check_call(f'sphinx-build docs docs/build -b html', shell=True)
    
    def do_exit(self, args):
        """
        Exit script
        """
        exit(0)

def test():
    Admin().onecmd('test')

def run():
    Admin().onecmd('run')

def docs():
    Admin().onecmd('docs')

if __name__ == '__main__':
    console = Admin()
    if len(sys.argv) > 1:
        console.onecmd(' '.join(sys.argv[1:]))
    else:
        console.cmdloop()
