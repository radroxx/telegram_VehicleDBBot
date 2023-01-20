"""Main handler"""
import time
import json
import traceback
from datetime import datetime
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
    db_put_checks_log,
    db_create_checks_log,
    db_get_checks_log_by_messae_id,
    db_top_users,
    db_top_vehicles,
    db_seach_plate,
    db_get_checks_log,
)


DEFAULT_RESPONCE = {"statusCode": 200, "body": "True"}


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


def detect_plates_in_image(message, force = False): # pylint: disable=R0912
    """Detect plates in image"""
    image_uniq_ids, big_image_id = get_images(message["photo"])

    plates = {}

    # Достаем из базы по id картинок
    vehicle_images = []
    for image_id in image_uniq_ids:
        vehicle_images.append( db_get_vehicle_image(image_id) )

    if force is False:
        # Достаем номера из базы
        for vehicle_image in vehicle_images:
            for plate in vehicle_image["plates"]['L']:
                if plate['S'] not in plates:
                    plates[plate['S']] = {
                        "dscore": -1,
                        "vehicle": db_get_vehicle(plate['S'])
                    }
        if len(plates) > 0:
            return plates
    else:
        # Зачищаем те номера что уже есть
        for vehicle_image in vehicle_images:
            vehicle_image["plates"]['L'] = []

    # Идем в platerecognizer
    platerecognizer_responce = platerecognizer_plate_reader(
        telegram_get_file_url(big_image_id)
    )

    for r_plate in platerecognizer_responce.get("results", []):

        plate = "[" + r_plate["region"]["code"] + "] " + r_plate["plate"]
        plate = plate.upper()

        # Скипаем все что ниже порога
        if r_plate["dscore"] > 0.6 or force is True:
            if plate not in plates:
                plates[plate] = {}
            plates[plate]["dscore"] = r_plate["dscore"]
            plates[plate]["vehicle"] = db_get_vehicle(plate)

    # Сохраняем в базку номера с привязкой к файлам в телеге
    if len(plates) > 0:
        for vehicle_image in vehicle_images:
            for plate in list(plates.keys()):
                vehicle_image["plates"]['L'].append({'S': plate})

            db_put_vehicle_image(vehicle_image)

    # Прихраним картинку в базке и проверим не забанен ли часом номерок
    for plate in list(plates.keys()):
        vehicle = plates[plate]["vehicle"]
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
            del plates[plate]

    return plates


def response_accordion(plate, last_check):
    """Generates a response if plate has already been"""
    last_check_ago = int((time.time() - float(last_check))/86400)

    if last_check_ago == 0:
        return \
            f"Этому баяну {plate} даже 24 часов еще нет.\n"
    if last_check_ago == 1:
        return f"Я уже видел вчера {plate} в этом чате.\n"

    return f"Я уже видел {plate} в этом чате {last_check_ago} дней тому.\n"


def response_vehicle_raitings(vehicle_raitings):
    """Create message from list"""

    text = ""
    for vehicle in vehicle_raitings:
        plate = vehicle["plate"]['S']
        raiting = vehicle["raiting"]['N']
        text += f"🚗 <code>{plate}</code> рейтинг <b>{raiting}</b>\n"
    return text


def response_user_raitings(chat_id, user_raitings, users_name = None, diff = None):
    """Create message from list"""

    text = ""
    for user in user_raitings:
        user_id = int(user["user_id"]['N'])
        raiting = user["raiting"]['N']

        if users_name is None:
            users_name = {}

        if diff is None:
            diff = {}

        user_name = users_name.get(user_id, None)
        if user_name is None:
            user_name = telegram_get_chat_member_first_name(chat_id, user_id)

        diff_number = diff.get(user_id, 0)
        diff_text = ""
        if diff_number > 0:
            diff_text = f"+{diff_number} "
        if diff_number < 0:
            diff_text = f"-{diff_number} "

        text += f"👤 <a href=\"tg://user?id={user_id}\">{user_name}</a> рейтинг"
        text += f" {diff_text}<b>{raiting}</b>\n"
    return text


