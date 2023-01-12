"""Main handler"""
import time
import json
import traceback
from .cache import cache_init
from .platerecognizer import platerecognizer_plate_reader
from .telegram import (
    telegram_send_message,
    telegram_get_file_url,
    telegram_send_photo,
    telegram_get_chat_member_first_name
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
    db_put_checks_log,
    db_top_users,
    db_top_vehicles,
    db_seach_plate
)


def get_images(photos):
    """Get file_uniq_ids and bigger photo id"""
    size = 0
    big_image = None
    images = []

    for image in photos:
        images.append(image["file_unique_id"])
        if image["file_size"] > size:
            size = image["file_size"]
            big_image = image["file_id"]

    return images, big_image


def get_bot_command(message):
    """Get command and args from telegram message"""
    bot_command = None
    bot_command_args = []

    for entitie in message.get("entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["text"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args_string = message["text"][entitie["length"] + 1:]
        if len(bot_command_args_string) > 0:
            bot_command_args = bot_command_args_string.split(' ')

    for entitie in message.get("caption_entities", []):
        if entitie["type"] != "bot_command":
            continue
        bot_command = message["caption"][entitie["offset" ] + 1 : entitie["length"]].lower()
        bot_command_args_string = message["caption"][entitie["length"] + 1:]
        if len(bot_command_args_string) > 0:
            bot_command_args = bot_command_args_string.split(' ')

    return bot_command, bot_command_args


def send_message(text, message, is_debug = False):
    """Send message to tg, depect supergroup and force send if debug"""
    if message["chat"]["type"] == "supergroup" and is_debug is False:
        return {"statusCode": 200, "body": "True"}
    telegram_send_message(message["chat"]["id"], text, message["message_id"])
    return {"statusCode": 200, "body": "True"}


def up_car_raiting(chat_id, plate, max_raiting = 1):
    """Up vehicle raiting"""
    vehicle_raiting = db_get_vehicle_raiting(chat_id, plate)

    # Проверяем что бы рейтинг не был выше чем количество реальных фоток
    if vehicle_raiting["raiting"]['N'] < max_raiting:
        vehicle_raiting["raiting"]['N'] += 1
        db_put_vehicle_raiting(vehicle_raiting)


def response_accordion(plate, last_check):
    """Generates a response if plate has already been"""
    last_check_ago = int((time.time() - last_check)/86400)

    if last_check_ago == 0:
        return \
            f"Эх ты голова дырявая, 24 часа еще не прошло, а ты уже забыл что {plate} скидывали.\n"
    if last_check_ago == 1:
        return f"Кажеться я уже видел вчера {plate} в этом чате.\n"

    return f"Кажеться я уже видел {plate} в этом чате {last_check_ago} дней тому.\n"


def detect_plates_in_image(message, force = False):
    """Detect plates in image"""
    image_uniq_ids, big_image_id = get_images(message["photo"])

    # Достаем из базы по id картинок
    vehicle_images = []
    for image_id in image_uniq_ids:
        vehicle_images.append( db_get_vehicle_image(image_id) )

    plates = []
    dscore = []
    vehicles = []

    # Достаем номера из базы
    for vehicle_image in vehicle_images:
        for plate in vehicle_image["plates"]['L']:
            if plate['S'] not in plates:
                plates.append(plate['S'])
                dscore.append(-1)
                vehicles.append(db_get_vehicle(plate['S']))

    # Зачищаем и перечекиваем
    if force:
        for vehicle_image in vehicle_images:
            vehicle_image["plates"]['L'] = []
        plates = []
        dscore = []
        vehicles = []

    if len(plates) > 0:
        return plates, dscore, vehicles

    # Идем в platerecognizer
    file_full_url = telegram_get_file_url(big_image_id)
    responce = platerecognizer_plate_reader(file_full_url)
    if "results" in responce:
        for r_plate in responce["results"]:

            plate = "[" + r_plate["region"]["code"] + "] " + r_plate["plate"]
            plate = plate.upper()

            # Скипаем все что ниже порога
            if r_plate["dscore"] > 0.6 or force is True:
                plates.append(plate)
                dscore.append(r_plate["dscore"])
                vehicles.append(db_get_vehicle(plate))

    # Сохраняем в базку номера с привязкой к файлам в телеге
    if len(plates) > 0:
        for vehicle_image in vehicle_images:
            for plate in plates:
                vehicle_image["plates"]['L'].append({'S': plate})

            db_put_vehicle_image(vehicle_image)

    # Прихраним картинку в базке и проверим не забанен ли часом номерок
    ban_plates = []
    i = 0
    for vehicle in vehicles:

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

        i += 1

    ban_plates = sorted(ban_plates, reverse=True)
    for i in ban_plates:
        del plates[i]
        del dscore[i]
        del vehicles[i]

    return plates, dscore, vehicles


def handler(event, context):
    """Handler"""

    is_develop = (__name__.split('.', maxsplit=1)[0] == "develop")

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


    try:

        message_id = message["message_id"]
        chat_id = message["chat"]["id"]
        chat_type = message["chat"]["type"] # private, group, supergroup
        from_user_id = message["from"]["id"]

        is_show_reply = True
        if chat_type == "supergroup":
            is_show_reply = False

        # Bot command extract
        bot_command, bot_command_args = get_bot_command(message)
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
            if vehicle["is_hiden"]["BOOL"] is True:
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

        # /topuser
        if bot_command == "topuser":
            if chat_type == "private":
                return send_message("Солнышко ты тут единственный и неповторимый.", message)
            limit = 10
            if len(bot_command_args) > 0:
                limit = int(bot_command_args[0])

            top_users = db_top_users(chat_id, limit)
            responce_message = ""
            for user in top_users:
                responce_message += "<a href=\"tg://user?id="
                responce_message += str(user["user_id"]["N"])
                responce_message += "\">"
                responce_message += telegram_get_chat_member_first_name(
                    chat_id, user["user_id"]["N"]
                )
                responce_message += "</a> рейтинг " + user["raiting"]["N"] + "\n"

            telegram_send_message(chat_id, responce_message, message_id)
            return {"statusCode": 200, "body": "True"}

        # /topvehicle
        if bot_command == "topvehicle":
            limit = 10
            if len(bot_command_args) > 0:
                limit = int(bot_command_args[0])

            top_vehicles = db_top_vehicles(chat_id, limit)
            if len(top_vehicles) == 0:
                telegram_send_message(chat_id, "Тут пока пусто.", message_id)
                return {"statusCode": 200, "body": "True"}

            responce_message = ""
            for vehicle in top_vehicles:
                responce_message += "<code>"
                responce_message += vehicle["plate"]['S']
                responce_message += "</code> рейтинг <b>"
                responce_message += str(vehicle["raiting"]['N'])
                responce_message += "</b>\n"

            telegram_send_message(chat_id, responce_message, message_id)
            return {"statusCode": 200, "body": "True"}

        # /search
        if bot_command == "search":
            if len(bot_command_args) == 0:
                return send_message("Укажите номер авто или часть номера", message)

            plate_conditions = []
            for arg in bot_command_args:
                plate_conditions.append(arg.upper())

            vehicle_raitings = []
            if chat_type == "private":
                vehicle_raitings = db_seach_plate(plate_conditions)
            else:
                vehicle_raitings = db_seach_plate(plate_conditions, chat_id)

            if len(vehicle_raitings) == 0:
                return send_message("У меня таких номеров нет.", message)

            responce_message = ""
            for vehicle_raiting in vehicle_raitings:
                responce_message += "<code>"
                responce_message += vehicle_raiting["plate"]['S']
                responce_message += "</code> рейтинг "
                responce_message += str(vehicle_raiting["raiting"]['N'])
                responce_message += "\n"
            telegram_send_message(chat_id, responce_message, message_id)
            return {"statusCode": 200, "body": "True"}

        # /check without photo
        if bot_command == "check" and "photo" not in message:
            is_check = True
            is_force = "force" in bot_command_args
            is_debug = "debug" in bot_command_args

            if "reply_to_message" not in message:
                return send_message("А что чекать то ?", message, is_debug)

            reply_message = message["reply_to_message"]

            if "photo" not in reply_message:
                return send_message("А что чекать то ?", message, is_debug)

            plates, dscore, vehicles = detect_plates_in_image(reply_message, is_force)

            if len(plates) == 0:
                return send_message("На фото номеров не найденно.", message, is_debug)

            user = db_get_user(chat_id, reply_message["from"]["id"])
            user_raiting = user["raiting"]['N']
            responce_message = ""

            for i in range(0, len(plates)):
                last_check = db_get_checks_log_last(chat_id, plates[i])
                if is_check:
                    db_put_checks_log(
                        chat_id, time.time(), plates[i], from_user_id, message_id, True
                    )
                else:
                    db_put_checks_log(
                        chat_id, time.time(), plates[i], from_user_id, message_id, is_show_reply
                    )

                # # Докинем рейтинга машинке, но не больше чем реальных фоток
                up_car_raiting(chat_id, plates[i], len(vehicles[i]["show_images"]['L']))

                plate_string = "<code>" + plates[i] + "</code>"
                if is_debug:
                    plate_string += " (" + str(dscore[i]) + ")"

                # Если номер не чекался до этого или чекался но не показывался
                if len(last_check) == 0 or last_check[0]["is_show_reply"]["BOOL"] is False:
                    # Небыло еще
                    # Юзер молодец прислал уникальный номер
                    user["raiting"]['N'] += 1
                    responce_message += "Номер " + plate_string + " вижу впервые в этом чате.\n"
                else:
                    # Было уже
                    responce_message += response_accordion(
                        plate_string, last_check[0]["timestamp"]['N']
                    )

            user_raiting_diff = user["raiting"]['N'] - user_raiting
            if user_raiting_diff > 0:
                db_put_user(user)
                responce_message += "Рейтинг <a href=\"tg://user?id="
                responce_message += reply_message["from"]["id"]
                responce_message += "\">"
                responce_message += reply_message["from"]["first_name"]
                responce_message += "</a> +"
                responce_message += str(user_raiting_diff)
                responce_message += " ("
                responce_message += str(user["raiting"]['N'])
                responce_message += ")!"

            return send_message(responce_message, message, is_check)

        # Просто фото
        if "photo" in message:

            is_check = bot_command == "check"
            is_force = "force" in bot_command_args
            is_debug = "debug" in bot_command_args

            plates, dscore, vehicles = detect_plates_in_image(message, is_force)

            if len(plates) == 0:
                return send_message("На фото номеров не найденно.", message, is_check)

            user = db_get_user(chat_id, from_user_id)
            user_raiting = user["raiting"]['N']
            responce_message = ""
            for i in range(0, len(plates)):
                last_check = db_get_checks_log_last(chat_id, plates[i])
                if is_check:
                    db_put_checks_log(
                        chat_id, time.time(), plates[i], from_user_id, message_id, True
                    )
                else:
                    db_put_checks_log(
                        chat_id, time.time(), plates[i], from_user_id, message_id, is_show_reply
                    )

                # Докинем рейтинга машинке, но не больше чем реальных фоток
                up_car_raiting(chat_id, plates[i], len(vehicles[i]["show_images"]['L']))

                plate_string = "<code>" + plates[i] + "</code>"
                if is_debug:
                    plate_string += " (" + str(dscore[i]) + ")"

                if len(last_check) == 0:
                    # Небыло еще
                    # Юзер молодец прислал уникальный номер
                    user["raiting"]['N'] += 1
                    responce_message += "Номер " + plate_string + " вижу впервые в этом чате.\n"
                else:
                    # Было уже
                    responce_message += response_accordion(
                        plate_string, last_check[0]["timestamp"]['N']
                    )

            user_raiting_diff = user["raiting"]['N'] - user_raiting
            if user_raiting_diff > 0:
                db_put_user(user)
                responce_message += "Твой рейтинг +%s (%s)!"
                responce_message += str(user_raiting_diff)
                responce_message += " ("
                responce_message += str(user["raiting"]['N'])
                responce_message += ")!"

            return send_message(responce_message, message, is_check)

        # Return default responce
        return {"statusCode": 200, "body": "True"}

    except Exception: # pylint: disable=W0703
        responce_message = "Упс, что-то пошло не так :("
        if is_develop:
            trace_back = "\n" + traceback.format_exc()
            trace_back = trace_back.replace('&', '&amp;')
            trace_back = trace_back.replace('<', '&lt;')
            trace_back = trace_back.replace('<', '&lt;')
            responce_message += "<pre>" + trace_back + "</pre>"
        return send_message(responce_message, message)
