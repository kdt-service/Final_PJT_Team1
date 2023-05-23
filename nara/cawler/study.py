from multiprocessing import Pool


def work(x):
    print(x)


if __name__ == "__main__":
    pool = Pool(4)
    data = range(1, 100)
    pool.map(work, data)