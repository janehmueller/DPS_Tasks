# Task 3 - Date Format Changer
### Train scoring model
```
python run.py
# to do a prediction edit the corresponding lines in the file
```
Take a look at the [data preprocessor](https://github.com/janehmueller/DPS_Tasks/blob/master/task3/data_preprocessor.py#L81)
to see where the training and validation data has to be (or edit it).

The implementation of the model is in `model.py`.
The preprocessing happens in `data_preprocessor.py`.

### Generate training data
```
# generate positive training/validation samples
python date_augmentor.py
# generate negative training/validation samples
python extract_negative_samples.py
```
Take a look at the files to see where the used datasets have to be.


### Train encoder decoder model
Unfortunately saving the model is not possible due to an [open issue](https://github.com/keras-team/keras/issues/8343).
We haven't found a working workaround yet.
The implementation of the model is in `enc_dec_model.py`.
```
python run_enc_dec.py
```


### Data sources
- [Soccer dataset](https://www.kaggle.com/hugomathien/soccer): Extract the matches table from the sqlite dump
- [Terrorism](https://www.kaggle.com/START-UMD/gtd)
- [Trending Youtube videos](https://www.kaggle.com/datasnaek/youtube-new)
- [Yelp](https://www.kaggle.com/yelp-dataset/yelp-dataset)
- [Zillow Economics Data](https://www.kaggle.com/zillow/zecon) (Housing data)
- [Brazilian Ecommerce](https://www.kaggle.com/olistbr/brazilian-ecommerce)
- [Donors Choose](https://www.kaggle.com/donorschoose/io)
- [Health Insurance](https://www.kaggle.com/hhs/health-insurance-marketplace)
