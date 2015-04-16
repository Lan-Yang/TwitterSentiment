FROM centos:7

RUN yum -y update && yum clean all
# Install pip
RUN yum install -y python-setuptools gcc python-devel
RUN easy_install pip

# Add and install Python modules
RUN yum -y install pkg-config libffi-devel openssl-devel
ADD requirements.txt /twitter-senti/requirements.txt
RUN cd /twitter-senti; pip install -r requirements.txt

# Bundle app source
ADD . /twitter-senti
WORKDIR /twitter-senti

# Expose
EXPOSE  80

# Run
CMD ["python", "/twitter-senti/application.py"]
