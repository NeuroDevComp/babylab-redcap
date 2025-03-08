
FROM python:3.12

WORKDIR /babylab

RUN python -m pip install --upgrade pip
RUN python -m pip install flask python-dotenv babylab 

RUN export FLASK_RUN_PORT=5000
CMD [ "python", "-m" , "flask", "--app", "babylab.app", "run", "--host=0.0.0.0"]