## Итоговая работа
## 12448/1 ИНЖДАН МГТУ им. Н.Э. Баумана
## Инженер данных (Data engineer)
## Андреев Андрей Анатольевич

## КЛАССИФИКАЦИЯ ГОСКОНТРАКТОВ ПО ОБЪЕКТАМ ЗАКУПКИ

### Задача: необходимо на основе данных с ftp.zakupki.gov.ru научиться определять группу, к которой относится контракт с кодом ОКПД-2 41, 42, 43, 71.1.

Группы могут быть следующими:

1.	Строительно-монтажные работы (СМР)
2.	Проектно-изыскательские работы (ПИР)
3.	Строительный надзор
4.	Подключение коммуникаций
5.	Прочее.

По ОКПД-2 контракты в общем случае должны разделяться так:
- Строительно-монтажные работы (СМР) - 41, 42, 43(кроме нижеперечисленных)
- Проектно-изыскательские работы (ПИР) - 41.1, 71.1
- Подключение коммуникаций - 43.22
- Строительный надзор – четкой группы нет.


Проблема: Далеко не всегда контракты указываются с нужным кодом, поэтому есть проблема как такие контракты "отловить" и определить в нужную группу.

Поэтому задача предполагает классификацию контрактов на основе объекта закупки, который сформулирован естественным языком. Также предполагаем, что могут иметь значение цена контракта и его длительность.
На основе этого на входе данные о контрактах. На выходе необходимо получить группу для каждого контракта.

Иногда контракт может относиться одновременно в несколько групп.

В приложении ниже пример нескольких контрактов, у которых неверно проставлен ОКПД-2.



# Отчет о проделанной работе

В процессе работы были выполнены шаги:

![alt text](dfd.png "Title")

1. Загрузка csv файла объемом 25Гб. Поскольку файл не помещался в памяти, было приняло решение загрузить его в базу данных. В процессе загрузки данные загружались порциями, при возникновении исключений, строка отбрасывалась. В базу данных загружал только необходимые признаки:
- contract_number (номер контракта), 
- object_name (наименование услуги),
- object_code (код услуги), 
- cost (стоимость), 
- contract_execution_days (длительность контракта в днях -  рассчитывался как разница дат начала и окончания контракта).

2. Провел разведочный анализ данных. Сделал очистку данных от дублей и пропусков, а также от пустых строк и латинских символов. Поскольку в данных нет явной разметки, принял решение выполнить кластеризацию
данных, а уже кластеризованные данные в качестве разметки использовать для обучения модели классификатора.

3. Для выполнения классификации по наименованию услуги был выполнен NLP процесс  (токкенизация, лемматизация, стеминг, удаление стоп слов и знаков пунктуации). 

4. Выполнил кластеризацию  по наименованию услуги. Для этого уже разобранный текст (nlp) на предыдущем шаге был векторизован с помощью TfidfVectorizer. К полученным признакам добавлены стоимость за день и группа контракта (как задано в условии). Группа была закодирована с помощью OneHotEncoder. Признаки были нормализованы с помощью MinMaxScaler.

Услуги распределились по кластеру, визуально видно, что описание услуги соответствует кластеру. Но, полученные кластера не совсем соответствуют группам по условию. Возможно, не обходимо либо пересмотреть группировку кодов и обратится за помощью к специалисту из предметной области для уточнения ТЗ. В итоге, было принято решение обучить модель классификации, а в качестве метки использовать кластер.

Выполнена задача по классификации определения группы, к которой относится контракты. Классификация была выполнена с использованием разных моделей:
- Нейронная сеть c помощью библиотеки TensorFlow.
- Градиентный бустинг с помощью библиотеки CatBoost.
- Логистическая регрессия с помощью библиотеки sklearn.

Как показали эксперименты, лучше всего показала классическая модель машинного обучения - логистическая регрессия. Она показала лучшую точность 0.865 и производительность (скорость обучения). 
При обучении модели логистической регрессии подбирались гипперпараметры с помощью GridSearchCV. 

Есть ошибки в неправильной классификации. Возможно необходимо уточнить в ТЗ правильность группировки кодов ОКПД-2.


# Вывод

Анализ датасета показал, что он не размечен, нет признаков явно указывающих, какой код и группа верные, а какой нет. Поэтому, можно провести разметку, прибегнув к кластеризации.

Если предположить, что количество некорректных кодов ОКПД-2 большое, тогда выполним кластеризацию данных по столбцу с описанием контракта. На основе полученной кластеризации, получаем размеченные данные, с помощью которых, можно обучить модель классификации с учетом стоимости и количества дней исполнения контракта.

Выполнена задача по классификации определения группы, к которой относится контракт с кодом ОКПД-2.
В качестве модели выбрал алгоритм логистической регрессии. В результате проделанной работы был разработан классификатор групп кодов ОКПД-2 с точность предсказания 0.865, что соответствует заданию.





