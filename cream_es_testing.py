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

import subprocess, shlex, time, re, os, datetime, random, string




class _error(Exception):
        def __init__(self,string):
                self.string = string
        def __str__(self):
                return str(self.string)
##############################################################################################################################
##############################################################################################################################
def create_proxy(password, vo, cert=None, key=None, time=None):
        '''
                |  Description:  |  Create a user proxy.                                        |\n
                |  Arguments:    |  password  |  the user's proxy password                      |
                |                |  vo        |  for the voms extention.                        |
                |                |  cert      |  non standard certificate path                  |
                |                |  key       |  non standard key path                          |
                |                |  time      |  the validity period of the proxy. Form: HH:MM  |\n
                |  Returns:      |  nothing.                                                    |
        '''


        com = "/usr/bin/voms-proxy-init -pwstdin --voms %s" % vo

        if cert != None and key != None:
                com = com + ' -cert ' + cert + ' -key ' + key
        if time != None:
                pattern = "\d\d\:\d\d"
                match = re.search(pattern,time)
                if match:
                        com = com + ' -valid ' + time
                else:
                        raise _error("Wrong time format for proxy creation! It must be in the form HH:MM")

        if (cert != None and key == None) or (cert == None and key != None):
                raise _error("Wrong arguments for proxy creation: " + password + " " + vo + " " + cert + " " + key)

        args = shlex.split(com.encode('ascii'))
        p = subprocess.Popen( args , shell=False , stderr=subprocess.STDOUT , stdout=subprocess.PIPE , stdin=subprocess.PIPE)
        (outData,inData)=p.communicate(input=password)

        retVal=p.wait()

        #output = outFP.read()

        print 'Command "' + com + '" output follows:'
        print outData

        if retVal != 0 :
                if retVal == 1 :
                        raise _error("Proxy creation failed.Most probably wrong Virtual Organisation was given.")
                elif retVal == 3 :
                        raise _error("Proxy creation failed.Most probably the password provided was not valid.")
                else :
                        raise _error("Proxy creation failed.Reason: Unknown.")
##############################################################################################################################
##############################################################################################################################
def check_proxy(time_left=None):
        '''
                |  Description:  |  Check whether the proxy exists and if it has any time left.                                                  |\n
                |  Arguments:    |  Without any arguments,it checks if the proxy exists and has any time left                                    |
                |                |  With one argument,it checks if the proxy exists and has greater than or equal to the requested time left.    |\n
                |  Returns:      |  nothing                                                                                                      |
        '''

	if os.environ.has_key("X509_USER_PROXY") == False :
		raise _error("Proxy path env. var not set")

	if os.path.exists(os.environ["X509_USER_PROXY"]) == False :
		raise _error("Proxy file not present or inaccessible")

	com="/usr/bin/voms-proxy-info -timeleft"
	args = shlex.split(com.encode('ascii'))
	p = subprocess.Popen( args , shell=False , stderr=subprocess.STDOUT , stdout=subprocess.PIPE )
	fPtr=p.stdout
	proxy_timeleft=int(fPtr.readline())

        if time_left == None:
        	if proxy_timeleft <= 0 :
	        	raise _error("No proxy time left")
        else:
                if proxy_timeleft <= int(time_left) :
	        	raise _error("Proxy has less time than requested (%s seconds) left" % time_left)
##############################################################################################################################
##############################################################################################################################
def destroy_proxy():
        '''
                |  Description:  |  Delete a user's proxy.  | \n
                |  Arguments:    |  none.                   | \n
                |  Returns:      |  nothing.                |
        '''

        com="/usr/bin/voms-proxy-destroy"
        args = shlex.split(com.encode('ascii'))
        p = subprocess.Popen( args , shell=False , stderr=subprocess.STDOUT , stdout=subprocess.PIPE )
        fPtr=p.stdout

        retVal=p.wait()

        output=fPtr.readlines()

        if retVal != 0 :
		raise _error("Proxy destroy operation failed with return value: " + str(p.returncode) + " \nCommand reported: " +  ','.join(output) )
