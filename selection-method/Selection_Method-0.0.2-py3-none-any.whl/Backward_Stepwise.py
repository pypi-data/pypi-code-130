class backward_stepwise():

    def __init__(self, x_train, x_test, y_train, y_test, reg_model):
        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.reg_model = reg_model

    def __str__(self):
        return 'Backward Stepwise Object using the {} method.'.format(self.reg_model)

    def select(self):
        X_train = self.x_train
        X_test = self.x_test
        Y_train = self.y_train
        Y_test = self.y_test
        model = self.reg_model
        variable = list(X_train.columns)
        final_list = list(variable)
        model.fit(X_train[final_list], Y_train)
        prev_score = model.score(X_test[final_list], Y_test)
        scores_ = []

        for i in range(len(variable)):
            temp_list = list(final_list)
            for index in range(len(final_list)):
                temp_list.pop(index)
                model.fit(X_train[temp_list], Y_train)
                scores_.append(model.score(X_test[temp_list], Y_test))
                temp_list = list(final_list)

            index = scores_.index(max(scores_))
            score_change = max(scores_) - prev_score

            if score_change > 0: 
                final_list.pop(index)
                prev_score = max(scores_)
                scores_ = []
            else:
                break        
        return (final_list, max(scores_))