def telegram_bot_command_version_handler(message):
    """version handler"""
    if message["chat"]["type"] == "supergroup":
        return DEFAULT_RESPONCE
    telegram_send_message(message["chat"]["id"], "0.0.4", message["message_id"])
    return DEFAULT_RESPONCE


def telegrma_bot_command_top_vehicle_handler(message):
    """top vehicle handler"""
    _, bot_command_args = get_bot_command(message)

    limit = 10
    if len(bot_command_args) > 0:
        limit = int(bot_command_args[0])

    top_vehicles = db_top_vehicles(message["chat"]["id"], limit)
    if len(top_vehicles) == 0:
        telegram_send_message(message["chat"]["id"], "Тут пока пусто.", message["message_id"])
        return DEFAULT_RESPONCE

    responce_message = response_vehicle_raitings(top_vehicles)

    telegram_send_message(message["chat"]["id"], responce_message, message["message_id"])
    return DEFAULT_RESPONCE


def telegrma_bot_command_top_user_handler(message):
    """top user handler"""

    _, bot_command_args = get_bot_command(message)

    if message["chat"]["type"] == "private":
        telegram_send_message(
            message["chat"]["id"],
            "Солнышко ты тут единственный и неповторимый.",
            message["message_id"]
        )
        return DEFAULT_RESPONCE

    limit = 10
    if len(bot_command_args) > 0:
        limit = int(bot_command_args[0])

    top_users = db_top_users(message["chat"]["id"], limit)
    responce_message = response_user_raitings(message["chat"]["id"], top_users)

    telegram_send_message(message["chat"]["id"], responce_message, message["message_id"])
    return DEFAULT_RESPONCE


def telegram_bot_command_search_handler(message):
    """Search plate"""
    _, bot_command_args = get_bot_command(message)

    if len(bot_command_args) == 0:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"],
                "Укажите номер авто или часть номера",
                message["message_id"]
            )
        return DEFAULT_RESPONCE

    plate_conditions = []
    for arg in bot_command_args:
        plate_conditions.append(arg.upper())

    chat_id_param = message["chat"]["id"]
    if message["chat"]["type"] == "private":
        chat_id_param = None
    vehicle_raitings = db_seach_plate(plate_conditions, chat_id_param)

    if len(vehicle_raitings) == 0:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"],
                "У меня таких номеров нет.",
                message["message_id"]
            )
        return DEFAULT_RESPONCE


    responce_message = response_vehicle_raitings(vehicle_raitings)
    telegram_send_message(message["chat"]["id"], responce_message, message["message_id"])
    return DEFAULT_RESPONCE


def telegram_bot_command_images_handler(message):
    """Get omages by plate"""
    _, bot_command_args = get_bot_command(message)

    if len(bot_command_args) == 0:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"], "Укажите номер авто.", message["message_id"]
            )
        return DEFAULT_RESPONCE

    plate = " ".join(bot_command_args).upper().strip(" ")
    vehicle = db_get_vehicle(plate)

    # Авто скрыто
    if vehicle["is_hiden"]["BOOL"] is True:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"],
                "Барин нежелает демонстрировать свое авто.",
                message["message_id"]
            )
        return DEFAULT_RESPONCE

    images = []
    for image in vehicle["show_images"]['L']:
        images.append(image['S'])

    if len(images) == 0:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"],
                "У меня в базе нет такого номера.",
                message["message_id"]
            )
        return DEFAULT_RESPONCE

    # В приватном чате показываем все фото
    if message["chat"]["type"] == "private":
        telegram_send_photo(message["chat"]["id"], images, message["message_id"])
        return DEFAULT_RESPONCE

    # Груповой чат, ограничиваем поиск авто из чата

    vehicle_raiting = db_get_vehicle_raiting(message["chat"]["id"], plate)
    if vehicle_raiting["raiting"]['N'] == 0:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"],
                "У меня в базе нет такого номера.",
                message["message_id"]
            )
        return DEFAULT_RESPONCE

    telegram_send_photo(message["chat"]["id"], images, message["message_id"])
    return DEFAULT_RESPONCE


