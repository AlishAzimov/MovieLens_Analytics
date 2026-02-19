
import os
import requests
from bs4 import BeautifulSoup
from collections import Counter


class Links:
    def __init__(self, path='./ml-latest-small/links.csv', limit=1000):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise FileNotFoundError(f"Файл не найден или пустой: {path}")
        
        self.path = path
        self.limit = limit
        self.links = {}
        self.imdb_info=[]
        self.load()

    def load(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            next(f)
            for i, line in enumerate(f):
                if i >= self.limit:
                    break
                try:
                    movieId, imdbId, _ = line.strip().split(',', 2)
                    self.links[int(movieId)] = int(imdbId)
                except Exception as e:
                    print("Ошибка разбора:",i+2, line)
                    print("→", e)
                    continue
    
    def get_links(self):
        return self.links.copy()

    def get_imdb(self, list_of_movies, list_of_fields=None):
        if len(list_of_movies) > 20:
            raise ValueError("Слишком много фильмов. Разбей список на части по 20 или меньше.")

        if not isinstance(list_of_movies,list):
            raise TypeError("Не верный тип данных в аргументах")

        if list_of_fields is None:
            list_of_fields = ["Director", "Budget", "Cumulative Worldwide Gross", "Runtime"]

        self.imdb_info=[]

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        for movie_id in list_of_movies:
            imdb_id = self.links.get(movie_id)
            if not imdb_id:
                continue

            url = f"https://www.imdb.com/title/tt{imdb_id:07d}/"
            print("Запрашиваем:", url)

            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"[ERROR] [{movie_id}] Не удалось загрузить {url}: код {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                movie_data = {'movie_id': movie_id}

                for field in list_of_fields:
                    if field == "Director":
                        director = None
                        section = soup.find(attrs={"data-testid": "title-pc-principal-credit"})
                        if section:
                            name_tag = section.find("a")
                            if name_tag:
                                director = name_tag.text.strip()
                        movie_data["Director"] = director

                    elif field == "Budget":
                        budget = None
                        for li in soup.find_all("li", class_="ipc-metadata-list__item"):
                            if li.find(string="Budget"):
                                val = li.find_all("span")[-1]
                                if val:
                                    budget = val.text.strip()
                                break
                        movie_data["Budget"] = budget
                    elif field == "Cumulative Worldwide Gross":
                        gross = None
                        for li in soup.find_all("li", class_="ipc-metadata-list__item"):
                            if li.find(string="Gross worldwide"):
                                val = li.find_all("span")[-1]
                                if val:
                                    gross = val.text.strip()
                                break
                        movie_data["Cumulative Worldwide Gross"] = gross

                    elif field == "Runtime":
                        runtime = None
                        tech = soup.find("li", attrs={"data-testid": "title-techspec_runtime"})
                        if tech:
                            time_tag = tech.find("div")
                            if time_tag:
                                runtime = time_tag.text.strip()
                        movie_data["Runtime"] = runtime

                    else:
                        movie_data[field] = None  
                self.imdb_info.append(movie_data)

            except Exception as e:
                print(f"Ошибка для {movie_id}: {e}")
                continue

        self.imdb_info.sort(key=lambda x: x['movie_id'], reverse=True)
        return self.imdb_info
    
    def _ensure_data_loaded(self):
        if not self.imdb_info:
            raise ValueError("Нет данных в imdb_info. Сначала вызови get_imdb().")

    def top_directors(self, n=5):
        if  not isinstance(n, int) or n<=0:
            raise ValueError(f"Неверное значние аргумента: {n}")
        self._ensure_data_loaded()
        counter = Counter()
        for m in self.imdb_info:
            if m.get("Director"):
                counter[m["Director"]] += 1
        return dict(counter.most_common(n))

    def most_expensive(self, n=5):
        if  not isinstance(n, int) or n<=0:
            raise ValueError(f"Неверное значние аргумента: {n}")
        self._ensure_data_loaded()
        data = {}
        for m in self.imdb_info:
            raw = m.get("Budget")
            if raw and "$" in raw:
                digits = ''.join(c for c in raw if c.isdigit())
                if digits:
                    data[m["movie_id"]] = int(digits)
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_profitable(self, n=5):
        if  not isinstance(n, int) or n<=0:
            raise ValueError(f"Неверное значние аргумента: {n}")
        self._ensure_data_loaded()
        data = {}
        for m in self.imdb_info:
            raw_budget = m.get("Budget")
            raw_gross = m.get("Cumulative Worldwide Gross")
            if raw_budget and raw_gross and "$" in raw_budget and "$" in raw_gross:
                b = int(''.join(c for c in raw_budget if c.isdigit()))
                if b == 0:
                    continue
                g = int(''.join(c for c in raw_gross if c.isdigit()))
                data[m["movie_id"]] = g - b
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n=5):
        if  not isinstance(n, int) or n<=0:
            raise ValueError(f"Неверное значние аргумента: {n}")
        self._ensure_data_loaded()
        data = {}

        for m in self.imdb_info:
            r = m.get("Runtime")
            movie_id = m.get("movie_id")

            if r and movie_id:
                try:
                    h = 0
                    mnt = 0
                    parts = r.lower().replace(",", "").split()

                    if "hour" in parts or "hours" in parts:
                        h_index = parts.index("hour") if "hour" in parts else parts.index("hours")
                        h = int(parts[h_index - 1])

                    if "minute" in parts or "minutes" in parts:
                        m_index = parts.index("minute") if "minute" in parts else parts.index("minutes")
                        mnt = int(parts[m_index - 1])

                    total = h * 60 + mnt
                    data[movie_id] = total

                except Exception as e:
                    print(f"Ошибка при обработке '{r}': {e}")

        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:n])

    def top_cost_per_minute(self, n=5):
        if  not isinstance(n, int) or n<=0:
            raise ValueError(f"Неверное значние аргумента: {n}")
        self._ensure_data_loaded()
        data = {}

        for m in self.imdb_info:
            r = m.get("Runtime", "")
            b = m.get("Budget", "")
            movie_id = m.get("movie_id")

            if not (r and b and "$" in b and movie_id):
                continue

            try:
                h = 0
                minut = 0
                parts = r.lower().replace(",", "").split()

                if "hour" in parts or "hours" in parts:
                    h_index = parts.index("hour") if "hour" in parts else parts.index("hours")
                    h = int(parts[h_index - 1])

                if "minute" in parts or "minutes" in parts:
                    m_index = parts.index("minute") if "minute" in parts else parts.index("minutes")
                    minut = int(parts[m_index - 1])

                total_min = h * 60 + minut
                if total_min == 0:
                    continue  

                digits = ''.join(c for c in b if c.isdigit())
                if not digits:
                    continue
                budget_val = int(digits)

                cost = round(budget_val / total_min, 2)
                data[movie_id] = cost

            except (ValueError, IndexError) as e:
                print(f"Ошибка при обработке '{r}' / '{b}': {e}")
                continue

        return dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:n])


if __name__=='__main__':
    b=Links(limit=15)
    print(b.links)
    # a=list(b.links.keys())
    # b.get_imdb(a)
    # print(b.top_directors(10))
    # print(b.most_expensive(10))
    # print(b.most_profitable(10))
    # print(b.longest(10))
    # print(b.top_cost_per_minute(10))
    