##############################################################################################################################
##############################################################################################################################
def execute_command(com):
        '''
                |  Description:   |  Runs the given command through the subprocess module                          | \n
                |  Arguments:     |  com     |  a string with the command and its arguments                        | \n
                |  Returns:       |  (int,str) tuple, containing the returnValue and the output of the command     |
        '''

        args = shlex.split(com.encode('ascii'))
        p = subprocess.Popen( args , stderr=subprocess.STDOUT , stdout=subprocess.PIPE )
        fPtr=p.stdout
        retVal=p.wait()
        output=fPtr.read()

        return (retVal, output)
##############################################################################################################################
##############################################################################################################################
def _ec(s):
        # convenience method for execute_command
        return execute_command(s)
##############################################################################################################################
##############################################################################################################################
def es_delegate_proxy(ep):
        '''
                |  Description:   |  Execute the glite-es-delegate-proxy command on the given endpoint             | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )      | \n
                |  Returns:       |  the delegation id or raises error                                             |
        '''

        com='/usr/bin/glite-es-delegate-proxy -d -e ' + ep
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output

                for line in output.split('\n'):
                        if 'DelegationID' in line:
                                did = line.split('=')[1].strip()
                                return did
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_delegation_info(ep,did,time=False):
        '''
                |  Description:   |  Execute the glite-es-delegation-info command on the given endpoint             | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )       |
                |                 |  did    |  the delegation id                                                    | 
                |                 |  time   |  if set to True, the time remaining is instead returned               | \n
                |  Returns:       |  the command's output or the time remaining (in seconds)                        |
        '''

        com='/usr/bin/glite-es-delegation-info -d -e ' + ep + ' ' + did
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output

                if time:
                        for line in output.split('\n'):
                                if "Lifetime" in line:
                                        end = line.split('=')[1].strip()

                        now  = datetime.datetime.now().strftime('%c')
                        d1   = datetime.datetime.strptime(end,'%c')
                        d2   = datetime.datetime.strptime(now,'%c')
                        diff = d1-d2
                        secs_left = (diff.microseconds + (diff.seconds + diff.days * 24 * 3600) * 10**6) / 10**6

                        return secs_left
                else:
                        return output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_delegation_renew(ep,did):
        '''
                |  Description:   |  Renew a delegation with glite-es-delegation-renew                              | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )       |
                |                 |  did    |  the delegation id                                                    | \n
                |  Returns:       |  the command's output                                                           |
        '''
        com='/usr/bin/glite-es-delegation-renew -d -e ' + ep + ' ' + did
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output
                return output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_create(ep,adl,retOut=False):
        '''
                |  Description:   |  Submit the activity described in the file adl to the endpoint ep               | \n
                |  Arguments:     |  ep      |  the endpoint on which to run the command  (format: host:port )      |
                |                 |  adl     |  path to adl file                                                    |
                |                 |  retOut  |  if set to True, the output will also be returned                    | \n
                |  Returns:       |  the submitted aid  and possibly the command's output                           |
        '''

        com='/usr/bin/glite-es-activity-create -d -e ' + ep + ' ' + adl
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output

                aid='notset'
                for line in output.split('\n'):
                        if 'ActivityID' in line:
                                aid = line.split('=')[1].strip()
                                break

                if retOut == True or retOut=='True':
                        return (aid,output)
                else:
                        return aid
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_multi_activity_create(ep,adl):
        '''
                |  Description:   |  Submit a multiple activity described in the file adl to the endpoint ep        | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )       |
                |                 |  adl    |  path to adl file                                                     | \n
                |  Returns:       |  list of aids                                                                   |
        '''

        com='/usr/bin/glite-es-activity-create -d -e ' + ep + ' ' + adl
        (retVal,output) = _ec(com)

        aids=[]
        if retVal == 0:
                for line in output.split('\n'):
                        if 'ActivityID' in line:
                                aid = line.split('=')[1].strip()
                                aids.append(aid)
                return aids
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_current_status(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-status command on the given endpoint               | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )         |
                |                 |  aid    |  the activity id                                                        | \n
                |  Returns:       |  the activity's status and attributes                                             |
        '''

        com='/usr/bin/glite-es-activity-status -d -e ' + ep + ' ' + aid
        (retVal,output) = _ec(com)

        if retVal == 0:
                for line in output.split('\n'):
                        if 'Status' in line and '=' in line:
                                status = line.split('=')[1].strip()
                for line in output.split('\n'):
                        if 'Attributes' in line and '=' in line:
                                attrs = line.split('=')[1].split('{')[1].split('}')[0].strip()

                return (status,attrs)
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)

        #at this point, no error occured, but the status hasn't been determined, so raise error
        raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_multi_activity_current_status(ep,aids):
        '''
                |  Description:   |  Execute the glite-es-activity-status command on the given endpoint for multiple aids | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )             |
                |                 |  aids   |  a list of aids                                                             | \n
                |  Returns:       |  two lists with statuses and attributes, in correct order                             |
        '''

        s=''
        for aid in aids:
                s = s+ ' ' + aid

        com='/usr/bin/glite-es-activity-status -d -e ' + ep + ' ' + s
        (retVal,output) = _ec(com)

        statuses=[]
        attributes=[]
        if retVal == 0:
                for line in output.split('\n'):
                        if 'Status' in line and '=' in line:
                                status = line.split('=')[1].strip()
                                statuses.append(status)
                for line in output.split('\n'):
                        if 'Attributes' in line and '=' in line:
                                attrs = line.split('=')[1].strip()
                                attributes.append(attrs)

                return (statuses,attributes)
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)

        #at this point, no error occured, but the status hasn't been determined, so raise error
        raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_final_status(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-info command on the given endpoint and wait until  |
                |                 |  the job has reached TERMINAL status                                              | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )         |
                |                 |  aid    |  the activity id                                                        | \n
                |  Returns:       |  the activity's status (normaly TERMINAL) and attributes                          |
        '''

        (status, attrs) = es_activity_current_status(ep,aid)
        while status != 'TERMINAL':
                time.sleep(5)
                (status, attrs) = es_activity_current_status(ep,aid)

        return (status,attrs)
