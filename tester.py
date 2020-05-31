"""
Podział testów ze względu na strategię: 
- Alicja - singlequery
- Marysia - stopwords
- Kuba - chunks
"""

import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
import requests, json

def get_answer_from_kps(question):
    query = question[0]
    real_answer = question[1]
    params = {"engine": "google", "strategy": "singlequery"}
    url =f"http://localhost:5010/ask/{query}"
    print(url)
    try:
        answer = requests.get(url, params=params)
        kps_answer = json.loads(answer.text)
        kps_answer["real_answer"] = real_answer      
    except:
        kps_answer["real_answer"] = "NIE ZNALEZIONO"       
    return kps_answer


test_data = pd.read_excel("./pytania.xlsx", converters={
                                                'Pytanie':str, 
                                                'Odpowiedź':str, 
                                                'TypPytania':str, 
                                                'TypOdpowiedzi':str,
                                                'Domena WordnetPL':str,
                                                'Dziedzina odpowiedzi':str
                                            })
columns = test_data.columns
questions = test_data.values

pool = ThreadPool(4)
results = pool.map(get_answer_from_kps, questions)
pool.close()
pool.join()

answer_data = pd.DataFrame(results)
answer_data.to_excel("./wyniki.xlsx")