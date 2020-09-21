import json
import csv


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    prods = dict()
    users = set()

    with open(
        "/Users/lap01203/PycharmProjects/vinid/data/VinIDRecruitChallenge_MLTrack_DataSet.csv",
        mode="r",
        encoding="utf-8"
    ) as csv_file:
        csv_file.readline()
        dat = csv.reader(csv_file)
        count = 0
        # csv_file.readline()
        for row in dat:
            x = json.loads(row[2].replace("'", '"'))
            count+=1
            prices = []
            for trans in x:
                if trans["article"] not in prods:
                    value = trans["salesquantity"] * trans["price"]
                    prods[trans["article"]] = [value, {trans["price"]}, trans["salesquantity"]]
                else:
                    prods[trans["article"]][0] += trans["salesquantity"] * trans["price"]
                    prods[trans["article"]][1].add(trans["price"])
                    prods[trans["article"]][2] += trans["salesquantity"]
    min_price, max_price = 18250, 18250
    min_quant, max_quant = 9999999, 0
    ind_min_quant, ind_max_quant = -1, -1
    for prod in prods:
        tmp_min, tmp_max = min(prods[prod][1]), max(prods[prod][1])
        min_price = min(tmp_min, min_price)
        max_price = max(tmp_max, max_price)
        if prods[prod][2] < min_quant:
            min_quant = prods[prod][2]
            ind_min_quant = prod
        if prods[prod][2] > max_quant:
            max_quant = prods[prod][2]
            ind_max_quant = prod
        max_quant = max(prods[prod][2], max_quant)
        print(prod, prods[prod], len(prods[prod][1]))
    print(count, len(prods), min_price, max_price, min_quant, max_quant, ind_min_quant, ind_max_quant)
