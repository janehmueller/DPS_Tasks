from model import Model


def train(model: Model):
    model.build()
    model.train()


def main():
    model = Model()
    train(model)
    # data = ["1989-12-11", "1988-11-12", "thisIsDate", "1966-02-24", "1957-02-05", "12-11-1989", "2008-08-08",
    #         "2017-01-07", "2014-13-31", "2000-01-32"]
    # model.predict(data, model_path="models/model_emb3_epochs2.hdf5")


if __name__ == '__main__':
    main()
