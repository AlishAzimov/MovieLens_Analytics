from collections import Counter
import os

class Movies:
    def __init__(self, path='./ml-latest-small/movies.csv', limit=1000):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise FileNotFoundError(f"Файл не найден или пустой: {path}")
        
        self.path = path
        self.limit = limit
        self.movies = []
        self.load()

    def smart_split(self, line):
        line = line.strip()
        if '"' in line:
            first_quote = line.index('"')
            last_quote = line.rindex('"')
            movieID = line[:first_quote - 1]
            title = line[first_quote + 1:last_quote]
            genres = line[last_quote + 2:]
        else:
            movieID, title, genres = line.split(',', maxsplit=2)
        return int(movieID), title.strip(), genres.strip()

    def extract_title_and_year(self, title):
        if title.endswith(')') and '(' in title:
            name, year = title.rsplit('(', 1)
            year_cleaned = year.strip(')')
            if year_cleaned[:4].isdigit():
                return name.strip(), int(year_cleaned[:4])
        return title.strip(), None

    def load(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            next(f)
            for i, line in enumerate(f):
                if i >= self.limit:
                    break
                try:
                    movieID, title_raw, genres = self.smart_split(line)
                    title, year = self.extract_title_and_year(title_raw)
                    genre_list = genres.split('|') if genres != "(no genres listed)" else ['(no genres listed)']
                    self.movies.append({
                        'movieID': movieID,
                        'title': title,
                        'release': year,
                        'genres': genre_list
                    })
                except Exception as e:
                    print("Ошибка разбора:",i+2, line)
                    print("→", e)
                    continue

    def get_all(self):
        return self.movies.copy()

    def dist_by_release(self):
        years = [m['release'] for m in self.movies if m['release'] is not None]
        return dict(Counter(years).most_common())

    def dist_by_genres(self):
        genres = []
        for m in self.movies:
            genres.extend(m['genres'])
        return dict(Counter(genres).most_common())

    def most_genres(self, n):
        if  not isinstance(n, int) or n<=0:
            raise ValueError(f"Неверное значние аргумента: {n}")
        movies = {
            m['title']: len(m['genres']) for m in self.movies
        }
        return dict(sorted(movies.items(), key=lambda x: x[1], reverse=True)[:n])
    

if __name__ == "__main__":
    # Movies()
    a=Movies().get_all()

    print(a)
    # print(Movies().dist_by_genres())
    # print(Movies().dist_by_release())
    m=Movies()
    print(m.most_genres(-2))
