# Здесь будет код веб-приложения
from random import randint
from flask import Flask, session, redirect, url_for, request, render_template
from db_scripts import *
import os
#render_template - шаблоны, test например
#получитть путь к нашим файлам, чтоб сервер знал где хр данные


#умеет делать гет или уметь обрабатывать пост
def test():
    if request.method == 'GET':
        '''возвращает страницу вопроса'''
        #что если пользователь без выбора викторины пошел сразу на адрес '/test'?
        if not ('quiz' in session) or int(session['quiz']) < 0:
            return redirect(url_for('index'))
        else:
            #тут пока старая версия функции:
            result = getQuestion(session['last_question'], session['quiz']) #достает запрос по id   
            if result is None or len(result) == 0:
                return redirect(url_for('result'))
            else:
                session['last_question'] = result[1]# сохраняем текущий id вопроса
                answList = getAnswers(session['last_question'])#получаем список ответов на эт вопр
                #если мы научили базу возвращать Row или dict, то надо писать не result[0], а result['id']
                return render_template('test.html', quest=result[0], answList=answList)
                #если мы научили базу возвращать Row или dict, то надо писать не result[0], а
                #return '<h1>' + str(session['quiz']) + <br>' + str(result) + '</h1>'
    else:
        answerId = request.form.get('answer') #выбрать номер викторины .строковое значение - ошибка, в шаблоне иное, если вэлью в кавычках - это строка, строку не надо преобразовывать к строке
        isTrueAnswer = getAnswerIsTrue(answerId)#проверять истинность ответа
        if isTrueAnswer:
            session['countT'] +=1#если правльно увеличиваем счетчик, если не правльно ничего не делаем
        return redirect(url_for('test'))  


def start_quiz(quiz_id): #готовит первоначальную сессию
    '''создает нужные значения в словаре session'''
    session['quiz'] = quiz_id #сохранияем текущий
    session['last_question'] = 0 #нулевой вопрос
    #если что-то уже выбрали меняем счетчик
    #считаем сколько вопросов в этом квизе, для итога в конце
    if int(quiz_id) > -1:
        session['countQ'] = get_rec_count('question', '''
        q left join RelQQ rqq on rqq.question_id == q.id
        WHERE rqq.quiz_id = ''' + str(session['quiz']))[0]
    else:
        session['countQ'] = 0 #колво вопросов
    session['countT'] = 0 #количество ПРАВИЛЬНЫХ ответов когда стартуем
#берется из dbскрипта

#создает страницу, рендерится, на основании шаблона страницы старт, на данную страницу передает qlist - список всех квизов
#а в список от куда -  передаем параметры имя и значение q_list=q_list
def quiz_form():
    '''функция получает список викторин из базы и формирует форму с выпадающим списком'''
    q_list = get_quizes()
    return render_template('start.html', q_list=q_list)


#функция кот формирует старинцу индекс ,кот отображается при вх-е на гл страницу сайта
def index():
    ''' Первая страница: ешли пришлти запросом гет, то выбирать викторину,
    если post - то запомнит id викторины и отправлять на вопросы'''
    if  request.method == 'GET':
        #викторина не выбрана, сбрасываем id викторины и показываем форму выбора
        start_quiz(-1)
        return quiz_form() # функция кот на осн хтмл формирует страницу
    else:
        #получили доп данные в запросе! Используем их:
        quiz_id = request.form.get('quiz') #выбранный номер викторины
        start_quiz(quiz_id)#отправили на сервер id, а выше request.form.get('quiz') принимаем
        return redirect(url_for('test')) #переход на др страницу тест

def result():
    if  request.method == 'GET':
        return render_template('result.html', trueAnswers=session['countT'], allAnswers=session['countQ'])
    else:
        return redirect(url_for('index'))

#Пишем исполняеемый код
#Cоздаем объект веб приложения:
folder = os.getcwd() #заполнили текущую рабочую папке
#Cоздаем объект веб приложения:
app = Flask(__name__, template_folder=folder, static_folder=folder)
app.add_url_rule('/', 'index', index) #создает правило для URL '/'
#создает правило для '/index'
app.add_url_rule('/index', 'index', index, methods=['post', 'get'])
#создает правило для '/test'
app.add_url_rule('/test', 'test', test, methods=['post', 'get']) #пост - когда пользователь нажал ответить
#создает правило для URL '/result'
app.add_url_rule('/result', 'result', result, methods=['post', 'get'])

#устанавливаем ключ шифрования: для сессии. обязательно. 
app.config['SECRET_KEY'] = 'ThisIsSecretSecretSecretLife'
if __name__ == '__main__':
    #Запускаем веб-сервер:
    app.run()



