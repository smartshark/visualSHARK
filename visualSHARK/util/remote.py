import requests


class RemoteShark(object):
    """Wraps code to run jobs on the ServerSHARK.

    This should not contain django dependencies as it will someday be run on an exclusive worker.

    TODO:
    - error reporting, unknown plugin
    """

    def __init__(self, api_url, api_key, substitutions):
        self._api_key = api_key
        self._url = api_url
        self._substitutions = substitutions

    def list_plugins(self):
        r = requests.get('{}/plugin/?ak={}'.format(self._url, self._api_key))
        dat = r.json()
        return dat['plugins']

    def list_plugin_arguments(self, plugin_ids):
        r = requests.get('{}/argument/?ak={}&plugin_ids={}'.format(self._url, self._api_key, ','.join(plugin_ids)))
        arguments = r.json()
        return arguments

    def test_connection(self, data):
        r = requests.get('{}/test/?ak={}&ping={}'.format(self._url, self._api_key, data['ping']))
        dat = r.json()
        return r.status_code == 200, dat

    def _get_form_args(self, plugin_ids, vals):
        arguments = self.list_plugin_arguments(plugin_ids)

        form_args = []
        for plugin_id, args in arguments.items():
            for arg in args:
                val = vals.get(arg['name'], '')
                if not val:
                    tmp = self._substitutions.get(arg['name'], '')
                    if tmp:
                        val = tmp['name']
                form_args.append(('{}_argument_{}'.format(plugin_id, arg['id']), val))
        return form_args

    def collect_revision(self, project_mongo_ids, plugin_ids, vals={}):
        pids = plugin_ids

        # we need to fetch ids for our names if we have str instead of ids
        if not all([p.isnumeric() for p in plugin_ids]):
            pids = []
            plugins = self.list_plugins()
            for p in plugin_ids:
                for p2 in plugins:
                    if p2['name'].lower() == p.lower():
                        pids.append(str(p2['id']))
        form_args = self._get_form_args(pids, vals)

        req = {'ak': self._api_key,
               'execution': 'rev',
               'revisions': ','.join(vals['revisions']),
               'plugin_ids': ','.join(pids),
               'project_mongo_ids': ','.join(project_mongo_ids),
               'repository_url': '{}'.format(vals['url'])}
        for k, v in form_args:
            req[k] = v

        r = requests.post('{}/collect/'.format(self._url), data=req)
        return r.status_code == 202, {'msg': r.text}

    def collect_other(self, project_mongo_ids, plugin_ids, vals={}):
        pids = plugin_ids

        # we need to fetch ids for our names if we have str instead of ids
        if not all([p.isnumeric() for p in plugin_ids]):
            pids = []
            plugins = self.list_plugins()
            for p in plugin_ids:
                for p2 in plugins:
                    if p2['name'].lower() == p.lower():
                        pids.append(str(p2['id']))

        form_args = self._get_form_args(pids, vals)
        req = {'ak': self._api_key,
               'plugin_ids': ','.join(pids),
               'project_mongo_ids': ','.join(project_mongo_ids),
               'repository_url': '{}'.format(vals['url'])}
        for k, v in form_args:
            req[k] = v

        r = requests.post('{}/collect/'.format(self._url), data=req)
        return r.status_code == 202, {'msg': r.text}
