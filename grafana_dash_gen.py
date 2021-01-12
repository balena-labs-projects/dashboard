import time
import os
import urllib.request
import urllib.error
import json
import stringcase
import base64

class GrafanaDashGen():
    grafana_url = "localhost:"+os.environ['GF_SERVER_HTTP_PORT']
    api_key_file = os.environ['GF_PATHS_DATA'] + "/grafana_api_key"
    history_file = os.environ['GF_PATHS_DATA'] + "/field_history.json"
    reports_directory = "/usr/share/grafana/conf/provisioning/dashboards"
    generated_tag = "generated"
    dashboard = None
    current_id = None
    row = None
    history = None
    apikey = None

    def __init__(self):
        while self.check_api() == False:
            print('Waiting for Grafana API')
            time.sleep(5)

        self.get_api_key()

    def check_api(self):
        # Check if Grafana is alive and healthy
        # This is done by checking for an 'ok' string in the health endpoint response
        # Returns boolean true/false
        req = urllib.request.Request('http://' + self.grafana_url + '/api/health')
        try:
            res = urllib.request.urlopen(req, timeout=5).read()
            data = json.loads(res.decode())
            if data['database'] == 'ok':
                return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass

        return False

    def get_api_key(self):
        # If there's an API key in the env var, we can use that
        if "GF_API_KEY" in os.environ:
            self.apikey = os.environ['GF_API_KEY']
        elif os.path.isfile(self.api_key_file):
            with open(self.api_key_file, 'r') as file:
                self.apikey = file.read()
        else:
            # If there's no key, try to create one using the default credentials

            # there may be an existing key, but we don't have the keyfile for it
            # so let's check and delete any existing key first
            req = urllib.request.Request('http://' + self.grafana_url + '/api/auth/keys')
            base64string = base64.b64encode(bytes('%s:%s' % ('admin', 'admin'),'ascii'))
            req.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
            try:
                res = urllib.request.urlopen(req, timeout=5).read()
                json_result = json.loads(res.decode())
                # for each key returned by the API
                for result in json_result:
                    if result['name'] == "dashboardapikey":
                        key = result['id']
                        # delete the key if it's a dashboard block created one.
                        req = urllib.request.Request('http://' + self.grafana_url + '/api/auth/keys/' + str(key), method='DELETE')
                        req.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
                        res = urllib.request.urlopen(req, timeout=5)
            except(urllib.error.HTTPError, urllib.error.URLError) as ex:
                print('Failed to find keys with exception: ', ex)

            api_key_request = {
                'name': 'dashboardapikey',
                'role': 'Admin'
            }

            api_key_request_json = json.dumps(api_key_request)
            jsondatabytes = api_key_request_json.encode('utf-8') 

            req = urllib.request.Request('http://' + self.grafana_url + '/api/auth/keys', jsondatabytes)
            req.add_header('Accept', 'application/json')
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            req.add_header('Content-Length', len(jsondatabytes))

            req.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))

            try:
                res = urllib.request.urlopen(req, timeout=5).read()
                json_result = json.loads(res.decode())
                if json_result['name'] != "dashboardapikey":
                    return False
            except (urllib.error.HTTPError, urllib.error.URLError) as ex:
                print('Could not generate API key (this is bad)')
                print('Exception: ', ex)
                return False

            self.apikey = json_result['key']

            # Store this for future use
            with open(self.api_key_file, 'w') as self.api_key_file:
                self.api_key_file.write(self.apikey)         

    def clear_history(self, data):
        # clear the history for the specified measurement, allowing the dashboard to be added again
        # note that this also clears the fields
        self.load_history()
        self.history.pop(data['name'], None)
        self.write_history()

    def sync_dashboard(self, data, quiet = False):
        # data contains name and values[]['name']['type']
        if not quiet:
            print('Synchronizing dashboard for ' + data['name'])
        self.load_history()

        if data['name'] in self.history:
            # we've already added this dashboard in the past so just need to add fields that aren't in history
            # load the dashboard from grafana
            if self.load_existing_dashboard(data['name']):
                if not quiet:
                    print('Loaded existing dashboard: ' + data['name'])
            else:
                # we had the dashboard in history but it's not in grafana, so skip
                if not quiet:
                    print('Could not find previously added dashboard ' + data['name'] + '. Skipping.')
                return
        else:
            # this is a new measurement so create a new dashboard for it
            print('Creating new dashboard: ' + data['name'])
            self.create_new_dashboard(data['name'])
            
        for fields in data['values']:
            # check the history file to see if we have done this one already
            # if we have we can skip it
            fieldname = fields[0]
            fieldtype = fields[1]

            if fieldname in self.history[data['name']]:
                if self.history[data['name']][fieldname] == 'added':
                    if not quiet:
                        print('Skipping known field: ' + fieldname)
                    continue

            print('New field found: ' + fieldname + ' (' + fieldtype + ')')
            self.add_field_to_dashboard(fieldname, fieldtype, data['name'])
            self.add_to_history(fieldname, data['name'])

        # store this in grafana
        self.create_update_dashboard()
        self.write_history()

    def load_history(self):
        # Load the history from the file on disk and parse it into the class instance
        with open(self.history_file, 'a+') as history:
            history.seek(0)

            try:
                self.history = json.load(history)
            except json.decoder.JSONDecodeError:
                self.history = {}
                print('Creating new history log')
                pass

    def add_to_history(self, fieldname, measurement):
        self.history.setdefault(measurement, {})
        self.history[measurement].setdefault(fieldname, 'added')

    def write_history(self):
        # Write the history held in the class back to the file on disk for safe keeps
        with open(self.history_file, 'w') as history:
            json.dump(self.history, history)

    def load_existing_dashboard(self,uid):
        # Load the existing dashboard JSON from Grafana, ready to append new panels
        req = urllib.request.Request('http://' + self.grafana_url + '/api/dashboards/uid/' + uid)
        req.add_header('Authorization', 'Bearer ' + self.apikey)
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json; charset=utf-8')

        try:
            res = urllib.request.urlopen(req, timeout=5).read()
            self.dashboard = json.loads(res.decode())['dashboard']
        except (urllib.error.HTTPError, urllib.error.URLError):
            return False
            pass

        # Here we need to find the highest ID existing in the dashboard in order to increment from there
        self.current_id = self.get_highest_dashboard_id()

        return True
        

    def create_new_dashboard(self, measurement):
        with open('templates/dashboard_template.json') as dashboardfile:
            self.dashboard = json.load(dashboardfile)

        self.current_id = 1
        self.dashboard['title'] = stringcase.titlecase(measurement)
        self.dashboard['uid'] = measurement
        self.dashboard['tags'] = [self.generated_tag]

        self.history[measurement] = {}

        # With every new dashboard we add a summary panel first
        self.add_summary_panel_to_dashboard(measurement)


    def add_field_to_dashboard(self, fieldname, fieldtype, measurement):
        # Take the existing dashboard JSON and inject the appropriate panel JSON
        # We are interested in .panels[]
        # Add the panel json to this array, being careful to increment the id
        self.create_row(fieldname)

        # we can take a guess at panel type not only based on field type but name too
        # ie a timestamp might be a float but if it's called timestamp we could show a 'clock' panel or sth
        if fieldtype == "float" or fieldtype == "integer":
            self.add_panel_to_row("stat", fieldname, measurement)
            self.add_panel_to_row("graph", fieldname, measurement)
        elif fieldtype == "string" or fieldtype == "boolean":
            self.add_panel_to_row("textstat", fieldname, measurement)
            self.add_panel_to_row("table", fieldname, measurement)

        self.dashboard['panels'].append(self.row)
        self.row = None

    def add_panel_to_row(self, paneltype, fieldname, measurement):
        newpanel = self.load_panel(paneltype)

        self.current_id = self.current_id + 1
        newpanel['id'] = self.current_id
        newpanel['title'] = self.generate_panel_name(fieldname)

        if paneltype in ['gauge', 'graph', 'stat', 'table', 'textstat']:
            newpanel['targets'][0]['measurement'] = measurement
            newpanel['targets'][0]['alias'] = fieldname
            newpanel['targets'][0]['select'][0][0]['params'][0] = fieldname

        self.row['panels'].append(newpanel)

    def add_summary_panel_to_dashboard(self, measurement):
        self.create_row("Data summary", False)

        newpanel = self.load_panel('summary')
        self.current_id = self.current_id + 1
        newpanel['id'] = self.current_id
        newpanel['title'] = self.generate_panel_name(measurement)
        newpanel['targets'][0]['measurement'] = measurement

        self.dashboard['panels'].append(self.row)
        self.dashboard['panels'].append(newpanel)
        self.row = None


    def create_row(self, title, collapsed = True):
        row = self.load_panel('row')

        self.current_id = self.current_id + 1
        row['id'] = self.current_id
        row['title'] = self.generate_panel_name(title)

        if len(self.dashboard['panels']) > 0:
            row['gridPos']['y'] = self.dashboard['panels'][-1]['gridPos']['y'] + 1

        row['collapsed'] = collapsed

        self.row = row

    # Load the object for the specified fieldtype
    def load_panel(self, paneltype):
        with open('templates/' + paneltype + '_panel_template.json') as panelfile:
            panel = json.load(panelfile)

        return panel

    def generate_panel_name(self, name):
        return stringcase.titlecase(name)


    def create_update_dashboard(self):
        # Send this JSON to Grafana
        # This could be a new dashboard (no ID), or updating an existing one (with ID)
        grafana_dashboard = {
            'dashboard': self.dashboard,
            'folderId': 0,
            'overwrite': True
        }

        dashboardjson = json.dumps(grafana_dashboard)
        jsondatabytes = dashboardjson.encode('utf-8') 

        # Send this to grafana
        # TODO load auth key automatically
        req = urllib.request.Request('http://' + self.grafana_url + '/api/dashboards/db', jsondatabytes)
        req.add_header('Authorization', 'Bearer ' + self.apikey)
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(jsondatabytes))

        try:
            res = urllib.request.urlopen(req, timeout=5)
            return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass

        return False

    def get_highest_dashboard_id(self):
        id_values = self.get_recursively(self.dashboard, 'id')

        return max(id_values)

    def get_recursively(self, search_dict, field):
        fields_found = []

        for key, value in search_dict.items():

            if key == field and isinstance(value, int):
                fields_found.append(value)

            elif isinstance(value, dict):
                results = self.get_recursively(value, field)
                for result in results:
                    if isinstance(result, int):
                        fields_found.append(result)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.get_recursively(item, field)
                        for another_result in more_results:
                            if isinstance(another_result, int):
                                fields_found.append(another_result)

        return fields_found

    def get_provisioning_dash(self):
        # Returns id of first json file in reports_diretory or
        # id of default.json file if it exists, otherwise 0
        found_file = "none"
        list_dir = os.listdir(self.reports_directory)
        list_dir = [f.lower() for f in list_dir]
        list_dir = sorted(list_dir)
        count = 0
        for filename in list_dir:
            if filename.endswith(".json"):
                count = count + 1
                if count == 1:
                    # This is the first json file
                    found_file = filename
                if filename == "default.json":
                    found_file = filename
                    continue

        return_id = 0
        if found_file != "none":
            # Get uid from file
            found_file = open(self.reports_directory + "/" + found_file)
            report_json = json.loads(found_file.read())
            found_file.close()
            found_file = report_json["uid"]
            # Find matching uid in grafana and get id
            req = urllib.request.Request('http://' + self.grafana_url + '/api/search?query=%')
            res = urllib.request.urlopen(req, timeout=5).read()
            data = json.loads(res.decode())
            for result in data:
              if result['uid'] == found_file:
                return_id = result['id']
                continue

        return return_id

    def get_lowest_dashboard_id(self):
        # Returns minimum id of any generated dashboard
        # based on dashboard having a tag (generated_tag)
        req = urllib.request.Request('http://' + self.grafana_url + '/api/search?query=%')
        res = urllib.request.urlopen(req, timeout=5).read()
        data = json.loads(res.decode())
        min_id = 0
        ids = []
        for result in data:
            if self.generated_tag in result['tags']:
                ids.append(result['id'])
        if len(ids) > 0:
            ids.sort
            min_id = ids[0]

        return min_id


    def set_default_dashboard(self, id):
        # Sets the default dashboard to provided id
        default_dashboard = {
            'homeDashboardId': id,
            'theme': "",
            'timezone': ""
        }

        defaultjson = json.dumps(default_dashboard)
        jsondatabytes = defaultjson.encode('utf-8')

        req = urllib.request.Request('http://' + self.grafana_url + '/api/user/preferences', jsondatabytes, method='PUT')
        req.add_header('Authorization', 'Bearer ' + self.apikey)
        req.add_header('Accept', 'application/json')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Content-Length', len(jsondatabytes))

        try:
            res = urllib.request.urlopen(req, timeout=5)
            return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            print(urllib.error)
            pass
            return False

    def get_current_default_dashboard(self):
        # Returns current default dashboard ID
        req = urllib.request.Request('http://' + self.grafana_url + '/api/user/preferences')
        res = urllib.request.urlopen(req, timeout=5).read()
        data = json.loads(res.decode())
        dash = data["homeDashboardId"]

        return dash

    def default_dashboard(self):
        # Routine to set the default dashboard based on opinionated criteria
        x = True
        default_dash = self.get_current_default_dashboard()
        provisioned = self.get_provisioning_dash()
        if provisioned != 0:
            if provisioned != default_dash:
                print("Found provisioned dashboard ID {0} and setting as default.".format(provisioned))
                x = self.set_default_dashboard(provisioned)
        else:
            if default_dash == 0:
                min_dash = self.get_lowest_dashboard_id()
                if min_dash > 0 and min_dash != default_dash:
                    x = self.set_default_dashboard(min_dash)
                    print("Set default dashboard to ID {0}.".format(min_dash))

        if x != True:
            print("Could not set default dashboard.")

        return x
