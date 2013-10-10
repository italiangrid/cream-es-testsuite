# Copyright 2012 Dimosthenes Fioretos dfiore -at- noc -dot- edunet -dot- gr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# The cream endpoint to be used (e.g.: ctb04.gridctb.uoa.gr:8443 )
ce_endpoint=""

# The cream queue to be used (e.g.: see )
queue=""

# The user's submitting the jobs virtual organisation (e.g.: see )
vo=""

# The user's submitting the jobs proxy password (e.g.: p4sSw0rD )
proxy_pass=""

# The log level used during the test.Default is INFO.For extra output,set to DEBUG or TRACE.
# (possible values: NONE FAIL WARN INFO DEBUG TRACE)
log_level=""

# Delete temporary files (jdl and script files created during the test) or not. Possible values: True False. Defaults to "True"
delete_files=""

# The path in which temporary files will reside.
# They will be automatically cleaned up unless you set the variable delete_files to "False" or explicitely don't run the cleanup test case.
# The path will be created -with its parents-, it doesn't have to exist. You can leave it empty and a temporary directory will be created for you.
# In order to know which temp random directory is used, it is printed in standard output and in the final test suite report.
# Warning: any parent directories created, are not removed! 
# All in all, unless needed for specific reasons, you should leave this variable empty.
tmp_dir=""


#########################################
#
# Variable checking/setting code follows.
# Do not edit. (unless you know what and why you are doing it!)
#
#########################################

import os as _os       # underscored libs aren't included into rf when the module itself is loaded
import tempfile as _tf # same as above

# do not change this variable
ce=ce_endpoint

class _error(Exception):
	def __init__(self,string):
		self.string = string
	def __str__(self):
		return str(self.string)

if tmp_dir == "" or tmp_dir[0] != '/' or tmp_dir == "/tmp" or tmp_dir == "/tmp/":
        tmp_dir = _tf.mkdtemp(suffix=".cream_testing", dir="/tmp/") + '/'
else:
        if tmp_dir[-1] != '/':
                tmp_dir += '/'
        _os.system("mkdir -p " + tmp_dir) #this should work under normal circumstances,the code here is kept minimal after all.

print "INFO: The files of this testsuite will be stored under: " + tmp_dir
#outputdata_dir = tmp_dir + 'outputdata'
#_os.system("mkdir -p " + outputdata_dir) #this should work under normal circumstances, the code here is kept minimal after all.

ce_host=ce_endpoint.split(":")[0] #helper
