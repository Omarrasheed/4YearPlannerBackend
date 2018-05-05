FROM python:2.7

RUN mkdir /usr/src/app
RUN git clone https://github.com/Omarrasheed/4YearPlannerBackend.git /usr/src/app

WORKDIR /usr/src/app

RUN pip install git+https://github.com/cuappdev/appdev.py.git --upgrade
RUN pip install -r requirements.txt

EXPOSE 5000
CMD python src/run.py