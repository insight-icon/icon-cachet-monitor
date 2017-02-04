#!/usr/bin/python
# coding=utf-8

import urllib3
import certifi
import httplib
import time


from utils import Utils

'''
   Copyright 2017 Gareth Williams

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''


class Cachet(object):

    def __init__(self):
        self.utils = Utils()
        self.config = self.utils.readConfig()
        self.base_url = self.config['api_url']
        self.api_token = self.config['api_token']
        self.maxRetries = self.config['retries']

        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.checkSites()

    def checkSites(self):
        # Count how many sites to monitor
        monitor_count = len(self.config['monitoring'])
        x = 0

        cfErrors = {
            520: "Web server is returning an unknown error",
            521: "Web server is down",
            522: "Connection timed out",
            523: "Origin is unreachable",
            524: "A timeout occurred",
            525: "SSL handshake failed",
            526: "Invalid SSL certificate"
        }

        # Loop through sites to monitor
        while x < monitor_count:
            isEnabled = self.config['monitoring'][x]['enabled']
            status_codes = self.config['monitoring'][x]['expected_status_code']
            url = self.config['monitoring'][x]['url']
            request_method = self.config['monitoring'][x]['method']
            c_id = self.config['monitoring'][x]['component_id']
            localtime = time.asctime(time.localtime(time.time()))
            try:
                if isEnabled:
                    r = self.http.request(request_method, url, retries=self.maxRetries, timeout=self.config['monitoring'][x]['timeout'])
            except urllib3.exceptions.SSLError as e:
                incident_id = self.checkForIncident(c_id)
                if not incident_id:
                    c_status = 4
                    error_code = '%s check **failed** - %s \n\n`%s %s SSL Error: %s`' % (url, localtime, request_method, url, e)
                    incident_id = self.checkForIncident(c_id)
                    if not incident_id:
                        self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                                 component_status=c_status)
            except urllib3.exceptions.MaxRetryError as e:
                c_status = 4
                error_code = '%s check **failed** - %s \n\n`%s %s Max Retry Error: %s`' % (url, localtime, request_method, url, e)
                incident_id = self.checkForIncident(c_id)
                if not incident_id:
                    self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                             component_status=c_status)
            except urllib3.exceptions.NewConnectionError as e:
                c_status = 4
                error_code = '%s check **failed** - %s \n\n`%s %s New Connection Error: %s`' % (
                url, localtime, request_method, url, e)
                incident_id = self.checkForIncident(c_id)
                if not incident_id:
                    self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                             component_status=c_status)
            except urllib3.exceptions.HTTPError as e:
                c_status = 4
                error_code = '%s check **failed** - %s \n\n`%s %s HTTP Error: %s`' % (
                    url, localtime, request_method, url, e)
                incident_id = self.checkForIncident(c_id)
                if not incident_id:
                    self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                             component_status=c_status)
            except urllib3.exceptions.HTTPWarning as e:
                c_status = 2
                error_code = '%s check **failed** - %s \n\n`%s %s HTTP Warning: %s`' % (
                    url, localtime, request_method, url, e)
                incident_id = self.checkForIncident(c_id)
                if not incident_id:
                    self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                             component_status=c_status)
            except urllib3.exceptions.ReadTimeoutError as e:
                c_status = 2
                error_code = '%s check **failed** - %s \n\n`%s %s Read Timeout: %s`' % (
                    url, localtime, request_method, url, e)
                incident_id = self.checkForIncident(c_id)
                if not incident_id:
                    self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                             component_status=c_status)
            else:
                if r.status not in status_codes and r.status not in cfErrors:
                    error_code = '%s check **failed** - %s \n\n`%s %s HTTP Error %s: %s`' % (url, localtime, request_method, url, r.status, httplib.responses[r.status])
                    c_status = 4
                    incident_id = self.checkForIncident(c_id)
                    if not incident_id:
                        self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                                 component_status=c_status)
                    current_status = self.getCurrentStatus(c_id)
                    if current_status is not c_status:
                        self.utils.putComponentsByID(c_id, status=c_status)
                elif r.status in cfErrors and r.status not in status_codes:
                    error_code = '%s check **failed** - %s \n\n`%s %s HTTP Error %s: %s`' % (url, localtime, request_method, url, r.status, cfErrors[r.status])
                    c_status = 4
                    incident_id = self.checkForIncident(c_id)
                    if not incident_id:
                        self.utils.postIncidents('%s: HTTP Error' % url, error_code, 1, 1, component_id=c_id,
                                                 component_status=c_status)
                    current_status = self.getCurrentStatus(c_id)
                    if current_status is not c_status:
                        self.utils.putComponentsByID(c_id, status=c_status)
                elif r.status in status_codes:
                    current_status = self.getCurrentStatus(c_id)
                    if current_status is not 1:
                        self.utils.putComponentsByID(c_id, status=1)
                        incident_id = self.checkForIncident(c_id)
                        if incident_id:
                            incident_description = "Resolved at %s\n\n***\n\n%s" % (localtime, self.getIncidentInfo(incident_id))
                            self.utils.putIncidentsByID(incident_id, message=incident_description, status=4, component_id=c_id,
                                                        component_status=1)
            x += 1

    def checkForIncident(self, component_id):
        current_incidents = self.utils.getIncidents().json()
        incidents = len(current_incidents['data'])
        x = 0

        while x < incidents:
            incident_id = current_incidents['data'][x]['id']
            incident_component_id = current_incidents['data'][x]['component_id']
            incident_status = current_incidents['data'][x]['status']

            if component_id == incident_component_id and incident_status is not 4:
                return incident_id
            x += 1

    def getIncidentInfo(self, i_id):
        incident = self.utils.getIncidentsByID(i_id).json()
        i_description = incident['data']['message']
        return i_description

    def getCurrentStatus(self, c_id):
        current_status = self.utils.getComponentsByID(c_id).json()['data']['status']
        return current_status

