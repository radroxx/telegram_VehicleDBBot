"""Main handler"""
import time
import json
from .cache import cache_init
from .platerecognizer import platerecognizer_plate_reader
from .telegram import (
    telegram_send_message,
    telegram_get_file_url,
    telegram_send_photo
)
from .database import (
    _db_create_tables,
    db_get_vehicle_image,
    db_put_vehicle_image,
    db_get_vehicle,
    db_put_vehicle,
    db_get_user,
    db_put_user,
    db_get_vehicle_raiting,
    db_put_vehicle_raiting,
    db_get_checks_log_last,
    db_put_checks_log
)


def get_images(photos):
    size = 0
    big_image = None
    images = []

    for image in photos:
        images.append(image["file_unique_id"])
        if image["file_size"] > size:
            size = image["file_size"]
            big_image = image["file_id"]
    
    return images, big_image


def detect_plates_in_image(message, force = False):
    image_uniq_ids, big_image_id = get_images(message["photo"])

    # Достаем из базы по id картинок
    vehicle_images = []
    for image_id in image_uniq_ids:
        vehicle_images.append( db_get_vehicle_image(image_id) )
    
    plates = []
    dscore = []

    # Достаем номера из базы
    for vehicle_image in vehicle_images:
        for plate in vehicle_image["plates"]['L']:
            if plate['S'] not in plates:
                plates.append(plate['S'])
                dscore.append(-1)
    
    # Зачищаем и перечекиваем
    if force:
        for vehicle_image in vehicle_images:
            vehicle_image["plates"]['L'] = []
        plates = []
        dscore = []

    if len(plates) > 0:
        return plates, dscore

    # Идем в platerecognizer
    file_full_url = telegram_get_file_url(big_image_id)
    responce = platerecognizer_plate_reader(file_full_url)
    if "results" in responce:
        for r_plate in responce["results"]:

            plate = "[%s] %s"%(r_plate["region"]["code"], r_plate["plate"])
            plate = plate.upper()

            # Скипаем все что ниже порога
            if r_plate["dscore"] > 0.6 or force is True:
                plates.append(plate)
                dscore.append(r_plate["dscore"])

    # Сохраняем в базку номера с привязкой к файлам в телеге
    if len(plates) > 0:
        for vehicle_image in vehicle_images:
            for plate in plates:
                vehicle_image["plates"]['L'].append({'S': plate})

            db_put_vehicle_image(vehicle_image)

    # Прихраним картинку в базке и проверим не забанен ли часом номерок
    ban_plates = []
    for i in range(0, len(plates)):
        vehicle = db_get_vehicle(plates[i])

        is_add_image = True
        
        for file_uniq_id_obj in vehicle["images_file_uid"]['L']:
            if file_uniq_id_obj['S'] in image_uniq_ids:
                is_add_image = False
                break
        
        if is_add_image:
            vehicle["show_images"]['L'].append({'S': big_image_id})
            for images_file_uniq_id in image_uniq_ids:
                vehicle["images_file_uid"]['L'].append({'S': images_file_uniq_id})
            db_put_vehicle(vehicle)

        if vehicle["is_hiden"]["BOOL"]:
            ban_plates.append(i)
        
    ban_plates = sorted(ban_plates, reverse=True)
    for i in ban_plates:
        del plates[i]
        del dscore[i]
        
    return plates, dscore


def send_message(text, message):
    if message["chat"]["type"] == "supergroup":
        return {"statusCode": 200, "body": "True"}
    telegram_send_message(message["chat"]["id"], text, message["message_id"])
    return {"statusCode": 200, "body": "True"}


def handler(event, context):
    """Handler"""

    if event is None and context is None:
        return {"statusCode": 200, "body": "True"}

    if event.get("headers", {}).get("Content-Type") != "application/json":
        return {'statusCode': 200, 'body': 'True'}

    body = json.loads(event.get("body", "{}"))

    if not body:
        return {'statusCode': 200, 'body': 'True'}

    cache_init()
    _db_create_tables()

    message = body["message"]
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    chat_type = message["chat"]["type"] # private, group, supergroup
    from_user_id = message["from"]["id"]
    from_user_first_name = message["from"]["first_name"]

    is_show_reply = True
    if chat_type == "supergroup":
        is_show_reply = False

    # Bot command extract
    bot_command = None
    bot_command_args = []

    for entitie in message.get("entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["text"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args = message["text"][entitie["length"] + 1:].split(' ')

    for entitie in message.get("caption_entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["caption"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args = message["caption"][entitie["length"] + 1:].split(' ')
    # Bot Command extract

    # /version
    if bot_command == "version":
        return send_message("0.0.3", message)

    # /images [gb] 5B314
    if bot_command == "images":
        if len(bot_command_args) == 0:
            return send_message("Укажите номер авто.", message)

        plate = " ".join(bot_command_args).upper()
        vehicle = db_get_vehicle(plate)

        # Авто скрыто
        if vehicle["is_hiden"]["BOOL"] == True:
            return send_message("Барин нежелает демонстрировать свое авто.", message)

        images = []
        for image in vehicle["show_images"]['L']:
            images.append(image['S'])

        if len(images) == 0:
            return send_message("У меня в базе нет такого номера.", message)

        # В приватном чате показываем все фото
        if chat_type == "private":
            telegram_send_photo(chat_id, images, message_id)
            return {"statusCode": 200, "body": "True"}

        # Груповой чат, ограничиваем поиск авто из чата
        last_check = db_get_checks_log_last(chat_id, plate)
        if len(last_check) == 0:
            return send_message("У меня в базе нет такого номера.", message)

        telegram_send_photo(chat_id, images, message_id)

        return {"statusCode": 200, "body": "True"}

    # Просто фото
    if "photo" in message and bot_command is None:
        plates, dscore = detect_plates_in_image(message)
        
        telegram_send_message(chat_id, "%s | %s"%(plates, dscore), message_id)

        message = ""
        for i in range(0, len(plates)):
            last_check = db_get_checks_log_last(chat_id, plates[i])
            db_put_checks_log(chat_id, time.time(), plates[i], from_user_id, message_id, is_show_reply)
            print(last_check)
            if len(last_check) == 0:
                # Небыло еще
                # Юзер молодец прислал уникальную фотку
                user = db_get_user(chat_id, from_user_id)
                user["raiting"]['N'] += 1
                db_put_user(user)

                message += "Номер " + plates[i] + ""
                message += "Номер [HU] FNJ732 вижу впервые в этом чате."
                message += "Рейтинг толькозователя увеличен на 1"
            
            else:
                # Было уже
                # Ммм популярная тачка
                vehicle_raiting = db_get_vehicle_raiting(chat_id, plates[i])
                vehicle_raiting["raiting"]['N'] += 1
                db_put_vehicle_raiting(vehicle_raiting)


        telegram_send_message(chat_id, "finish", message_id)

    return {"statusCode": 200, "body": "True"}
