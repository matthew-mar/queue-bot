source ./bot-venv/bin/activate

python ./queue_bot/manage.py runserver &
server=$!
echo "запуск сервера" $server
echo $server >> ./pids.txt

python ./queue_bot/manage.py chat_bot_run &
chat_bot=$!
echo "запуск чат бота" $chat_bot
echo $chat_bot >> ./pids.txt

python ./queue_bot/manage.py dialog_bot_run &
dialog_bot=$!
echo "запуск диалогового бота" $dialog_bot
echo $dialog_bot >> ./pids.txt