##############################################################################################################################
##############################################################################################################################
def es_activity_info(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-info command on the given endpoint for this aid  | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )       |
                |                 |  aid    |  the activity id                                                      | \n
                |  Returns:       |  the activity's info                                                            |
        '''

        com='/usr/bin/glite-es-activity-info -d -e ' + ep + ' ' + aid
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output
                return output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_list(ep,fMax=None, fFrom=None, fTo=None, fState=None):
        '''
                |  Description:   |  Execute the glite-es-activity-list command on the given endpoint,               |
                |                 |  using the specified filters.                                                    | \n
                |  Arguments:     |  ep      |  the endpoint on which to run the command  (format: host:port )       |
                |                 |  fMax    |  the maximum returned entries filter                                  |
                |                 |  fFrom   |  FROM YYYY-MM-DD HH:mm:ss date filter                                 |
                |                 |  fTo     |  TO YYYY-MM-DD HH:mm:ss date filter                                   |
                |                 |  fState  |  Sets the status/status-attrs filter: each status/status-attr is      |
                |                 |          |  a string in this format <STATUS>[:<STATUS_ATTRIBUTE>]; multiple      |
                |                 |          |  status/status-attr items can be separated by ',' and are OR'ed by    |
                |                 |          |  the service when it tries to selects activities to return.           |
                |                 |          |  Example: TERMINAL,PREPROCESSING:VALIDATING,TERMINAL:APP_FAILURE      |
                |                 |          |  Check corresponding man page for relevant statuses and attributes.   | \n
                |  Returns:       |  list of aid(s)                                                                  |
        '''

        rest = ''
        if fMax != None:
                rest += ' -l ' + str(fMax) + ' '
        if fFrom != None:
                pattern = "\d\d\d\d\-\d\d\-\d\d\s\d\d\:\d\d\:\d\d"
                match = re.search(pattern,fFrom)
                if not match:
                        raise _error("Invalid FROM filter datetime argument: " + fFrom \
                        + " .Should have format: YYYY-MM-DD hh:mm:ss")
                else:
                        rest += ' -F \''+fFrom+'\' '
        if fTo != None:
                pattern = "\d\d\d\d\-\d\d\-\d\d\s\d\d\:\d\d\:\d\d"
                match = re.search(pattern,fTo)
                if not match:
                        raise _error("Invalid FROM filter datetime argument: " + fTo \
                        + " .Should have format: YYYY-MM-DD hh:mm:ss")
                else:
                        rest += ' -T \''+fTo+'\' '
        if fState != None:
                rest += ' -S' + fState + ' '

        com='/usr/bin/glite-es-activity-list -d -e ' + ep + ' ' + rest
        (retVal,output) = _ec(com)

        if retVal == 0:
                host = ep.split(':')[0]
                index = 0
                for line in output.split('\n'):
                        if host in line:
                                break
                        index += 1

                # this kinda obscure thing means: return a comma separated string of all the values in output.split('\n')
                # after index+1 item and if the item striped of whitespaces has positive length
                #return ','.join([i for i in output.split('\n')[index+1:] if len(i.strip()) > 0 ])
                retList = [i for i in output.split('\n')[index+1:] if len(i.strip()) > 0 ]
                print retList
                return retList
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_pause(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-pause command on the given endpoint for this aid  | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )        |
                |                 |  aid    |  the activity id                                                       | \n
                |  Returns:       |  nothing or error                                                                |
        '''

        com='/usr/bin/glite-es-activity-pause -d -e ' + ep + ' ' + aid
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_resume(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-resume command on the given endpoint for this aid  | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )         |
                |                 |  aid    |  the activity id                                                        | \n
                |  Returns:       |  nothing or error                                                                 |
        '''

        com='/usr/bin/glite-es-activity-resume -d -e ' + ep + ' ' + aid
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_cancel(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-cancel command on the given endpoint for this aid  | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )         |
                |                 |  aid    |  the activity id                                                        | \n
                |  Returns:       |  nothing or error                                                                 |
        '''

        com='/usr/bin/glite-es-activity-cancel -d -e ' + ep + ' ' + aid
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def es_activity_wipe(ep,aid):
        '''
                |  Description:   |  Execute the glite-es-activity-wipe command on the given endpoint for this aid   | \n
                |  Arguments:     |  ep     |  the endpoint on which to run the command  (format: host:port )        |
                |                 |  aid    |  the activity id                                                       | \n
                |  Returns:       |  nothing or error                                                                |
        '''

        com='/usr/bin/glite-es-activity-wipe -d -e ' + ep + ' ' + aid
        (retVal,output) = _ec(com)

        if retVal == 0:
                print output
        else:
                raise _error('Command:"' + com + '" failed with return value ' + str(retVal) + ' and output:\n' + output)
##############################################################################################################################
##############################################################################################################################
def sleep_adl(queue,secs, output_dir):
        '''
                |  Description: |   Simple adl file.Executes /bin/sleep for the defined number of seconds.      | \n
                |  Arguments:   |   queue        |   the queue to submit the activity                           |
                |               |   secs         |   seconds to sleep                                           |
                |               |   output_dir   |   the directory to put the file in                           | \n
                |  Returns:     |   Temporary file name.                                                        |
        '''

        folder = output_dir
        identifier = 'sleep' + str(secs)
        tmp1 = str(time.time())
        tmp2 = ''.join(random.choice(string.letters) for i in xrange(5))
        name = 'cream_es_testing-' + tmp1 + '-' + tmp2 + '-' + identifier + '.adl'
        path = folder + '/' + name

        adl_file = open(path,'w')

        adl_contents =  '<ActivityDescription>\n'\
                        '\t<ActivityIdentification>\n'\
                        '\t\t<Name>sleep'+str(secs)+'</Name>\n'\
                        '\t\t<Description>sleep '+str(secs)+'</Description>\n'\
                        '\t\t<Type>single</Type>\n'\
                        '\t</ActivityIdentification>\n'\
                        '\t<Application>\n'\
                        '\t\t<Executable>\n'\
                        '\t\t\t<Path>/bin/sleep</Path>\n'\
                        '\t\t\t<Argument>'+str(secs)+'</Argument>\n'\
                        '\t\t</Executable>\n'\
                        '\t</Application>\n'\
                        '\t<Resources>\n'\
                        '\t\t<QueueName>'+queue+'</QueueName>\n'\
                        '\t</Resources>\n'\
                        '</ActivityDescription>\n'


        adl_file.write(adl_contents)
        adl_file.close()

        return path
