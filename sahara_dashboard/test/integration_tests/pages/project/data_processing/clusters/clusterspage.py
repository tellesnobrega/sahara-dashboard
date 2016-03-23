#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack_dashboard.test.integration_tests.regions import forms
from selenium.common.exceptions import NoSuchElementException

from sahara_dashboard.test.integration_tests.pages import basepage
from sahara_dashboard.test.integration_tests.pages import mixins


class ClustersPage(mixins.PluginSelectMixin, mixins.DeleteMixin,
                   basepage.BaseDataProcessingPage):

    TABLE_NAME = "clusters"
    CREATE_FIELD_MAPPING = ('cluster_name', 'description', 'cluster_template',
                            'cluster_count', 'image', 'keypair')

    TABLE_NAME_COLUMN = 'name'

    @property
    def create_form(self):
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.CREATE_FIELD_MAPPING)

    def is_cluster_active(self, name):
        row = self._get_row_with_name(name)
        status_cell = row.cells['status']
        if status_cell.text.startswith('Error'):
            msg = status_cell.text
            try:
                msg = '{}\n{}'.format(
                    msg,
                    status_cell.find_element_by_tag_name('span').get_attribute(
                        'title')
                )
            except NoSuchElementException:
                pass
            raise Exception(msg)
        return status_cell.text == "Active"

    def create(self, plugin_name, plugin_version, name, description=None,
               cluster_template=None, cluster_count=1, image=None,
               keypair=None):
        self.choose_plugin(plugin_name, plugin_version)
        form = self.create_form
        form.cluster_name.text = name
        if description is not None:
            form.description.text = description
        if cluster_template is not None:
            form.cluster_template.text = cluster_template
        form.cluster_count.text = cluster_count
        if image is not None:
            form.image.text = image
        if keypair is not None:
            form.keypair.text = keypair
        form.submit()

    def wait_until_cluster_active(self, name, timeout=None):
        self._wait_until(lambda x: self.is_cluster_active(name),
                         timeout=timeout)

    def wait_until_cluster_deleted(self, name):
        self._wait_until(lambda x: not self.is_present(name))
