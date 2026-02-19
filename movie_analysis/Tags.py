import os
from collections import Counter
from datetime import datetime

class Tags:
    def __init__(self, path='./ml-latest-small/tags.csv', limit=1000):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise FileNotFoundError(f"Файл не найден или пустой: {path}")
        self.path=path
        self.limit=limit
        self.tags = []
        with open(self.path, 'r', encoding='utf-8') as file:
            next(file)  
            try:
                for i, line in enumerate(file):
                    if i >= self.limit:
                        break
                    parts = line.strip().split(',', 3)  
                    if len(parts) < 4:
                        continue
                    user_id = int(parts[0])
                    movie_id = int(parts[1])
                    tag = parts[2]
                    timestamp = int(parts[3])
                    self.tags.append({'userId': user_id, 'movieId': movie_id, 'tag': tag, 'timestamp': timestamp})
                    
            except Exception as e:
                print(f"Ошибка при загрузке тегов: {e}, line:{i+2} - {line}")


    def get_tags(self):
        return self.tags.copy()

    def most_words(self, n=5):
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Неверное значение аргумента: {n}")
        
        unique_tags = set(i['tag'].strip().lower() for i in self.tags)
        counts = {tag: len(tag.split()) for tag in unique_tags}

        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n):
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Неверное значение аргумента: {n}")
        
        unique_tags = set(i['tag'].strip().lower() for i in self.tags)
        counts = {tag: len(tag) for tag in unique_tags}

        return list(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n])
    
    def most_words_and_longest(self, n=5):
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Неверное значение аргумента: {n}")
    
        most_words_tags = set(self.most_words(n).keys())
        longest_tags = set(tag for tag, _ in self.longest(n))
        intersection = most_words_tags & longest_tags

        return sorted(intersection)

    
    def most_popular(self, n=5):
        if not isinstance(n, int) or n <= 0:
            raise ValueError(f"Неверное значение аргумента: {n}")
        
        tag_list = [i['tag'].strip().lower() for i in self.tags]
        counter = Counter(tag_list)
    
        return dict(counter.most_common(n))

    def tags_with(self, word):
        if not isinstance(word, str) or not word.strip():
            raise ValueError(f"Некорректное слово для поиска: {word}")

        word = word.strip().lower()
        # set comprehension
        matching_tags = {
            i['tag'].strip().lower()
            for i in self.tags
            if word in i['tag'].strip().lower()
        }

        return sorted(matching_tags)

    def dist_by_year(self):
        years = []
        for tag in self.tags:
            ts = tag.get('timestamp')
            if ts:
                year = datetime.fromtimestamp(ts).year
                years.append(year)
        return dict(Counter(years).most_common())
    
    def dist_by_month(self):
        months = []
        for tag in self.tags:
            ts = tag.get('timestamp')
            if ts:
                month = datetime.fromtimestamp(ts).month
                months.append(month)
        return dict(Counter(months).most_common())
    

if __name__ == '__main__':
    a=Tags(limit=100)
    t=a.get_tags()
    # print(t)
    # print(a.most_words(10))
    # print(a.longest(10))
    # print(a.most_words_and_longest(10))
    print(a.tags_with('W'))
    print(a.dist_by_month())
    print(a.dist_by_year())




