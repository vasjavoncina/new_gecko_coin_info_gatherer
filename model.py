import json
import time


class Coin:
    def __init__(self, name, gecko_listed, bsc_url, times, cmc_listed=None, cmc_url=None):
        self.name = name
        self.gecko_listed = gecko_listed
        self.bsc_url = bsc_url
        self.times = times
        self.cmc_listed = cmc_listed
        self.cmc_url = cmc_url
        


class Coins:
    def __init__(self):
        self.coins = []
        self.coins_in_names = {}
        

    def v_slovar(self):
        return {
            "coins":[
                {
                    "name": coin.name,
                    "gecko_listed": coin.gecko_listed,
                    "bsc_url": coin.bsc_url, 
                    "times": coin.times,
                    "cmc_listed": coin.cmc_listed, 
                    "cmc_url": coin.cmc_url
                }
                for coin in self.coins
            ]
        }


    @classmethod
    def iz_slovarja(cls, slovar_s_coini):
        coini = cls()
        for coin in slovar_s_coini["coins"]:
            nov_coin = coini.add_coin_from_json(
                coin["name"],
                coin["gecko_listed"],
                coin["bsc_url"], 
                coin["times"],
                coin["cmc_listed"],
                coin["cmc_url"]
                )
        return coini


    def add_coin(self, name, gecko_listed, bsc_url, times):
        if name not in self.coins_in_names:
            new = Coin(name, gecko_listed, bsc_url, times)
            self.coins.append(new)
            self.coins_in_names[name] = new
            return new


    def add_coin_from_json(self, name, gecko_listed, bsc_url, times, cmc_listed, cmc_url):
        if name not in self.coins_in_names:
            new = Coin(name, gecko_listed, bsc_url, times, cmc_listed, cmc_url)
        self.coins.append(new)
        self.coins_in_names[name] = new
        return new


    def shrani_stanje(self, ime_datoteke):
        with open(ime_datoteke, "w") as datoteka:
            json.dump(self.v_slovar(), datoteka, ensure_ascii=False, indent=4)


    @classmethod
    def nalozi_stanje(cls, ime_datoteke):
        with open(ime_datoteke) as datoteka:
            slovar_s_coini = json.load(datoteka)
        return cls.iz_slovarja(slovar_s_coini)