def telegram_bot_command_history(message):
    """Show check history"""
    _, bot_command_args = get_bot_command(message)

    if len(bot_command_args) == 0:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"], "Укажите номер авто.", message["message_id"]
            )
        return DEFAULT_RESPONCE

    plate = " ".join(bot_command_args).upper().strip(" ")
    vehicle = db_get_vehicle(plate)

    # Авто скрыто
    if vehicle["is_hiden"]["BOOL"] is True:
        if message["chat"]["type"] != "supergroup":
            telegram_send_message(
                message["chat"]["id"],
                "Барин нежелает демонстрировать свое авто.",
                message["message_id"]
            )
        return DEFAULT_RESPONCE

    vehicle_raiting = db_get_vehicle_raiting(message["chat"]["id"], plate)

    text = ""
    prev_timestamp = vehicle_raiting["last_check"]["N"]
    for _ in range(0, 100):
        vehicle_history = db_get_checks_log(message["chat"]["id"], prev_timestamp)

        user_id = vehicle_history["user_id"]['N']
        user_name = telegram_get_chat_member_first_name(message["chat"]["id"], user_id)

        message_id = vehicle_history["message_id"]['N']
        unsig_chat_id = str(message["chat"]["id"])[4:]
        msg_dt = datetime.fromtimestamp(vehicle_history["timestamp"]['N']).strftime('%y-%m-%d')
        text += f"🕐 {msg_dt} - 👤 <a href=\"tg://user?id={user_id}\">{user_name}</a> - "
        text += f"<a href=\"https://t.me/c/{unsig_chat_id}/{message_id}\">go to msg</a>\n"

        prev_timestamp = vehicle_history["prev_timestamp"]['N']
        if prev_timestamp == 0:
            break

    telegram_send_message(message["chat"]["id"], text, message["message_id"])

    return DEFAULT_RESPONCE


def telegram_bot_photo_process(message, force = False):
    """Processing photo"""

    if "photo" not in message:
        return []

    check_logs = db_get_checks_log_by_messae_id(
        message["chat"]["id"], message["message_id"]
    )

    if len(check_logs) > 0:
        return check_logs

    plates = detect_plates_in_image(message, force)

    if len(plates) == 0:
        return []

    user = db_get_user(message["chat"]["id"], message["from"]["id"])

    for plate in list(plates.keys()):

        user_old_raiting = user["raiting"]['N']
        vehicle_raiting = db_get_vehicle_raiting(message["chat"]["id"], plate)

        # Докинем рейтинга машинке, но не больше чем реальных фоток
        max_raiting = len(plates[plate]["vehicle"]["show_images"]['L'])
        if vehicle_raiting["raiting"]['N'] < max_raiting:
            vehicle_raiting["raiting"]['N'] += 1

        # Если номер не чекался до этого
        if vehicle_raiting["last_check"]['N'] == 0:
            # Небыло еще
            # Юзер молодец прислал уникальный номер
            user["raiting"]['N'] += 1

        check_time = time.time()
        check_time = message["date"] + (check_time - int(check_time))

        if vehicle_raiting['first_check']['N'] == 0:
            vehicle_raiting['first_check']['N'] = check_time

        item = db_create_checks_log(
            message["chat"]["id"], check_time, vehicle_raiting["last_check"]['N'],
            message["message_id"], plate, plates[plate]["dscore"],
            message["from"]["id"], user["raiting"]['N'] - user_old_raiting,
            user["raiting"]['N'], vehicle_raiting['first_check']['N'] != check_time
        )
        check_logs.append(item)

        vehicle_raiting["last_check"]['N'] = check_time
        db_put_vehicle_raiting(vehicle_raiting)

    db_put_user(user)
    return check_logs


