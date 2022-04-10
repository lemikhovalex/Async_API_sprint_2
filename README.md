# Movies api

## Deployment
* Checkout docker-compose files with common services from https://github.com/maximium/yp-docker
* Checkout ETL service from https://github.com/maximium/etl-pges
* Checkout this api repository
* Rename .env.sample to .env in each repo, change settings as needed.
* Run required service combination with command like `docker-compose up elasticsearch nginx` or `docker-compose up` in corresponding directories starting with common servises.
* Specify `-f docker-compose.yaml` option in `docker-compose up` command to run service in production mode or just `docker-compose up` to run in dev mode.
* Check api documentation at http://localhost:8000/api/openapi

## Tests
* Change working directory to *tests/functional*
* Rename .env.sample to .env to customize container names
* Run `docker-compose up`

Ссылка для DeepBlue - https://github.com/maximium/Async_API_sprint_2

Таски по ETL закрыты тут - https://github.com/maximium/etl-pges
