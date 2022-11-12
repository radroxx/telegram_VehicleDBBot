import os
import json
import urllib3
import database as db


def request_json(method, url, fields, headers = {}):
    
    with urllib3.PoolManager() as pool:
        r = pool.request(method, url, headers=headers, fields=fields)
        return r.status, json.loads(r.data)
    
    return None, None
    

def telegram_send_message(text, chat_id, reply_to = None):

    fields = {
        'chat_id': chat_id,
        'text': text
    }

    if reply_to is not None:
        fields['reply_to_message_id'] = reply_to
    
    return request_json(
        'POST', 
        'https://api.telegram.org/bot' + os.getenv('TELEGRAM_BOT_API') + '/sendMessage',
        fields
        )


def telegram_send_photo(photo, chat_id, reply_to = None):

    fields = {
        'chat_id': chat_id,
        'photo': photo
    }

    if reply_to is not None:
        fields['reply_to_message_id'] = reply_to
    
    return request_json(
        'POST', 
        'https://api.telegram.org/bot' + os.getenv('TELEGRAM_BOT_API') + '/sendPhoto',
        fields
        )


def telegram_get_file(file_id):
    
    status, body = request_json(
        'POST', 
        'https://api.telegram.org/bot' + os.getenv('TELEGRAM_BOT_API') + '/getFile',
        {'file_id': file_id}
    )
    
    if status == 200 and body is not None:
        return "https://api.telegram.org/file/bot" + os.getenv('TELEGRAM_BOT_API') + "/" + body['result']['file_path']

    return None


def lambda_get_photo_file_id_from_message(message):
    file_id = None
    
    if 'photo' in message:
        width = 0
        for file in message['photo']:
            if file['width'] < width:
                continue
            width = file['width']
            file_id = file['file_id']
    
    return file_id


def lambda_reply_and_exit(message, body):
    telegram_send_message(message, body['message']['chat']['id'], body['message']['message_id'])
    return {'statusCode': 200, 'body': 'True'}


def platerecognizer_plate_reader(file_path):
    
    status, body = request_json(
        'POST',
        'https://api.platerecognizer.com/v1/plate-reader/',
        headers={'Authorization': 'Token ' + os.getenv('PLATERECOGNIZER_API')},
        fields={
            'regions': 'lt',
            'upload_url': file_path
        }
    )
    
    if status == 201 and body is not None:
        return body

    return None


def lambda_check_image(message, force = False, silent = False, verbose = True):
    file_id = lambda_get_photo_file_id_from_message(message)
    if file_id is None:
        return

    vehicles = []
    if force == False:
        vehicles += db.get_vehicle_by_image(file_id)

    if len(vehicles) == 0:
        file_path = telegram_get_file(file_id)
        if file_path is None: return
        
        plate_data = platerecognizer_plate_reader(file_path)
        if 'results' not in plate_data or len(plate_data['results']) == 0:
            if silent == False and verbose == True:
                telegram_send_message(
                    "На фото нет номерных знаков.", 
                    message['chat']['id'],
                    message['message_id']
                )
            return
    
        for car in plate_data['results']:
            plate = "[{}] {}".format(car['region']['code'], car['plate']).upper()
            vehicles.append( db.get_vehicle(plate) )

    for vehicle in vehicles:
        plate = vehicle['plate']['S']
        last_found_day = db.get_last_update(vehicle, message['chat']['id'])
        
        db.update_last_found(vehicle, message['chat']['id'])
        db.add_images(vehicle, file_id)
        db.save_vehicle(vehicle)
        
        if silent == False:
            if last_found_day != None:
                telegram_send_message(
                    "Номер {} баян, было уже {} дней назад. #{}".format(plate, last_found_day, len(vehicle['images']['L'])), 
                    message['chat']['id'],
                    message['message_id']
                )
            else:
                telegram_send_message(
                    "Номер {} вижу впервые в этом чате.".format(plate), 
                    message['chat']['id'],
                    message['message_id']
                )


def lambda_handler(event, context):
    
    if 'headers' not in event:
        return {'statusCode': 200, 'body': 'True'}
        
    if 'Content-Type' not in event['headers']:
        return {'statusCode': 200, 'body': 'True'}

    if event['headers']['Content-Type'] != 'application/json':
        return {'statusCode': 200, 'body': 'True'}

    if 'body' not in event:
         return {'statusCode': 200, 'body': 'True'}

    body = json.loads(event['body'])
    
    if 'message' not in body:
        return {'statusCode': 200, 'body': 'True'}

    # /images
    if 'text' in body['message'] and body['message']['text'].startswith('/images'):
        plate = body['message']['text'][8:]
        if len(plate) == 0:
            return lambda_reply_and_exit('Укажите номер', body)
        if not db.is_exist(plate):
            return lambda_reply_and_exit('Такой номер не найден', body)

        for img in db.get_vehicle(plate)['images']['L']:
            telegram_send_photo(img['S'], body['message']['chat']['id'], body['message']['message_id'])

        return {'statusCode': 200, 'body': 'True'}

    # /check
    if 'text' in body['message'] and body['message']['text'].startswith('/check'):
        if 'reply_to_message' not in body['message']:
            #return lambda_reply_and_exit('Немогли бы вы прислать хотя бы фото', body)
            return {'statusCode': 200, 'body': 'True'}

        force = False
        if body['message']['text'][7:] == 'force':
            force = True

        print(event)
        lambda_check_image(body['message']['reply_to_message'], force)

        return {'statusCode': 200, 'body': 'True'}

    if 'photo' in body['message']:
        print(event)
        lambda_check_image(body['message'], silent = False, verbose = False)
        return {'statusCode': 200, 'body': 'True'}

    return {'statusCode': 200, 'body': 'True'}
