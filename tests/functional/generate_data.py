import json
from copy import deepcopy
from uuid import uuid1

from test_data.data_classes import BasePerson, FilmWork, Genre, Person

if __name__ == "__main__":
    filmworks = []
    persons = []
    genres = tuple(Genre(id=uuid1(), name=n) for n in ["comedy", "drama", "action"])
    n_genres = len(genres)

    n_multitask_persons = 3
    multitask_person = tuple(
        Person(
            id=uuid1(),
            name=f"Multitask person {_i}",
            roles=["writer", "actor", "director"],
        )
        for _i in range(n_multitask_persons)
    )
    persons.extend(multitask_person)

    extra_p = 2
    genres_for_fw = 2
    for title, title_len in zip(["HP", "SW"], [4, 2]):
        series_actors = [
            Person(id=uuid1(), name=f"{title}_actor_{_j}", roles=["actor"])
            for _j in range(3)
        ]

        series_writers = [
            Person(id=uuid1(), name=f"{title}_writer_{_j}", roles=["writer"])
            for _j in range(3)
        ]

        series_directors = [
            Person(id=uuid1(), name=f"{title}_director_{_j}", roles=["director"])
            for _j in range(3)
        ]
        persons.extend(series_actors)
        persons.extend(series_writers)
        persons.extend(series_directors)

        for _i in range(title_len):
            actors = deepcopy(series_actors)
            actors.extend(
                [
                    multitask_person[(_i + k) % n_multitask_persons]
                    for k in range(extra_p)
                ]
            )

            writers = deepcopy(series_writers)
            writers.extend(
                [
                    multitask_person[(_i + k + 1) % n_multitask_persons]
                    for k in range(extra_p)
                ]
            )

            directors = deepcopy(series_directors)
            directors.extend(
                [
                    multitask_person[(_i + k + 2) % n_multitask_persons]
                    for k in range(extra_p)
                ]
            )

            filmworks.append(
                FilmWork(
                    id=uuid1(),
                    imdb_rating=10 - _i / 10,
                    title=title,
                    description=f"description for {title}",
                    directors_names=[],
                    actors_names=[],
                    writers_names=[],
                    directors=[BasePerson(**dict(p)) for p in directors],
                    actors=[BasePerson(**dict(p)) for p in actors],
                    writers=[BasePerson(**dict(p)) for p in writers],
                    genres=[genres[(_i + k) % n_genres] for k in range(genres_for_fw)],
                )
            )
    with open("test_data/persons.json", "w") as f:
        json.dump([json.loads(p.json()) for p in persons], f, indent=2)

    with open("test_data/genres.json", "w") as f:
        json.dump([json.loads(p.json()) for p in genres], f, indent=2)

    with open("test_data/movies.json", "w") as f:
        json.dump([json.loads(p.json()) for p in filmworks], f, indent=2)