##############################################################################################################################
##############################################################################################################################
def sleep_failif_ne_adl(queue,secs, output_dir,failif_exitcode_ne=None):
        '''
                |  Description: |   Simple adl file, using the FailIfExitCodeNotEqualTo tag.                            |
                |               |   Executes /bin/sleep for the defined number of seconds.                              | \n
                |  Arguments:   |   queue                |   the queue to submit the activity                           |
                |               |   secs                 |   seconds to sleep                                           |
                |               |   output_dir           |   the directory to put the file in                           |
                |               |   failif_exitcode_ne   |   the FailIfExitCodeNotEqualTo argument (ignore if None)     | \n
                |  Returns:     |   Temporary file name.                                                                |
        '''

        folder = output_dir
        identifier = 'sleep' + str(secs) + '-failif_ne'
        tmp1 = str(time.time())
        tmp2 = ''.join(random.choice(string.letters) for i in xrange(5))
        name = 'cream_es_testing-' + tmp1 + '-' + tmp2 + '-' + identifier + '.adl'
        path = folder + '/' + name

        if failif_exitcode_ne != None:
                s = '<FailIfExitCodeNotEqualTo>'+str(failif_exitcode_ne)+'</FailIfExitCodeNotEqualTo>'
        else:
                s = ' '

        adl_file = open(path,'w')

        adl_contents =  '<ActivityDescription>\n'\
                        '\t<ActivityIdentification>\n'\
                        '\t\t<Name>sleep'+str(secs)+'</Name>\n'\
                        '\t\t<Description>sleep '+str(secs)+'</Description>\n'\
                        '\t\t<Type>single</Type>\n'\
                        '\t</ActivityIdentification>\n'\
                        '\t<Application>\n'\
                        '\t\t<Executable>\n'\
                        '\t\t\t<Path>/bin/sleep</Path>\n'\
                        '\t\t\t<Argument>'+str(secs)+'</Argument>\n'\
                        '\t\t\t' + s + '\n'\
                        '\t\t</Executable>\n'\
                        '\t</Application>\n'\
                        '\t<Resources>\n'\
                        '\t\t<QueueName>'+queue+'</QueueName>\n'\
                        '\t</Resources>\n'\
                        '</ActivityDescription>\n'


        adl_file.write(adl_contents)
        adl_file.close()

        return path
