import time
import base64


def decode_this(string):
    '''Takes a base64 string and decodes it to human-readable value.'''
    return base64.b64decode(string).decode('utf-8')


def encode_this(string):
    '''Takes a human-readable string and encodes it to a base64 value.'''
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def just_read(file_path):
    '''Takes a csv file and makes a raw 2d table from it.'''
    with open(file_path, 'r') as csvfile:
        return [line.split(',') for line in csvfile]


def read_and_decode(file_path):
    '''
    Sorts by second value, then decodes
    the second, fifth, sixth and seventh values
    to a human-readable format and returns it
    in a 2d table (list of list).
    '''
    data_set = just_read(file_path)
    data_set = sorted(data_set, key=lambda x: x[1], reverse=True)
    for line in data_set:
        line[1] = time.ctime(int(line[1]))
        line[4] = decode_this(line[4])
        line[5] = decode_this(line[5])
        line[6] = decode_this(line[6])
    return data_set


def append_to_csv(data_string, file_path='./static/data/question.csv'):
    '''
    Takes a string and appends to the file.
    '''
    with open(file_path, 'a') as csvfile:
        csvfile.write(data_string+'\n')


def write_to_csv(data_list, file_path):
    '''
    Takes a list and writes it to the file.
    '''
    with open(file_path, 'w') as csvfile:
        for line in data_list:
            line = ','.join(line)
            csvfile.write(line)


def id_generator(file_path):
    '''
    Takes the first value of the last line from the file,
    adds 1 to it and returns the value as a string.
    '''
    data_set = just_read(file_path)
    return str(int(data_set[-1][0]) + 1)


def find_line_by_id(data_set, question_id):
        '''
        Finds question data line by question_id in 2d table (list in list) and returns it.
        '''
        i = 0
        while i < len(data_set) - 1 and data_set[i][0] != str(question_id):
            i += 1
        return data_set[i]
