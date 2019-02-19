from enc_dec_model import EncDecModel


def train(model: EncDecModel):
    model.build()
    model.train()


def main():
    model = EncDecModel()
    train(model)


if __name__ == '__main__':
    main()
