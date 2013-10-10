Summary: Testing library and test suite for cream execution service
Name: cream_es_test
Version: 1.0.el6
Release: 1
Source0: cream_es_test-1.0.el6.tar.gz
License: GPLv3
Group: GroupName
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot
Requires: uberftp glite-ce-cream-cli pexpect robotframework
%description
This is the python testing module and the test suite to use
along robot framework,in order to execute a functionality
test for CREAM ES.Documentation is also provided with this
package. Packaged for SL6 versions.
%prep
%setup -q
%build
%install
install -m 0755 -d $RPM_BUILD_ROOT/opt/cream_es_test
install -m 0755 -d $RPM_BUILD_ROOT/opt/cream_es_test/docs
install -m 0755 -d $RPM_BUILD_ROOT/opt/cream_es_test/lib
install -m 0755 -d $RPM_BUILD_ROOT/opt/cream_es_test/testsuite
install -m 0755 cream_es_testing.py $RPM_BUILD_ROOT/opt/cream_es_test/lib/cream_es_testing.py
install -m 0755 vars_es.py $RPM_BUILD_ROOT/opt/cream_es_test/lib/vars_es.py
install -m 0755 cream_es_test_suite.html $RPM_BUILD_ROOT/opt/cream_es_test/testsuite/cream_es_test_suite.html
install -m 0755 cream_es_test.7.gz $RPM_BUILD_ROOT/opt/cream_es_test/docs/cream_es_test.7.gz
install -m 0755 cream_es_testing_keywords.html $RPM_BUILD_ROOT/opt/cream_es_test/docs/cream_es_testing_keywords.html
install -m 0755 cream_es_testing_libdoc.html $RPM_BUILD_ROOT/opt/cream_es_test/docs/cream_es_testing_libdoc.html
install -m 0755 Cream_Es_Test_Suite-doc.html $RPM_BUILD_ROOT/opt/cream_es_test/docs/Cream_Es_Test_Suite-doc.html
install -m 0755 COPYING $RPM_BUILD_ROOT/opt/cream_es_test/docs/COPYING
install -m 0755 CHANGELOG $RPM_BUILD_ROOT/opt/cream_es_test/docs/CHANGELOG
%clean
rm -rf $RPM_BUILD_ROOT
%post
cp $RPM_BUILD_ROOT/opt/cream_es_test/docs/cream_es_test.7.gz /usr/share/man/man7/cream_es_test.7.gz
echo " "
echo "Package cream_es_test installed succesfully!"
%files
%dir /opt/cream_es_test
%dir /opt/cream_es_test/lib
%dir /opt/cream_es_test/docs
%dir /opt/cream_es_test/testsuite
/opt/cream_es_test/lib/cream_es_testing.py
/opt/cream_es_test/lib/vars_es.py
/opt/cream_es_test/testsuite/cream_es_test_suite.html
/opt/cream_es_test/docs/cream_es_test.7.gz
/opt/cream_es_test/docs/cream_es_testing_keywords.html
/opt/cream_es_test/docs/cream_es_testing_libdoc.html
/opt/cream_es_test/docs/Cream_Es_Test_Suite-doc.html
/opt/cream_es_test/docs/COPYING
/opt/cream_es_test/docs/CHANGELOG
