from datetime import datetime
from collections import Counter, defaultdict
from .Movies import Movies as mv
import os


class Ratings:
    def __init__(self, path='./ml-latest-small/ratings.csv', limit=1000):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            raise FileNotFoundError(f"Файл не найден или пустой: {path}")

        self.data=[]
        self.path = path
        self.limit = limit
        self.load()
    
    def load(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            headers=file.readline().strip().split(',',3)
            for i, line in enumerate(file):
                if i >= self.limit:
                    break
                try:
                    values=line.strip().split(',')
                    self.data.append(dict(zip(headers,values)))     
                except Exception as e:
                    print("Ошибка разбора:",i+2, line)
                    print("→", e)
                    continue


    class Movies: 
        def __init__(self, outer):
            if not isinstance(outer, Ratings):
                raise TypeError("Аргумент должен быть экземпляром класса Ratings")
            self.data=outer.data

        def dist_by_year(self):
            ratings_and_year=[]
            for row in self.data:
                year=datetime.fromtimestamp(int(row['timestamp'])).year
                ratings_and_year.append(year)
            return dict(Counter(ratings_and_year).most_common())
        
        def dist_by_rating(self):
            ratings_all=[]
            for row in self.data:
                rating=row['rating']
                ratings_all.append(rating)
            return dict(Counter(ratings_all).most_common())
        
        def top_by_num_of_ratings(self, n=5):
            if  not isinstance(n, int) or n<=0:
                raise ValueError(f"Неверное значние аргумента: {n}")
            data_from_mvcsv=mv().get_all()
            title_and_id={str(row['movieID']): row['title'] for row in data_from_mvcsv}
            rating_count=defaultdict(int)
            for row in self.data:
                movieId=row['movieId']
                rating_count[movieId]+=1
            title_ratings = {
            title_and_id[movie_id]: count
            for movie_id, count in rating_count.items()
            if movie_id in title_and_id
            }
            top_movies = dict(sorted(title_ratings.items(), key=lambda x: x[1], reverse=True)[:n])
            return top_movies
        
        def average(self,values):
            return sum(values) / len(values) if values else 0
        
        def median(self,values):
            if not values:
                return 0
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            mid = n // 2
            if n % 2 == 1:
                return sorted_vals[mid]
            else:
                return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2

        def top_by_ratings(self, n=5,metric='average'):
            if  not isinstance(n, int) or n<=0 or metric not in ['average','median']:
                raise ValueError(f"Неверное значние аргумента: {n,metric}")
            
            metric=self.average if metric=='average' else self.median
            data_from_mvcsv = mv().get_all()
            title_and_id = {str(row['movieID']): row['title'] for row in data_from_mvcsv}

            ratings = defaultdict(list)
            for row in self.data:
                movie_id = str(row['movieId'])
                rating = float(row['rating'])
                ratings[movie_id].append(rating)

            metric_values = {}
            for movie_id, rating_list in ratings.items():
                if movie_id in title_and_id and rating_list:
                    value = round(metric(rating_list), 2)
                    title = title_and_id[movie_id]
                    metric_values[title] = value

            top_movies = dict(sorted(metric_values.items(), key=lambda x: x[1], reverse=True)[:n])
            return top_movies
        def variance(self,lst):
                if not lst:
                    return 0
                mean=sum(lst)/len(lst)
                return sum((x-mean)**2 for x in lst)/len(lst)
        def top_controversial(self, n=5):
            if  not isinstance(n, int) or n<=0:
                raise ValueError(f"Неверное значние аргумента: {n}")
            data_from_mvcsv = mv().get_all()
            title_and_id = {str(row['movieID']): row['title'] for row in data_from_mvcsv}
            ratings=defaultdict(list)
            for row in self.data:
                movieId=str(row['movieId'])
                rating=float(row['rating'])
                ratings[movieId].append(rating)
            
            variance_dict={}
            for movie_id,rating_list in ratings.items():
                if movie_id in title_and_id and len(rating_list)>=2:
                    var=round(self.variance(rating_list),2)
                    title=title_and_id[movie_id]
                    variance_dict[title]=var
            top_movies=dict(sorted(variance_dict.items(), key=lambda x:x[1], reverse=True)[:n])
            return top_movies

    class Users(Movies):
        def __init__(self, outer):
            self.outer=outer
        def dist_by_num_of_rating(self):
            user_counter=Counter()
            for row in self.outer.data:
                user_id=row['userId']
                user_counter[user_id]+=1
            
            return dict(user_counter.most_common())
        
        def dist_by_rating_values(self, metric='average'):
            if metric not in ['average','median']:
                raise ValueError(f"Неверное значние аргумента: {metric}")
            ratings = defaultdict(list)
            for row in self.outer.data:
                user_id = row['userId']
                rating = float(row['rating'])
                ratings[user_id].append(rating)
            func = self.average if metric == "average" else self.median
            user_metrics = {
            user_id: round(func(rating_list), 2)
            for user_id, rating_list in ratings.items()
            }
            return dict(sorted(user_metrics.items(), key=lambda x: x[1], reverse=True))
        
        def top_controversial_users(self, n):
            if  not isinstance(n, int) or n<=0:
                raise ValueError(f"Неверное значние аргумента: {n}")
            ratings=defaultdict(list)
            for row in self.outer.data:
                user_id = row['userId']
                rating = float(row['rating'])
                ratings[user_id].append(rating)
            user_variances={}
            for user_id, rating_list in ratings.items():
                if len(rating_list) >= 2:
                    var = round(self.variance(rating_list), 2)
                    user_variances[user_id] = var
            return dict(sorted(user_variances.items(), key=lambda x: x[1], reverse=True)[:n])
        

if __name__=='__main__':
    a=Ratings(limit=10000)  
    print(a.Movies(a).dist_by_year())
    print(a.Movies(a).dist_by_rating())
    print(a.Movies(a).top_by_num_of_ratings())

