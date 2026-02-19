# ==== Классы ====
from movie_analysis.Movies import Movies
from movie_analysis.Ratings import Ratings
from movie_analysis.Tags import Tags
from movie_analysis.Links import Links

# ==== Только классы в __all__ ====
__all__ = [
    "Movies", "Ratings", "Tags", "Links"
]

if __name__=='__main__':
    a=Movies(limit=20)
    print(a.get_all())