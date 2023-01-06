import time
import boto3


db = boto3.client('dynamodb')
table_name = 'telegram_vehicledb_vehicles'


_cache = {}


def _get_vehicle(plate):
    if plate not in _cache:
        _cache[plate] = db.get_item(
            TableName = table_name,
            Key = {'plate': {'S': plate}}
        )
    return _cache[plate]


def get_vehicle_by_image(image):
    data = db.scan(
        TableName = table_name,
        FilterExpression = "contains(#name, :value)",
        ExpressionAttributeNames = {'#name': 'images'},
        ExpressionAttributeValues = {':value': {'S': image}}
    )
    r = []
    if data['Count'] > 0:
        for item in data['Items']:
            _cache[item['plate']['S']] = {'Item': item}
            r.append(item)
    return r


def is_exist(plate):
    return 'Item' in _get_vehicle(plate)


def get_vehicle(plate):

    data = _get_vehicle(plate)
    
    if 'Item' in data: return data['Item']

    return {
        'plate': {'S': plate},
        'comment': {'S': ""},
        'images': {'L': []},
        'last_found': {'L': []}
    }


def save_vehicle(vehicle):
    d = db.put_item( TableName = table_name, Item=vehicle )
    _cache[vehicle['plate']['S']] = {'Item': vehicle}
    return d


def update_comment(vehicle, comment):
    vehicle['comment']['S'] = comment


def add_images(vehicle, image):
    for i in vehicle['images']['L']:
        if i['S'] == image:
            return
    vehicle['images']['L'].append({'S': image})


def update_last_found(vehicle, chat_id):
    is_update = False
    for c in vehicle['last_found']['L']:
        if c['M']['chat_id']['N'] == str(chat_id):
            c['M']['timestamp']['N'] = str(time.time())
            is_update = True
            break
    
    if is_update == False:
        vehicle['last_found']['L'].append({
            'M': {
                'chat_id': {'N': str(chat_id)},
                'timestamp': {'N': str(time.time() + 1800)}
            }
        })


def get_last_update(vehicle, chat_id):
    for c in vehicle['last_found']['L']:
        if c['M']['chat_id']['N'] == str(chat_id):
            diff = time.time() - float(c['M']['timestamp']['N'])
            if diff < 0:
                return None
            return int( diff/86400 )

    return None


def search_by_plate(contains, limit = 10):

    if len(contains) < 1:
        return []

    expression = ""
    attribures = {}

    index = 0
    for val in contains:
        attribures[':v' + str(index) ] = {'S': val}
        if index > 0:
            expression += " AND "
        expression += "contains(#name, :v" + str(index) + ")"
        index += 1

    data = db.scan(
        TableName = table_name,
        FilterExpression = expression,
        ExpressionAttributeNames = {'#name': 'plate'},
        ExpressionAttributeValues = attribures
    )

    r = []
    if data['Count'] > 0:
        for item in data['Items']:
            if limit <= 0:
                break
            limit -= 1
            r.append(item)

    return r
