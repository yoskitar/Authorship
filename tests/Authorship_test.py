import unittest
import time

import sys
sys.path[0] = sys.path[0].replace('\\tests','')

from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix

from nltk.corpus import stopwords
from string import punctuation

import numpy as np

from tensorflow.keras.wrappers.scikit_learn import KerasClassifier

# Extraccion y filtrado de datos
from Authorship.functions import real_xml, filter_df

# MODELO: TfidfVectorizer, ANOVA, MLPClasiffier
from sklearn.feature_extraction.text import TfidfVectorizer
from Authorship.feature_selection import ANOVA
from Authorship.neural_network import MLPClassifier

# MODELO: test_TfidfVectorizer_ANOVA_SVCLinear
#from sklearn.feature_extraction.text import TfidfVectorizer
#from Authorship.feature_selection import ANOVA
from sklearn.svm import LinearSVC

# MODELO: test_TfidfVectorizer_ANOVA_LSA_MLPClasiffier
#from sklearn.feature_extraction.text import TfidfVectorizer
#from Authorship.feature_selection import ANOVA
from sklearn.decomposition import TruncatedSVD as LSA
#from Authorship.neural_network import MLPClassifier

# MODELO: test_TfidfVectorizer_ANOVA_NMF_MLPClasiffier
#from sklearn.feature_extraction.text import TfidfVectorizer
#from Authorship.feature_selection import ANOVA
from sklearn.decomposition import NMF
#from Authorship.neural_network import MLPClassifier

from Authorship.preprocessing import StopWords, Stemmer
from Authorship.feature_extration.text import Sequences

"""from Authorship.TFIDFANOVAMLP.Authorship import Authorship as MLP
from Authorship.TFIDFAVOVASVM.Authorship import Authorship as SVM
from Authorship.SESEPCNN.Authorship import Authorship as SEPCNN
from Authorship.SELSTM.Authorship import Authorship as LSTM"""


class AuthorshipTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(AuthorshipTest, self).__init__(*args, **kwargs)

        # Parametros genericos para cualquier test
        self.random_state = 1
        self.nwords = 50
        self.frecuency = 200
        self.subset = None
        self.nfiles = None
        self.sample = 10000
        self.test_size = 0.2
        self.verbose = True

        # Parametros TfidfVectorizer
        self.TfidfVectorizer_params = {
            'stop_words': stopwords.words("spanish") + list(punctuation),
            'max_features': 100000,
            'ngram_range': (1,2),
            'analyzer': 'word',
            'encoding': 'utf8',
            'dtype': np.float32,
            'min_df': 1.0 / 1000.0,
            'max_df': 999.0 / 1000.0,
            'strip_accents': 'unicode',
            'decode_error': 'replace',
            'lowercase': True
        }

        # Parametros ANOVA
        self.ANOVA_params = {
            'k': 20000
        }

        # Parametros MLPClassifier
        self.MLPClassifier_params = {
            'layers': 1,
            'units': 96,
            'dropout_rate': 0.3,
            'epochs': 100,
            'batch_size': 1024,
            'input_shape': self.ANOVA_params['k'],
            'sparse': True,
            'verbose': False
        }

        # Parametros LinearSVC
        self.LinearSVC_params = {
            'C': 1.0,
            'penalty': 'l2',
            'dual': True,
            'loss': 'squared_hinge',
            'max_iter': 5000,
        }

        # Parametros LSA
        self.LSA_params = {
            'n_components': 700,
            'n_iter': 15
        }

        # Parametros MLPClassifier
        self.MLPClassifier_params_2 = {
            'layers': 1,
            'units': 128,
            'dropout_rate': 0.3,
            'epochs': 150,
            'batch_size': 1024,
            'input_shape': self.LSA_params['n_components'],
            'sparse': False,
            'verbose': False
        }

        # Parametros NMF
        self.NMF_params = {
            'n_components': 700
        }

        # Parametros MLPClassifier
        self.MLPClassifier_params_3 = {
            'layers': 1,
            'units': 96,
            'dropout_rate': 0.3,
            'epochs': 100,
            'batch_size': 1024,
            'input_shape': self.LSA_params['n_components'],
            'sparse': False,
            'verbose': False
        }

        # Parametros StopWords
        self.StopWords_params = {
            'stop_words': stopwords.words("spanish")
        }

        # Parametros Stemmer
        self.Stemmer_params = {
            'language': 'spanish'
        }

        # Parametros Sequences
        self.Sequences_params = {
            'num_words': 50000, 
            'maxlen': 250, 
            'padding': 'post', 
            'truncating': 'post'
        }

    def test_read_xml_filter(self):
        df = real_xml('./iniciativas08/', nfiles = self.nfiles)
        if self.subset != None: df = df.sample(self.sample, random_state = self.random_state)
        if self.nfiles == None: df = filter_df(df, nwords = self.nwords, frecuency = self.frecuency)
        self.assertGreater(df.shape[0], 0)

    def test_TfidfVectorizer_ANOVA_MLPClassifier(self):
        df = real_xml('./iniciativas08/', nfiles = self.nfiles)
        if self.subset != None: df = df.sample(self.sample, random_state = self.random_state)
        if self.nfiles == None: df = filter_df(df, nwords = self.nwords, frecuency = self.frecuency)
        
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'],
            df['name'],
            test_size = self.test_size,
            random_state = self.random_state
        )

        labels = list(np.unique(df['name']))
        num_classes = len(labels)

        clf = Pipeline(steps = [
            ('TfidfVectorizer', TfidfVectorizer(
                **self.TfidfVectorizer_params
            )),
            ('ANOVA', ANOVA(
                **self.ANOVA_params
            )),
            ('MLPClassifier', KerasClassifier(
                MLPClassifier,
                num_classes = num_classes,
                **self.MLPClassifier_params
            ))
        ], verbose = True)

        clf.fit(X_train, y_train)
        print("Accuracy train: ", clf.score(X = X_train, y = y_train))
        print("Accuracy test: ", clf.score(X = X_test, y = y_test))

        y_test_pred = clf.predict(X = X_test)
        print(classification_report(y_test, y_test_pred))
        return(True)
    
    def test_TfidfVectorizer_ANOVA_LinearSVC(self):
        df = real_xml('./iniciativas08/', nfiles = self.nfiles)
        if self.subset != None: df = df.sample(self.sample, random_state = self.random_state)
        if self.nfiles == None: df = filter_df(df, nwords = self.nwords, frecuency = self.frecuency)
        
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'],
            df['name'],
            test_size = self.test_size,
            random_state = self.random_state
        )

        labels = list(np.unique(df['name']))
        num_classes = len(labels)

        clf = Pipeline(steps = [
            ('TfidfVectorizer', TfidfVectorizer(
                **self.TfidfVectorizer_params
            )),
            ('ANOVA', ANOVA(
                **self.ANOVA_params
            )),
            ('LinearSVC', LinearSVC(
                **self.LinearSVC_params
            ))
        ], verbose = True)

        clf.fit(X_train, y_train)
        print("Accuracy train: ", clf.score(X = X_train, y = y_train))
        print("Accuracy test: ", clf.score(X = X_test, y = y_test))

        y_test_pred = clf.predict(X = X_test)
        print(classification_report(y_test, y_test_pred))
        return(True)

    def test_TfidfVectorizer_ANOVA_LSA_MLPClassifier(self):
        df = real_xml('./iniciativas08/', nfiles = self.nfiles)
        if self.subset != None: df = df.sample(self.sample, random_state = self.random_state)
        if self.nfiles == None: df = filter_df(df, nwords = self.nwords, frecuency = self.frecuency)
        
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'],
            df['name'],
            test_size = self.test_size,
            random_state = self.random_state
        )

        labels = list(np.unique(df['name']))
        num_classes = len(labels)

        model = KerasClassifier(
            MLPClassifier,
            num_classes = num_classes,
            **self.MLPClassifier_params_2
        )
        param_grid = {
            'layers': [1,2],
            'units': [128],
            'dropout_rate': [0.3]
        }
        clf = Pipeline(steps = [
            ('TfidfVectorizer', TfidfVectorizer(
                **self.TfidfVectorizer_params
            )),
            ('ANOVA', ANOVA(
                **self.ANOVA_params
            )),
            ('LSA', LSA(
                **self.LSA_params
            )),
            ('GridSearchCV', GridSearchCV(
                estimator = model,
                param_grid = param_grid,
                verbose = self.verbose
            ))
        ], verbose = True)

        clf.fit(X_train, y_train)
        print(clf['GridSearchCV'].best_params_)
        print("Accuracy train: ", clf.score(X = X_train, y = y_train))
        print("Accuracy test: ", clf.score(X = X_test, y = y_test))

        y_test_pred = clf.predict(X = X_test)
        print(classification_report(y_test, y_test_pred))
        return(True)

    def test_TfidfVectorizer_ANOVA_NMF_MLPClassifier(self):
        df = real_xml('./iniciativas08/', nfiles = self.nfiles)
        if self.subset != None: df = df.sample(self.sample, random_state = self.random_state)
        if self.nfiles == None: df = filter_df(df, nwords = self.nwords, frecuency = self.frecuency)
        
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'],
            df['name'],
            test_size = self.test_size,
            random_state = self.random_state
        )

        labels = list(np.unique(df['name']))
        num_classes = len(labels)

        model = KerasClassifier(
            MLPClassifier,
            num_classes = num_classes,
            **self.MLPClassifier_params_3
        )
        param_grid = {
            'layers': [1,2],
            'units': [64,96],
            'dropout_rate': [0.2,0.3]
        }
        clf = Pipeline(steps = [
            ('TfidfVectorizer', TfidfVectorizer(
                **self.TfidfVectorizer_params
            )),
            ('ANOVA', ANOVA(
                **self.ANOVA_params
            )),
            ('NMF', NMF(
                **self.NMF_params
            )),
            ('GridSearchCV', GridSearchCV(
                estimator = model,
                param_grid = param_grid,
                verbose = self.verbose
            ))
        ], verbose = True)

        clf.fit(X_train, y_train)
        print(clf['GridSearchCV'].best_params_)
        print("Accuracy train: ", clf.score(X = X_train, y = y_train))
        print("Accuracy test: ", clf.score(X = X_test, y = y_test))

        y_test_pred = clf.predict(X = X_test)
        print(classification_report(y_test, y_test_pred))
        return(True)

    def test_StopWords_Stemmer_Sequences_LSTM(self):
        df = real_xml('./iniciativas08/', nfiles = self.nfiles)
        if self.subset != None: df = df.sample(self.sample, random_state = self.random_state)
        if self.nfiles == None: df = filter_df(df, nwords = self.nwords, frecuency = self.frecuency)
        df = df.head(10000)
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'],
            df['name'],
            test_size = self.test_size,
            random_state = self.random_state
        )

        labels = list(np.unique(df['name']))
        num_classes = len(labels)

        clf = Pipeline(steps = [
            ('StopWords', StopWords(
                **self.StopWords_params
            )),
            ('Stemmer', Stemmer(
                **self.Stemmer_params
            )),
            ('Sequences', Sequences(
                **self.Sequences_params
            ))
        ], verbose = True)

        clf.fit(X_train, y_train)
        print(clf.transform(X_test))

if __name__ == "__main__":
    unittest.main(verbosity = 2)