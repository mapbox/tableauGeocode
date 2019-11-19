# Dockerfile for TabPy
# Setup
FROM centos:7.6.1810
RUN yum -y update
RUN yum install git yum-utils groupinstall development which https://centos7.iuscommunity.org/ius-release.rpm -y
RUN yum install python36u python36u-pip tmux -y

# Python dependencies
RUN python3 -m pip install --upgrade pip 
RUN python3 -m pip install pandas tabpy ratelimit

# Where everything lives
WORKDIR /TabPy
COPY ./geocode.py ./geocode.py
COPY ./startup.sh ./startup.sh
COPY ./tabpy.conf ./tabpy.conf

# Expose port 9004
EXPOSE 80
# Start TabPy
CMD [ "./startup.sh" ]