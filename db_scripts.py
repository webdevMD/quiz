import sqlite3
db_name = 'quiz2.sqlite'
conn = None
cursor = None
#столбцы-поля, строки-записи
#PK праймери кей - первичный ключ, FK - форейн - внешний ключ
def open():#открывать соединение, открыть бд
    global conn, cursor
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

def close():
    cursor.close()
    conn.close()

def do(query):
    cursor.execute(query)
    conn.commit()

def doMany(query, lst):#много повторений
    cursor.executemany(query, lst)
    conn.commit()#сохранитть в базу, упр.сохранить файл

def get_quizes():
    '''Возвращает список викторин (id, name)
    можно брать только викторины, в кот есть вопросы'''
    query = '''SELECT DISTINCT q.id id, q.qName name
    FROM quiz q
    inner join relQQ rqq on rqq.quiz_id = q.id
    ORDER BY q.id'''
    #если убрать дистинкт, будут повторы в таблце, дублируется таблица викторин
    #inner - объединяет по и (не или), на пересеении двух таблиц(пересечение множеств)
    #в каждой викторине по два вопроса, они и пересекаются
    #join присоединяет таблица quiz q и таблица relQQ
    #rqq.quiz_id = q.id значение поля таблицы отношений должно сооветсвовать полю таблицы виккторин
    open()
    cursor.execute(query)
    result = cursor.fetchall()#получаем все строки
    close()
    print(result)
    return result

def get_rec_count(aTableName='quiz', aWhere=''):
    open()
    query= '''
            select
                count(*)
            from ''' + aTableName + aWhere
    cursor.execute(query)
    result = cursor.fetchone()
    close()
    return result      #из этого результата и выбираем нулевой элемент     .Функция достает количество 


def clear_db():
    ''' удаляет все таблицы '''
    open()
    query = '''DROP TABLE IF EXISTS quiz_content'''
    do(query)
    query = '''DROP TABLE IF EXISTS question'''
    do(query)
    query = '''DROP TABLE IF EXISTS quiz'''
    do(query)#исполняет запрос который  в нее переедаем ,исполняет коммит
    close()

    
def create():
    open()#1
    do('''PRAGMA foreign_keys=on''')#3
    #СОЧИНЯЕМ ЗДЕСЬ ЗАПРОСЫ
    query = '''
    CREATE TABLE IF NOT EXISTS quiz(
        id INTEGER PRIMARY KEY,
        name VARCHAR
    )
    '''
    do(query)
    query = '''
    CREATE TABLE IF NOT EXISTS question(
        id INTEGER PRIMARY KEY,
        text VARCHAR,
        answer VARCHAR,
        wrong1 VARCHAR,
        wrong2 VARCHAR,
        wrong3 VARCHAR
    )
    '''
    do(query)#выполнить запрос создания квестион
    #создаем квиз контент
    query = '''
    CREATE TABLE IF NOT EXISTS quiz_content(
        id INTEGER PRIMARY KEY,
        quiz_id INTEGER,
        question_id INTEGER,
        FOREIGN KEY (quiz_id) REFERENCES quiz (id),
        FOREIGN KEY (question_id) REFERENCES question (id)
    )
    '''
    do(query)#выполнитт запрос создания квиз контента
    close()#2

 #получать все варианты ответов gj pfghjce
def getAnswers(question_id=1):
    open()
    query = '''
            select
                a.text,
                a.id
            from
                answer a
            where
                a.question_id = ?
            '''
    cursor.execute(query, [question_id]) #выполнить запрос
    result = cursor.fetchall() #фечол - все
    close()#не забываем закрывать сессию, может быть ограниченное кол-во сесс на серв
    return result  

#получить следующий вопрос
def getQuestion(question_id, quiz_id):
    open()
    query = '''
            select
                q.text,
                q.id
            from
                question q
                left join relQQ qq on qq.question_id == q.id
            where
                qq.quiz_id == ?
                and q.id > ?
            '''
    cursor.execute(query, [quiz_id, question_id]) #выполнить запрос
    result = cursor.fetchone() 
    close()#не забываем закрывать сессию, может быть ограниченное кол-во сесс на серв
    return result                

#вычисляет правильность по Ид из табл ответов, где ид ответа выбрать изтру
def getAnswerIsTrue(answer_id='1'):
    open()
    query = '''
            select
                a.isTrue
            from
                answer a 
            where
                a.id = ?
            '''
    cursor.execute(query, [answer_id]) #выполнить запрос
    result = cursor.fetchone()[0]>0 #положим условный результат/ проверка не существующего ответа не возьмется
    #cursor.fetchone() - кортеж, из него вытаскиваем, все что больше 0 - истина
    close()#не забываем закрывать сессию, может быть ограниченное кол-во сесс на серв
    return result                     

def add_question():
    #список кортежей.кортеж -это один элемент списка. Cписок состоит из трех кортежей
    question = [
        ('Вопрос1', 'Правильный', 'Неправильный1', 'Неправильный2', 'Неправильный3'),
        ('Вопрос2', 'Правильный', 'Неправильный1', 'Неправильный2', 'Неправильный3'),
        ('Вопрос3', 'Правильный', 'Неправильный1', 'Неправильный2', 'Неправильный3')
    ]
    open()
    doMany('''
    INSERT INTO question
    (text, answer, wrong1, wrong2, wrong3)
    VALUES
    (?,?,?,?,?)
    ''', question)
    close()

def add_quiz():
    quiz = [
        ('Викторина1',),
        ('Викторина2',)
    ]
    open()
    doMany('''
    INSERT INTO quiz
    (name)
    VALUES
    (?)
    ''', quiz)
    close()

def add_links():
    links = [
        (1, 1),
        (1, 2),
        (2, 2),
        (2, 3)
    ]
    open()
    doMany('''
    INSERT INTO quiz_content
    (quiz_id, question_id)
    VALUES
    (?, ?)
    ''', links)
    close()    

def show(table):#выводит данные из таблиц по порядку
    query = 'SELECT * FROM ' + table
    open()
    cursor.execute(query)
    print(cursor.fetchall())
    close()

def show_tables():
    show('question')
    show('quiz')
    show('quiz_content')




def main():
    #clear_db()
    #create()
    #add_question()
    #add_quiz()
    #add_links()
    show_tables()

if __name__ == "__main__":
    main()
