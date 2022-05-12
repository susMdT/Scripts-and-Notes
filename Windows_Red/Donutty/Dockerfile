FROM scottyhardy/docker-wine
RUN apt update
RUN apt install python3 python3-pip -y
RUN pip install flask

RUN mkdir /donut/
RUN mkdir /donut/serv/
RUN mkdir /donut/files/

COPY ./files /donut/files
COPY ./serv /donut/serv
ADD setup.sh /donut/serv/setup.sh

RUN wineboot
RUN chmod +x /donut/serv/setup.sh
ENTRYPOINT ["/donut/serv/setup.sh"]