##############################################################################################################################
##############################################################################################################################
def multi_adl(queue,secs, output_dir):
        '''
                |  Description: |   Multi adl file.Executes /bin/sleep for the defined number of seconds.       | \n
                |  Arguments:   |   queue        |   the queue to submit the activity                           |
                |               |   secs         |   seconds to sleep                                           |
                |               |   output_dir   |   the directory to put the file in                           | \n
                |  Returns:     |   Temporary file name.                                                        |
        '''

        folder = output_dir
        identifier = 'multi_sleep' + str(secs)
        tmp1 = str(time.time())
        tmp2 = ''.join(random.choice(string.letters) for i in xrange(5))
        name = 'cream_es_testing-' + tmp1 + '-' + tmp2 + '-' + identifier + '.adl'
        path = folder + '/' + name

        adl_file = open(path,'w')

        adl_contents =  '<CreateActivities>\n'\
                        '\t<ActivityDescription>\n'\
                        '\t\t<ActivityIdentification>\n'\
                        '\t\t\t<Name>sleep'+str(secs)+'</Name>\n'\
                        '\t\t\t<Description>sleep '+str(secs)+'</Description>\n'\
                        '\t\t\t<Type>single</Type>\n'\
                        '\t\t</ActivityIdentification>\n'\
                        '\t\t<Application>\n'\
                        '\t\t\t<Executable>\n'\
                        '\t\t\t\t<Path>/bin/sleep</Path>\n'\
                        '\t\t\t\t<Argument>'+str(secs)+'</Argument>\n'\
                        '\t\t\t</Executable>\n'\
                        '\t\t</Application>\n'\
                        '\t\t<Resources>\n'\
                        '\t\t\t<QueueName>'+queue+'</QueueName>\n'\
                        '\t\t</Resources>\n'\
                        '\t</ActivityDescription>\n'\
                        '\t<ActivityDescription>\n'\
                        '\t\t<ActivityIdentification>\n'\
                        '\t\t\t<Name>sleep'+str(secs)+'</Name>\n'\
                        '\t\t\t<Description>sleep '+str(secs)+'</Description>\n'\
                        '\t\t\t<Type>single</Type>\n'\
                        '\t\t</ActivityIdentification>\n'\
                        '\t\t<Application>\n'\
                        '\t\t\t<Executable>\n'\
                        '\t\t\t\t<Path>/bin/sleep</Path>\n'\
                        '\t\t\t\t<Argument>'+str(secs)+'</Argument>\n'\
                        '\t\t\t</Executable>\n'\
                        '\t\t</Application>\n'\
                        '\t\t<Resources>\n'\
                        '\t\t\t<QueueName>'+queue+'</QueueName>\n'\
                        '\t\t</Resources>\n'\
                        '\t</ActivityDescription>\n'\
                        '</CreateActivities>\n'


        adl_file.write(adl_contents)
        adl_file.close()

        return path
##############################################################################################################################
##############################################################################################################################
def unsupported_capabillity_adl(queue,output_dir,optional=None):
        '''
                |  Description: |   Simple adl file, specifying an unsupported attribute.                       | \n
                |  Arguments:   |   queue        |   the queue to submit the activity                           |
                |               |   output_dir   |   the directory to put the file in                           |
                |               |   optional     |   the optional value for the capabillity being tested        |
                |               |                |   (either true, false or none(not present)                   | \n
                |  Returns:     |   Temporary file name.                                                        |
        '''

        folder = output_dir
        identifier = 'unsupported_capabillity'
        tmp1 = str(time.time())
        tmp2 = ''.join(random.choice(string.letters) for i in xrange(5))
        name = 'cream_es_testing-' + tmp1 + '-' + tmp2 + '-' + identifier + '.adl'
        path = folder + '/' + name

        end_tag = '</RemoteLogging>'    #the end tag is always the same
        if optional != None:
                if optional == 'true' or optional == 'True':
                        s = '<RemoteLogging optional="true">'
                elif optional == 'false' or optional == 'False':
                        s = '<RemoteLogging optional="false">'
        else:
                s = '<RemoteLogging>'

        adl_file = open(path,'w')

        adl_contents =  '<ActivityDescription>\n'\
                        '\t<ActivityIdentification>\n'\
                        '\t\t<Name>uname</Name>\n'\
                        '\t\t<Description>uname</Description>\n'\
                        '\t\t<Type>single</Type>\n'\
                        '\t</ActivityIdentification>\n'\
                        '\t<Application>\n'\
                        '\t\t<Executable>\n'\
                        '\t\t\t<Path>/bin/sleep</Path>\n'\
                        '\t\t\t<Argument>-a</Argument>\n'\
                        '\t\t</Executable>\n'\
                        '\t\t'+s+'\n'\
                        '\t\t\t<ServiceType>LB</ServiceType>\n'\
                        '\t\t\t<URL>https://localloger.com</URL>\n'\
                        '\t\t'+end_tag+'\n'\
                        '\t</Application>\n'\
                        '\t<Resources>\n'\
                        '\t\t<QueueName>'+queue+'</QueueName>\n'\
                        '\t</Resources>\n'\
                        '</ActivityDescription>\n'


        adl_file.write(adl_contents)
        adl_file.close()

        return path
