FROM centos:7

RUN yum -y update && yum clean all
# Install pip
RUN yum install -y python-setuptools gcc
RUN easy_install pip

# Add and install Python modules
RUN yum -y install postgresql-devel python-devel
ADD requirements.txt /twitter-heat/requirements.txt
RUN cd /twitter-heat; pip install -r requirements.txt

# Bundle app source
ADD . /twitter-heat
WORKDIR /twitter-heat

# Expose
EXPOSE  80

# Run
CMD ["/bin/bash", "/twitter-heat/run_all.sh"]
