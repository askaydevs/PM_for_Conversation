from sklearn import naive_bayes
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
import pickle




class MessageClassifier:
    X: object
    y: object

    y_test: object
    y_train: object
    X_test: object
    X_train: object

    adaboost_model: object
    rf_model: object
    logist_model: object

    best_classifier: object
    best_classifier_name: str
    classifiers: list


    def __init__(self):
        self.classifiers = []




    def split_data(self,data):
        y = data.pop('Tag')
        X = data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.3)




    def load_data_for_training(self, dataframe):
        """Function will split dataframe in x and y and append to training and test set"""
        self.y_train = dataframe.pop('Tag')
        self.X_train = dataframe

        #self.split_data()

    def load_data_for_test(self, dataframe):
        """Function will split dataframe in x and y and append to training and test set"""

        self.y_test = dataframe.pop('Tag')
        self.X_test = dataframe


        #self.split_data()





    def build_adaboost(self,X_train,y_train):
        # Building model with 100 decision trees

        adaboost = AdaBoostClassifier(n_estimators=100)

        self.adaboost_model=adaboost.fit(X_train, y_train)

        self.classifiers.append(("Adaboost",self.adaboost_model))


    def build_rf(self,X_train,y_train):
        # Build model with 1000 decision trees
        rf = RandomForestRegressor(n_estimators=1000, random_state=0)
        self.rf_model = rf.fit(X_train, y_train)
        self.classifiers.append(("RF", self.rf_model))



    def build_nb(self,X_train,y_train):
        # Build model with 1000 decision trees
        nb = naive_bayes.MultinomialNB()
        self.nb_model=nb.fit(X_train, y_train)
        self.classifiers.append(("NB", self.nb_model))
        #self.classifiers.append(("RF", self.rf_model))



    def build_logist(self,X_train, y_train):
        # Build logistic regression with 10-fold CV
        lr = LogisticRegressionCV(cv=5,max_iter=5000)
        self.logist_model=lr.fit(X_train, y_train)
        self.classifiers.append(("Logist", self.logist_model))



    def save_models(self):
        X_train = self.X_train
        y_train = self.y_train

        self.build_adaboost(X_train,y_train)
        print("adaboost trained")
        self.build_logist(X_train,y_train)
        print("logist trained")
        #self.build_rf(X_train,y_train)
        #print("rf trained")
        self.build_nb(X_train, y_train)
        print("nb trained")
        pickle.dump(self.adaboost_model, open('Model_Files/adaboost_model_synth.sav', 'wb'))
        pickle.dump(self.logist_model, open('Model_Files/logist_model_synth.sav', 'wb'))
        #pickle.dump(self.rf_model, open('Model_Files/rf_model_synth.sav', 'wb'))
        pickle.dump(self.nb_model, open('Model_Files/NB_model_synth.sav', 'wb'))




    def load_models(self,ending):

        self.adaboost_model = pickle.load(open('Model_Files/adaboost_model_' + ending +'.sav', 'rb'))

        self.classifiers.append(("Adaboost", self.adaboost_model))


        self.logist_model=pickle.load(open('Model_Files/logist_model_' + ending +'.sav', 'rb'))
        self.classifiers.append(('logistic', self.logist_model))

        self.nb_model = pickle.load(open('Model_Files/NB_model_' + ending +'.sav', 'rb'))
        self.classifiers.append(("NB_model.sav", self.logist_model))



    def evaluate_models(self):

        best_score = 0

        #eval all models in list
        print(self.X_test)

        for (name,model) in self.classifiers:
            score=model.score(self.X_test,self.y_test)
            print("Model: " + name + "- Score: " + str(score))
            if score > best_score:
                self.best_classifier = model
                self.best_classifier_name = name
                best_score = score


    def predict_class(self, dataset):

        classes=[x for x in self.adaboost_model.predict(dataset)]

        return classes