##############################################################################################################################
##############################################################################################################################
def diff_seconds(t1,t2,tolerance=0):
        '''
                |  Description: |   calculate difference of t1 from t2, in seconds                               | \n
                |  Arguments:   |   t1          |   a timestamp in seconds                                       |
                |               |   t2          |   a timestamp in seconds                                       |
                |               |   tolerance   |   the maximum difference between the two timestamps            | \n
                |  Returns:     |   diff in seconds                                                              |
        '''

        t1=int(t1) ; t2=int(t2) ; tolerance=int(tolerance)
        if t2-t1 > tolerance:
                raise _error('Timestamps difference greater than tolerance!(' + str(t2-t1) + ')')

##############################################################################################################################
##############################################################################################################################
def extract_error_from_activity_submit(s):
        '''
                |  Description: |   calculate difference of t1 from t2, in seconds                               | \n
                |  Arguments:   |   s          |   activity submit output                                        | \n
                |  Returns:     |   error message (may be empty)                                                 |
        '''

        for line in s.split('\n'):
                if 'FAULT' in line:
                        error_message = line.split('[')[1].split(']')[0]
                        return error_message
##############################################################################################################################
##############################################################################################################################
def execute_uberftp_command(uberftp_command, gridftp_server, gridftp_path):
        '''
                |  Description: |    Execute an uberftp command on a gridftp url                               | \n
                |  Arguments:   |    uberftp_command    |     one of cat,chgrp,chmod,dir,ls,mkdir,             |
                |               |                       |     rename,rm,rmdir,size,stage                       |
                |               |    gridftp_server     |     the gridftp server hostname                      |
                |               |    gridftp_path       |     the path in the gridftp server                   | \n
                |  Returns:     |    The output of the command                                                 |
        '''

        valid_commands = "cat chgrp chmod dir ls mkdir rename rm rmdir size stage"

        if uberftp_command not in valid_commands:
                raise _error("Invalid uberftp command given: " + uberftp_command)

        com="uberftp -" + uberftp_command + " gsiftp://" + gridftp_server + gridftp_path
	args = shlex.split(com.encode('ascii'))

        p = subprocess.Popen( args , stderr=subprocess.STDOUT , stdout=subprocess.PIPE )
        fPtr=p.stdout

        output=fPtr.read()

        p.wait()

        if p.returncode != 0:
                raise _error('Uberftp command "' + com + '" failed with return code: ' + str(p.returncode) + ' \nCommand reported: ' +  output)

        print 'Uberftp command "' + com + '" output follows:'
        print output

        return output
##############################################################################################################################
##############################################################################################################################
def get_activity_sb(ep,aid):
        '''
                |  Description:  |  Find the gridftp url of the ISB of the given job                  | \n
                |  Arguments:    |  aid             |       activity id returned by submit operation  | \n
                |                |  ep              |       enpoint                                   |
                |  Returns:      |  (gridftp server, gridftp path)                                    |
        '''

        info=es_activity_info(ep,aid)

        try:
                url='notset'
                l = info.split('\n')
                for line in l:
                        if "STAGE_IN_URI" in line:
                                url= l[l.index(line)+1].split('=')[1].strip()
        finally:
                if url=='notset' or len(url) == 0:
                        raise _error('Could not determine the activity\'s sandbox')


        split_list = url.split('/')
        server = split_list[2] #split_list[1] is an empty string, since it splits '//' on '/'

        path = ''
        for i in range(3,len(split_list)):
                path += '/' + split_list[i]

        return (server,path)
##############################################################################################################################
##############################################################################################################################
