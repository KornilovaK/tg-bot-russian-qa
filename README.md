# (QAcumber)[https://t.me/ru_qa_bot] - tg bot for Russian Question answering 

![Logo](images.jpeg "QAcumber logo")

## Models
go to [prepare_data_train_model](prepare_data_train_model) to learn about making a dataset, training models and evaluation results

## Чтобы развернуть docker контейнер (docker dekstop уже установлен на пк):
* Через терминал клонируем репозиторий git clone https://github.com/KornilovaK/tg-bot-russian-qa.git
* В docker-compose.yml изменяем BOT_TOKEN на свой, полученный через телеграмм бота BotFather, при создании своего бота (без кавычек!)
* Из основной директории переходим в docker cd docker
* Чтобы "построить" контейнер: docker compose -p <название нового контейнера> -f docker-compose.yml build
* Чтобы запустить его: docker compose -p <название нового контейнера> -f docker-compose.yml up

## Notes
* Работает быстро на cpu
* Чтобы выбрать любую другую подходящую модель с HF достаточно лишь изменить название модели в docker-compose.yml

## [Демонстрация](https://drive.google.com/file/d/1tXA5SxqV_pCG2nK5iy-BTnb4M8Q_sTIl/view?usp=sharing)