def telegram_bot_command_check_photo_handler(message): # pylint: disable=R0912
    """Processing photo"""

    bot_command, bot_command_args = get_bot_command(message)

    is_check = bot_command == "check"
    is_debug = "debug" in bot_command_args

    if message["chat"]["type"] == "private":
        is_check = True

    tg_msg = message

    if "photo" not in message and is_check:
        tg_msg = message.get("reply_to_message", message)

    if "photo" not in tg_msg:
        # Отвечаем только если была комманда /check
        # В любом другом случае игнорируем если фоток нет
        # Если был /check в супер группе без фоток то тоже игнорим
        # /check debug - показываем всегда
        if is_debug \
            or message["chat"]["type"] == "private" \
            or (message["chat"]["type"] == "group" and is_check):
            telegram_send_message(
                message["chat"]["id"], "А что чекать то ?", message["message_id"]
            )
        return DEFAULT_RESPONCE

    check_logs = telegram_bot_photo_process(tg_msg, "force" in bot_command_args)

    if is_check is False:
        return DEFAULT_RESPONCE

    if len(check_logs) == 0:
        if is_debug \
            or message["chat"]["type"] == "private" \
            or (message["chat"]["type"] == "group" and is_check):
            telegram_send_message(
                message["chat"]["id"], "На фото номеров не найденно.", message["message_id"]
            )
        return DEFAULT_RESPONCE

    responce_message = ""

    user_raiting_diff = 0
    user_id = None
    user_raiting = 0
    hiden_user_raiting = True
    for check in check_logs:

        user_raiting_diff += check["user_raiting_diff"]['N']
        user_id = check["user_id"]['N']
        if check["user_raiting_current"]['N'] > user_raiting:
            user_raiting = check["user_raiting_current"]['N']

        plate_string = "<code>" + check["plate"]['S'] + "</code>"
        if is_debug:
            plate_string += " (" + str(check["dscore"]['N']) + ")"

        # Если номер не чекался до этого или чекался но не показывался
        if check["is_show_reply"]["BOOL"] is False:
            responce_message += "Номер " + plate_string + " вижу впервые в этом чате.\n"

            check["is_show_reply"]["BOOL"] = True
            db_put_checks_log(check)
            hiden_user_raiting = False
        else:
            # Было уже
            responce_message += response_accordion(
                plate_string, check["prev_timestamp"]['N']
            )

    if user_raiting_diff > 0 and hiden_user_raiting is False:
        user_raiting = {
            "user_id": {"N": user_id},
            "raiting": {"N": user_raiting}
        }
        responce_message += response_user_raitings(
            message["chat"]["id"], [user_raiting],
            {tg_msg["from"]["id"]: tg_msg["from"]["first_name"]},
            {tg_msg["from"]["id"]: user_raiting_diff},
        )

    telegram_send_message(
        message["chat"]["id"], responce_message, message["message_id"]
    )
    return DEFAULT_RESPONCE


def handler(event, context):
    """Handler"""

    is_develop = (__name__.split('.', maxsplit=1)[0] == "develop")

    if event is None and context is None:
        return DEFAULT_RESPONCE

    if event.get("headers", {}).get("Content-Type") != "application/json":
        return DEFAULT_RESPONCE

    message = json.loads(event.get("body", "{}")).get("message", None)

    if message is None:
        return DEFAULT_RESPONCE

    try:

        cache_init()
        _db_create_tables()

        bot_command, _ = get_bot_command(message)

        command_handlers = {
            "version": telegram_bot_command_version_handler,
            "topvehicle": telegrma_bot_command_top_vehicle_handler,
            "topuser": telegrma_bot_command_top_user_handler,
            "search": telegram_bot_command_search_handler,
            "images": telegram_bot_command_images_handler,
            "check": telegram_bot_command_check_photo_handler,
            "history": telegram_bot_command_history
        }

        if bot_command in command_handlers:
            return command_handlers[bot_command](message)

        # Просто фото
        if "photo" in message:
            return telegram_bot_command_check_photo_handler(message)

    except Exception as ex: # pylint: disable=W0703
        print(ex)
        if message is not None \
            and message.get("chat", {}).get("type", "supergroup") != "supergroup":
            responce_message = "Упс, что-то пошло не так :("
            if is_develop:
                trace_back = traceback.format_exc()
                trace_back = trace_back.replace('&', '&amp;')
                trace_back = trace_back.replace('<', '&lt;')
                trace_back = trace_back.replace('<', '&lt;')
                responce_message += "\n<pre>" + trace_back + "</pre>"
            telegram_send_message(message["chat"]["id"], responce_message, message["message_id"])

    # Return default responce
    return DEFAULT_RESPONCE
