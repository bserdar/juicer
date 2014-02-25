# -*- coding: utf-8 -*-
# Juicer - Administer Pulp and Release Carts
# Copyright © 2012-2014, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from juicer.admin.JuicerAdmin import JuicerAdmin as ja
import juicer.utils

def create_repo(args):
    pulp = ja(args)
    pulp.create_repo(args.arch, args.name, args.feed, args.envs, args.checksum_type)


def import_repo(args):
    pulp = ja(args)
    # Get our TODO specs from juicer-admin
    (to_create, to_update) = pulp.import_repo(args.from_file, args.noop)

    if args.noop:
        if to_create:
            juicer.utils.Log.log_info("NOOP: Would have created repos with definitions:")
            juicer.utils.Log.log_info("%s", juicer.utils.create_json_str(to_create, indent=4, cls=juicer.common.Repo.RepoEncoder))

        for env,repos in to_update.iteritems():
            for repo in repos:
                debug_msg = None
                repo_diff_specs = repo['reality_check_in_env']
                for diff_spec in repo_diff_specs:
                    # [0] = env, [1] = RepoDiff, [2] = PulpRepo
                    if diff_spec[0] == env:
                        this_env_diff_spec = diff_spec
                        repo_diff = diff_spec[1]
                        # "{'distributor': {'distributor_config': {}}, 'importer': {'importer_config': {}}}"
                        # Does the diff contain anything?
                        if repo_diff.diff()['distributor']['distributor_config'] or repo_diff.diff()['importer']['importer_config']:
                            debug_msg = "    %s" % juicer.utils.create_json_str(this_env_diff_spec[1], indent=4, cls=juicer.common.Repo.RepoEncoder)

                if debug_msg:
                    juicer.utils.Log.log_info("NOOP: Would have updated %s-%s with:", repo['name'], env)
                    juicer.utils.Log.log_info(debug_msg)

    else:
        for repo in to_create:
            pulp.create_repo(repo_name=repo['name'],
                             feed=repo['feed'],
                             envs=repo['missing_in_env'],
                             checksum_type=repo['checksum_type'])

        for env,repos in to_update.iteritems():
            for repo in repos:
                juicer.utils.Log.log_info("Updated %s-%s with:", repo['name'], env)
                repo_diff_specs = repo['reality_check_in_env']
                for diff_spec in repo_diff_specs:
                    if diff_spec[0] == env:
                        repo_diff = diff_spec[1]
                        if repo_diff.diff()['distributor']['distributor_config'] or repo_diff.diff()['importer']['importer_config']:
                            pulp._update_repo(repo, diff_spec[2], env, diff_spec[1])


def create_user(args):
    pulp = ja(args)
    pulp.create_user(args.login, args.password, args.name, args.envs)

def list_repos(args):
    pulp = ja(args)
    repo_lists = pulp.list_repos(args.envs)
    if args.json:
        print juicer.utils.create_json_str(repo_lists, indent=4)
    else:
        for env, repos in repo_lists.iteritems():
            print "%s(%d): %s" % (env, len(repos), ' '.join(repos))

def sync_repo(args):
    pulp = ja(args)
    pulp.sync_repo(args.name, args.envs)


def show_repo(args):
    pulp = ja(args)
    repo_objects = pulp.show_repo(args.name, args.envs)

    if args.json:
        # JSON output requested
        print juicer.utils.create_json_str(repo_objects, indent=4,
                                           cls=juicer.common.Repo.RepoEncoder)
    else:
        found_repos = 0
        for env, repos in repo_objects.iteritems():
            found_repos += len(repos)
        if found_repos == 0:
            print "Could not locate repo(s) in any environment"
            return False

        # Human readable table-style output by default
        rows = [['Repo', 'Env', 'RPMs', 'SRPMs', 'Checksum', 'Feed']]
        for env,repos in repo_objects.iteritems():
            # 'repos' contains a list of hashes
            for repo in repos:
                # each hash represents a repo
                repo_name = repo['name']
                repo_rpm_count = repo['rpm_count']
                repo_srpm_count = repo['srpm_count']
                repo_checksum = repo['checksum_type']
                repo_feed = repo['feed']
                rows.append([repo_name, env, repo_rpm_count, repo_srpm_count, repo_checksum, str(repo_feed)])

        print juicer.utils.table(rows)

def show_user(args):
    pulp = ja(args)
    pulp.show_user(args.login, args.envs)


def delete_repo(args):
    pulp = ja(args)
    pulp.delete_repo(args.name, args.envs)


def delete_user(args):
    pulp = ja(args)
    pulp.delete_user(args.login, args.envs)


def role_add(args):
    pulp = ja(args)
    pulp.role_add(args.role, args.login, args.envs)


def list_roles(args):
    pulp = ja(args)
    pulp.list_roles(args.envs)


def update_user(args):
    pulp = ja(args)
    pulp.update_user(args.login, args.name, args.password, args.envs)


def setup(args):
    pulp = ja(args)
    pulp.setup()


def list_users(args):
    pulp = ja(args)
    pulp.list_users(args.envs)
