class forward_stepwise():

    def __init__(self, x_train, x_test, y_train, y_test, reg_model):
        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.reg_model = reg_model

    def __str__(self):
        return 'Forward Stepwise Object using the {} method.'.format(self.reg_model)

    def select(self):
        X_train = self.x_train
        X_test = self.x_test
        Y_train = self.y_train
        Y_test = self.y_test
        model = self.reg_model
        variable = list(X_train.columns)
        var = list(variable)
        final_list, scores_, prev_score = [], [], 0

        for i in range(len(variable)):
            temp_list = final_list
            for item in var:
                temp_list = temp_list + [item]
                model.fit(X_train[temp_list], Y_train)
                scores_.append(model.score(X_test[temp_list], Y_test))
                temp_list = final_list

            index = scores_.index(max(scores_))
            val = var[index]
            score_change = max(scores_) - prev_score

            if score_change > 0: 
                final_list.append(val)
                var.pop(index)
                prev_score = max(scores_)
                scores_ = []
            else:
                break        
        return (final_list, max(scores_))