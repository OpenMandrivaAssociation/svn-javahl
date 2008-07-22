%define section         free
%define gcj_support     1

Name:           svn-javahl
Version:        1.4.2
Release:        %mkrel 5
Summary:        Java bindings for Subversion
License:        BSD-style
Group:          Development/Java
URL:            http://subversion.tigris.org/
Source0:        http://subversion.tigris.org/tarballs/subversion-%{version}.tar.bz2
Source1:        http://subversion.tigris.org/downloads/subversion-%{version}.tar.bz2.asc
Patch0:         subversion-1.1.3-java.patch
Patch1:         subversion-1.4.2-latest_neon_is_0.26.2.diff
BuildRequires:  autoconf >= 2.54
BuildRequires:  chrpath
BuildRequires:  db4-devel
BuildRequires:  libtool >= 1.4.2
%if %{mdkversion} < 200610
BuildRequires:  neon-devel >= 0.24.7
%else
BuildRequires:  neon-devel >= 0.26
%endif
BuildRequires:  apache-devel
BuildRequires:  apr-devel >= 1.2.2
BuildRequires:  apr-util-devel >= 1.2.2
BuildRequires:  swig >= 1.3.27
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildRequires:  java-devel
%endif
BuildRequires:  java-rpmbuild
BuildRequires:  junit
Provides:       java-subversion = %{version}-%{release}
Obsoletes:      java-svn
Provides:       java-svn = %{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
This package contains the files necessary to use the subversion
library functions within java scripts.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q -n subversion-%{version}
%patch0 -p1 -b .java
%patch1 -p1 -b .neon
rm -rf neon apr apr-util db4
%{__perl} -pi -e 's/^LINK_JAVAHL_CXX = \$\(LIBTOOL\) \$\(LTCXXFLAGS\) --mode=link \$\(CXX\) \$\(LT_LDFLAGS\)/\
LINK_JAVAHL_CXX = \$\(LIBTOOL\) \$\(LTCXXFLAGS\) --mode=link \$\(CXX\) \$\(LT_LDFLAGS\) -avoid-version/;' \
              -e 's|^javahl_javadir =.*|javahl_javadir = %{_javadir}|g;' \
  Makefile.in

%build
./autogen.sh

export CFLAGS="-fPIC -I%{java_home}/include"
export CXXFLAGS="-fPIC -I%{java_home}/include"

# both versions could be installed, use the latest one per default
if [ -x %{_bindir}/apr-config ]; then APR=%{_bindir}/apr-config; fi
if [ -x %{_bindir}/apu-config ]; then APU=%{_bindir}/apu-config; fi

if [ -x %{_bindir}/apr-1-config ]; then APR=%{_bindir}/apr-1-config; fi
if [ -x %{_bindir}/apu-1-config ]; then APU=%{_bindir}/apu-1-config; fi

%{configure2_5x} \
   --with-apxs=%{_sbindir}/apxs \
   --with-apr=$APR \
   --with-apr-util=$APU \
   --disable-mod-activation \
   --with-swig=%{_prefix} \
   --disable-static \
   --with-jdk=%{java_home} \
   --with-junit=%{_javadir}/junit.jar \
   --enable-shared 
%{make} javahl_javadir=%{_javadir}
%{make} javahl javahl_javadir=%{_javadir}

pushd subversion/bindings/java/javahl/src
%{__mkdir_p} ../javadoc && %{javadoc} -d ../javadoc org.tigris.subversion
popd

%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install
%{__make} DESTDIR=%{buildroot} install-javahl

%{__rm} -rf %{buildroot}{%{_bindir},%{_datadir}/locale,%{_includedir},%{_mandir}}
%{__rm} -rf %{buildroot}%{_libdir}{apache,svn-javahl}
%{__rm} -f %{buildroot}%{_libdir}/libsvnjavahl-1.la
%{_bindir}/find %{buildroot}%{_libdir} ! -type d ! -name '*javahl*' | %{_bindir}/xargs -t %{__rm}

%{__mv} %{buildroot}%{_javadir}/svn-javahl.jar %{buildroot}%{_javadir}/svn-javahl-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)

%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a subversion/bindings/java/javahl/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%{_bindir}/chrpath -d %{buildroot}%{_libdir}/libsvnjavahl-1.so

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%if 0
%check
export CLASSPATH=$(%{_bindir}/build-classpath junit):%{buildroot}%{_javadir}/%{name}.jar:`pwd`/subversion/bindings/java/javahl/src
%{java} -Djava.library.path=%{buildroot}%{_libdir} org.tigris.subversion.javahl.tests.BasicTests
%endif

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%post javadoc
%{__rm} -f %{_javadocdir}/%{name}
%{__ln_s} %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ $1 -eq 0 ]; then
  %{__rm} -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%doc COPYING subversion/bindings/java/README
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%attr(0755,root,root) %{_libdir}/libsvnjavahl-1.so
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%ghost %doc %{_javadocdir}/%{name}


