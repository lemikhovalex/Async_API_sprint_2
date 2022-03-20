from http import HTTPStatus
from typing import List

from api.v1.genres import GenrePartial
from api.v1.persons import PersonPartial
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.films import FilmService, get_film_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах

# Модель ответа API


# todo import from module with shared info


# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру
# И адрес запроса будет выглядеть так — /api/v1/film/some_id
# В сигнатуре функции указываем тип данных, получаемый из адреса запроса
# (film_id: str)
# И указываем тип возвращаемого объекта — Film


class FilmFullInfo(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
    description: str
    genre: List[GenrePartial]
    actors: List[PersonPartial]
    writers: List[PersonPartial]
    directors: List[PersonPartial]


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=FilmFullInfo)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmFullInfo:
    return FilmFullInfo(
        uuid="123",
        title="the very best movie",
        imdb_rating=-1.0,
        description="the best one",
        genre=[GenrePartial(uuid="17", name="comedy")],
        actors=[PersonPartial(uuid="17", full_name="comediant")],
        writers=[],
        directors=[],
    )
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые
        # содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="film not found"
        )

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования
    # ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать