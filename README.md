# Что тут происходит
Вы находитесь в репозитории бота, реализующего функциональность Тайного Санты в Дискорд с подарками в виде игр в Стим. Распределение игр с учётом любимых жанров, уже имеющихся в библиотеке предметов и производительности компьютера пользователя.

**Сейчас бот работает с небольшим количеством подарков, примерно до двадцати штук**, после чего **блокируется Стимом**. Это можно исправить, добавив работу с несколькими токенами, но сейчас такая функциональность не реализована. Разработка завершалась в ограниченные сроки, поэтому небольшая часть кода написана плохо: много что захардкожено и предполагается к приведению в божеский вид.

# Общее устройство
Бот имеет структуру, состоящую из "режимов работы", которые не должны быть включены одновременно. Каждый режим берёт полный контроль над ботом и не воздействует на результаты работы других режимов. Предполагается, что режимы должны запускаться по порядку: первый, потом второй, потом третий, и так далее.

## Режимы работы
Режим выбирается в файле main.py

- Сбор подарков
- Фаза подготовки к раздаче
- Раздача подарков
- Завершение, отправка финального сообщения

### Сбор подарков
Бот работает в ЛС и имеет единственную команду /gift. Пользователю предлагается выбрать и оплатить игру, реализован паттерн "цепочка обязанностей", в каждом хендлере происходит какое-то одно действие: выбор игры, указание жанров, производительности, требовательности и так далее. Установлена минимальная сумма подарка в пятьсот рублей, в подарке может быть сколько угодно игр, но минимальная стоимость игры - десять рублей.

### Подготовка к раздаче
Бот отправляет запросы в друзья участникам ивента.

### Раздача подарков
Бот раздаёт подарки согласно алгоритму.

### Завершение работы
Бот отправляет сообщение о завершении ивениа всем участникам. Текст захардкожен, но может быть легко вынесен в strings.json


# О разработке и поддержке
Продолжение разработки не ожидается по крайней мере до следующего Нового года, причём не факт, что бот будет доработан вообще. 

Не уверен, что нужны подробности и документация, но могу написать, если кому-то окажется полезно. Создавайте issue - сделаю. 
