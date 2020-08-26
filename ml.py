import sys, csv, json
from decimal import *

class Matrix:
    def __init__(self, data):
        self.matrix = data
        self.row = len(data)
        self.col = len(data[0])

    def add(self, matrix):
        for i in range(self.row):
            for j in range(self.col):
                self.matrix[i][j] += matrix[0] if len(matrix) == 1 else matrix[i][j]
        return self
    
    def dot(self, matrix):
        m1_r = self.row
        m1_c = self.col
        m2_r = len(matrix)
        m2_c = len(matrix[0])
        if m1_c != m2_r: 
            raise("error: matricies dimension does not correct")
        def s_3(i, j): 
            return sum([self.matrix[i][k] * matrix[k][j] for k in range(m1_c)])
        def s_2(i): 
            return [s_3(i, j) for j in range(m2_c)]
        return Matrix([s_2(i) for i in range(m1_r)])

    def transpose(self):
        def s_2(i): return [self.matrix[j][i] for j in range(self.row)]
        return Matrix([s_2(i) for i in range(self.col)])

    def inverse(self):
        if self.row == 2 and self.col == 2:
            temp = self.matrix[0][0]
            self.matrix[0][0] = self.matrix[1][1]
            self.matrix[1][1] = temp
            self.matrix[0][1] = -self.matrix[0][1]
            self.matrix[1][0] = -self.matrix[1][0]
            determinant = self.matrix[0][0]*self.matrix[1][1] - self.matrix[0][1]*self.matrix[1][0]
            return self.multiply([1/determinant])

    def multiply(self, matrix):
        for i in range(self.row):
            for j in range(self.col):
                self.matrix[i][j] *= matrix[0] if len(matrix) == 1 else matrix[i][j]
        return self

def linear(x, param):
    # Return fungsi hipotesis
    return [param[0] + sum([x[i][j] * param[j+1] for j in range(len(x[i]))]) for i in range(len(x))]

def cost(x, y, param):
    n = len(y)
    # Hitung prediksi titik y
    x = linear(x, param)
    # Hitung jumlah loss menggunakan MSE (Mean Squared Error)
    return 1/(2*n)*sum([(float(x[i]) - float(y[i]))**2 for i in range(n)])

def cost_der(x, y, param, active = 0):
    n = len(y)
    x = linear(x, param)
    # Turunan parsial dari fungsi cost
    return (1/n)*sum([(float(x[i]) - float(y[i]))*(param[active] if active != 0 else 1) for i in range(n)])

# Gradient descent, mencari titik minimum dari fungsi hingga gradient dari titik tersebut mendekati/menjadi 0
def grad_descent(x, y, param, lrate):
    return [param[i] - (lrate*cost_der(x, y, param, i)) for i in range(len(param))]

def train(x, y, param, lrate = 0.1, epoch = 100, interval = 1):
    for i in range(epoch):
        param = grad_descent(x, y, param, lrate)
        if (i % interval == 0) or (i+1 == epoch):
            print("Loss -> {} | Param -> {} ".format(cost(x,y,param), param))

    return param

def predict(x, param, expected):
    prediction = linear(x, param)
    for i, v in enumerate(prediction):
        i = i+1
        print("="*50)
        print("{}. Prediction   -> {}".format(i, v))
        print("{}. Expected     -> {}".format(i, expected[i-1]))
        print("{}. Delta        -> {}".format(i, v-expected[i-1]))
        print("="*50)


# Normal equation
def normal_eq():
    pass

def read_csv(target, normalize = False, skip = [], y_key = ''):
    col = []
    x = []
    y = []
    with open(target) as f:
        data = csv.reader(f, delimiter=',')
        for i, v in enumerate(data):
            if i == 0:
                col = v
            else:
                d = {}
                a = []
                for i, k in enumerate(v):
                    if col[i] in skip: continue
                    if col[i] == y_key:
                        y.append(k)
                        continue
                    d[col[i]] = k
                if normalize:
                    d = normalization(d)
                    a = [d[k] for k in d]
                x.append(a)
                if i > 30:
                    break
        f.close()
    return x, y, len(x[0])

def scale(data, scale):
    return float(data)*scale

def normalization(data):
    for k in data:
        if data[k] == '':
            data[k] = 0
        if k == 'Date':
            n_date = sum([int(j) for j in data[k].split('-')])
            data[k] = scale(n_date, 0.0005)
        elif k in ['MAX', 'MIN', 'MEA', 'YR', 'MO', 'DA', 'Precip']:
            data[k] = scale(data[k], 0.02)
        elif k in ['PRCP']:
            data[k] = scale(data[k], 10)
        elif k in ['MaxTemp', 'MinTemp', 'MeanTemp']:
            data[k] = scale(data[k], 0.05)
        else:
            data[k] = scale(data[k], 0.0001)
    return data


def main():
    sys.setrecursionlimit(20000)
    # Matrix 
    # A[0][0]B[0][0] * A[0][1]B[1][0] * A[0][2]B[2][0]
    # A[0][0]B[0][1] * A[0][1]B[1][1] * A[0][2]B[2][1]
    # A[0][0]B[0][2] * A[0][1]B[1][2] * A[0][2]B[2][2]
    # A[0][0]B[0][3] * A[0][1]B[1][3] * A[0][2]B[2][3]
    # Linear
    skip = ['Precip', 'WindGustSpd', 'Snowfall', 'PoorWeather', 'DR', 'SPD', 'SNF', 'SND', 'FT', 'FB', 'FTI', 'ITH', 'PGT', 'TSHDSBRSGF', 'SD3', 'RHX', 'RHN', 'RVG', 'WTE', 'PRCP']
    n_x, n_y, l_p = read_csv('datasets/Summary of Weather.csv', normalize=True, skip=skip, y_key = 'MeanTemp')
    #y = [111,222,333,444,555,666]
    #x = [[1], [2], [3], [4], [5], [6]]
    # The 0 index of param is for bias, in other words the actual param length is 1
    param = [0] + [1] * l_p
    new_param = train(n_x, n_y, param, 
            lrate = 0.1, 
            epoch = 500, 
            interval = 1)
    prediction = [[6], [7], [7.5]]
    expected = [666, 777, 832.5]
    #predict(prediction, new_param, expected)
    


if __name__ == '__main__':
    main()
