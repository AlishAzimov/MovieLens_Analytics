
import pytest
import os
import sys
from movie_analysis.Tags import Tags
from movie_analysis.Movies import Movies
from movie_analysis.Ratings import Ratings
from movie_analysis.Links import Links

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ==== Fixtures ====

@pytest.fixture(scope="module")
def tags():
    assert os.path.isfile('./ml-latest-small/tags.csv')
    return Tags(limit=100)

@pytest.fixture(scope="module")
def movies():
    assert os.path.isfile('./ml-latest-small/movies.csv')
    return Movies(limit=100)

@pytest.fixture(scope="module")
def ratings():
    assert os.path.isfile('./ml-latest-small/ratings.csv')
    return Ratings(limit=100)

@pytest.fixture(scope="module")
def links():
    assert os.path.isfile('./ml-latest-small/links.csv')
    l = Links(path='./ml-latest-small/links.csv', limit=100)
    ids = list(l.get_links().keys())[:20]
    info = l.get_imdb(ids)
    assert info, "IMDb данные не загружены"
    return l

# ==== Tags Tests ====

def test_tags_most_words(tags):
    result = tags.most_words(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_tags_longest(tags):
    result = tags.longest(5)
    assert isinstance(result, list)
    for tag in result:
        assert isinstance(tag, tuple)
        assert isinstance(tag[0], str)
        assert isinstance(tag[1], int)
    lengths = [length for _, length in result]
    assert lengths == sorted(lengths, reverse=True)

def test_tags_most_popular(tags):
    result = tags.most_popular(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_tags_with_word(tags):
    result = tags.tags_with("war")
    assert isinstance(result, list)
    assert all(isinstance(tag, str) for tag in result)

def test_tags_dist_by_year(tags):
    result = tags.dist_by_year()
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())

def test_tags_dist_by_month(tags):
    result = tags.dist_by_month()
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())

# ==== Movies Tests ====

def test_movies_dist_by_release(movies):
    result = movies.dist_by_release()
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())

def test_movies_dist_by_genres(movies):
    result = movies.dist_by_genres()
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())

def test_movies_most_genres(movies):
    result = movies.most_genres(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

# ==== Ratings Tests ====

def test_ratings_dist_by_year(ratings):
    r = ratings.Movies(ratings)
    result = r.dist_by_year()
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())

def test_ratings_dist_by_rating(ratings):
    r = ratings.Movies(ratings)
    result = r.dist_by_rating()
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())

def test_ratings_top_by_num_of_ratings(ratings):
    r = ratings.Movies(ratings)
    result = r.top_by_num_of_ratings(5)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

# ==== Links Tests ====



def test_links_top_directors(links):
    result = links.top_directors(3)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_links_most_expensive(links):
    result = links.most_expensive(3)
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_links_most_profitable(links):
    result = links.most_profitable(3)
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_links_longest(links):
    result = links.longest(3)
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, int) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_links_cost_per_minute(links):
    result = links.top_cost_per_minute(3)
    assert isinstance(result, dict)
    assert all(isinstance(k, int) and isinstance(v, float) for k, v in result.items())
    assert list(result.values()) == sorted(result.values(), reverse=True)

def test_get_imdb_raises_on_too_many_movies(links):
    too_many_movies = list(range(21))  
    with pytest.raises(ValueError, match="Слишком много фильмов"):
        links.get_imdb(too_many_movies)

def test_get_imdb_raises_on_invalid_type(links):
    with pytest.raises(TypeError, match="Не верный тип данных"):
        links.get_imdb("not a list")

if __name__ == "__main__":
    pytest.main([__file__])

