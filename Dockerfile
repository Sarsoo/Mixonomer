FROM node:22.5.1-alpine AS js-build

RUN npm install -g sass

COPY ./package.json /mixonomer/
COPY ./package-lock.json /mixonomer/
COPY ./webpack.common.js /mixonomer/
COPY ./webpack.prod.js /mixonomer/
COPY ./.babelrc /mixonomer/
COPY ./src /mixonomer/src/
WORKDIR /mixonomer

RUN npm ci
RUN npm run build
RUN sass src/scss/style.scss build/style.css

FROM python:3.11-slim as py

RUN pip install poetry==1.8.3
RUN poetry config virtualenvs.create false

WORKDIR /mixonomer

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install
RUN poetry add gunicorn@^20

COPY ./music ./music
COPY gunicorn.conf.py gunicorn.conf.py
COPY main.api.py main.py
COPY --from=js-build /mixonomer/build ./build/

EXPOSE 80

#Run the container
ENTRYPOINT [ "poetry", "run", "gunicorn" ]