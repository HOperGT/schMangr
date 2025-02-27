# import requests
# from config import TOKEN

# def send_message_to_telegram(telegram_id, message):
#     url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
#     data = {
#         'chat_id': telegram_id,
#         'text': str(message),
#     }
#     requests.post(url, json=data)

# send_message_to_telegram(1441658354, 'Работает?ХММММ')