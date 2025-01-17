"""
This example demonstrates how to list structure of the facility (level - room - asset)

It uses 2-legged authentication - this requires that application is added to facility as service.
"""
import json

"""
This example demonstrates how to list all rooms from facility.

It uses 2-legged authentication - this requires that application is added to facility as service.
"""

import base64
import struct
from typing import List, Tuple



def decode_xref_key(key: str) -> Tuple[str, str]:
    """ Decodes xref key to model id and element key."""

    txt = __b64_prepare(key)
    buff = base64.b64decode(txt)
    model_buff = bytearray(MODEL_ID_SIZE)
    model_buff[0:] = buff[0:MODEL_ID_SIZE]
    model_id = __make_web_safe(base64.b64encode(model_buff).decode('utf-8'))
    key_buff = bytearray(MODEL_ID_SIZE)
    key_buff[0:] = buff[MODEL_ID_SIZE:]
    element_key = __make_web_safe(base64.b64encode(key_buff).decode('utf-8'))
    return model_id, element_key

def from_short_key_array(text: str, use_full_keys: bool = False, is_logical: bool = False) -> List[str]:
    """
    Decodes text (local refs) to list of keys. If use_full_keys is set to True then full
    keys are returned. If is_logical is set to True then logical keys are
    returned.
    """

    text = __b64_prepare(text)
    bin_data = base64.b64decode(text)
    buff = bytearray(ELEMENT_ID_SIZE)
    if use_full_keys:
        buff = bytearray(ELEMENT_ID_WITH_FLAGS_SIZE)
    result = []
    offset = 0
    while offset < len(bin_data):
        size = len(bin_data) - offset
        if size < ELEMENT_ID_SIZE:
            break
        if use_full_keys:
            flags_value = KEY_FLAGS_LOGICAL if is_logical else KEY_FLAGS_PHYSICAL
            struct.pack_into('>I', buff, 0, flags_value)
            buff[ELEMENT_FLAGS_SIZE:] = bin_data[offset:offset + ELEMENT_ID_SIZE]
        else:
            buff[0:] = bin_data[offset:offset + ELEMENT_ID_SIZE]
        element_key = __make_web_safe(base64.b64encode(buff).decode('utf-8'))
        result.append(element_key)
        offset += ELEMENT_ID_SIZE
    return result

def from_xref_key_array(text: str) -> List[Tuple[str, str]]:
    """ Decodes text (xref refs) to list of model id and element key tuples."""

    if text is None:
        return []
    text = __b64_prepare(text)
    bin_data = base64.b64decode(text)
    buff = bytearray(MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE)
    result = []
    offset = 0
    while offset < len(bin_data):
        size = len(bin_data) - offset
        if size < MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE:
            break
        buff[0:] = bin_data[offset:offset + MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE]
        model_id = __make_web_safe(base64.b64encode(buff[0:MODEL_ID_SIZE]).decode('utf-8'))
        element_key = __make_web_safe(base64.b64encode(buff[MODEL_ID_SIZE:]).decode('utf-8'))
        result.append((model_id, element_key))
        offset += MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE
    return result

def to_element_GUID(key: str) -> str:
    """ Converts element key to Revit GUID. Works for both short and full key. Note: It works only for models imported from Revit."""

    txt = __b64_prepare(key)
    buff = base64.b64decode(txt)
    if len(buff) == ELEMENT_ID_WITH_FLAGS_SIZE:
        del buff[0:4]
    hex = [f'{b:02x}' for b in buff]
    hex_groups = [4, 2, 2, 2, 6, 4]
    pos = 0
    result = []

    for length in hex_groups:
        result.append(''.join(hex[pos:pos + length]))
        pos += length
    return '-'.join(result)

def to_full_key(short_key: str, is_logical: bool = False) -> str:
    """ Converts short key to full key."""

    txt = __b64_prepare(short_key)
    buff = base64.b64decode(txt)
    full_key = bytearray(ELEMENT_ID_WITH_FLAGS_SIZE)
    flags_value = KEY_FLAGS_LOGICAL if is_logical else KEY_FLAGS_PHYSICAL
    struct.pack_into('>I', full_key, 0, flags_value)

    full_key[ELEMENT_FLAGS_SIZE:] = buff
    return __make_web_safe(base64.b64encode(full_key).decode('utf-8'))

def to_short_key(full_key: str) -> str:
    """ Converts full key to short key."""

    txt = __b64_prepare(full_key)
    buff = base64.b64decode(txt)
    key = bytearray(ELEMENT_ID_SIZE)
    key[0:] = buff[ELEMENT_FLAGS_SIZE:]
    return __make_web_safe(base64.b64encode(key).decode('utf-8'))

def to_system_id(key: str) -> str:
    """
    Converts element key to system id.
    """
    
    buff = base64.b64decode(__b64_prepare(key))
    id = buff[-4] << 24
    id |= buff[-3] << 16
    id |= buff[-2] << 8
    id |= buff[-1]
    res = bytearray(SYSTEM_ID_SIZE)
    offset  = [0]

    len = __write_var_int(res, offset, id)
    tmp = bytearray(len)
    tmp[0:] = res[0:len]
    text = base64.b64encode(tmp).decode('utf-8')
    text = text.replace('=','')
    return text
    

def to_xref_key(model_id: str, key: str) -> str:
    """ Converts model id and element key to xref key."""

    model_buff = base64.b64decode(__b64_prepare(model_id))
    element_buff = base64.b64decode(__b64_prepare(key))
    result = bytearray(MODEL_ID_SIZE + ELEMENT_ID_WITH_FLAGS_SIZE)
    result[0:] = model_buff
    result[MODEL_ID_SIZE:] = element_buff
    return __make_web_safe(base64.b64encode(result).decode('utf-8'))

def __b64_prepare(text: str) -> str:
    result = text.replace('-', '+')
    result = result.replace('_', '/')
    result += '=' * (len(result) % 4)
    return result

def __make_web_safe(text: str) -> str:
    result = text.replace('+', '-')
    result = result.replace('/', '_')
    result = result.rstrip('=')
    return result

def __write_var_int(buff, offset, value):
    start_offset = offset[0]

    while True:
        byte = 0 | (value & 0x7f)

        value >>= 7
        value &= 0xffffffff
        if value != 0:
            byte |= 0x80
        buff[offset[0]] = byte
        offset[0] += 1
        if not value:
            break
    return offset[0] - start_offset
from typing import Any, Dict, List
import requests

ELEMENT_FLAGS_SIZE = 4
ELEMENT_ID_SIZE = 20
ELEMENT_ID_WITH_FLAGS_SIZE = ELEMENT_FLAGS_SIZE + ELEMENT_ID_SIZE
MODEL_ID_SIZE = 16
SYSTEM_ID_SIZE = 9

KEY_FLAGS_PHYSICAL = 0x00000000
KEY_FLAGS_LOGICAL = 0x01000000

ELEMENT_FLAGS_SIMPLE_ELEMENT = 0x00000000
ELEMENT_FLAGS_FAMILY_TYPE = 0x01000000
ELEMENT_FLAGS_LEVEL = 0x01000001
ELEMENT_FLAGS_ROOM = 0x00000005
ELEMENT_FLAGS_STREAM = 0x01000003
ELEMENT_FLAGS_SYSTEM = 0x01000004

COLUMN_FAMILIES_DTPROPERTIES = 'z'
COLUMN_FAMILIES_LMV = '0'
COLUMN_FAMILIES_STANDARD = 'n'
COLUMN_FAMILIES_SYSTEMS = 'm'
COLUMN_FAMILIES_REFS = 'l'
COLUMN_FAMILIES_XREFS = 'x'

COLUMN_NAMES_CATEGORY_ID = 'c'
COLUMN_NAMES_CLASSIFICATION = 'v'
COLUMN_NAMES_OCLASSIFICATION = '!v'
COLUMN_NAMES_ELEMENT_FLAGS = 'a'
COLUMN_NAMES_ELEVATION = 'el'
COLUMN_NAMES_FAMILY_TYPE = 't'
COLUMN_NAMES_LEVEL = 'l'
COLUMN_NAMES_NAME = 'n'
COLUMN_NAMES_ONAME = '!n'
COLUMN_NAMES_PARENT = 'p'
COLUMN_NAMES_ROOMS = 'r'
COLUMN_NAMES_UNIFORMAT_CLASS = 'u'

QC_KEY = 'k'
QC_CLASSIFICATION = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_CLASSIFICATION}'
QC_OCLASSIFICATION = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_OCLASSIFICATION}'
QC_ELEMENT_FLAGS = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_ELEMENT_FLAGS}'
QC_ELEVATION = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_ELEVATION}'
QC_FAMILY_TYPE = f'{COLUMN_FAMILIES_REFS}:{COLUMN_NAMES_FAMILY_TYPE}'
QC_LEVEL = f'{COLUMN_FAMILIES_REFS}:{COLUMN_NAMES_LEVEL}'
QC_NAME = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_NAME}'
QC_ONAME = f'{COLUMN_FAMILIES_STANDARD}:{COLUMN_NAMES_ONAME}'
QC_ROOMS = f'{COLUMN_FAMILIES_REFS}:{COLUMN_NAMES_ROOMS}'
QC_XROOMS = f'{COLUMN_FAMILIES_XREFS}:{COLUMN_NAMES_ROOMS}'
QC_XPARENT = f'{COLUMN_FAMILIES_XREFS}:{COLUMN_NAMES_PARENT}'

MUTATE_ACTIONS_INSERT = 'i'



class TandemClient:
    """ A simple wrapper for Tandem Data API """

    def __init__(self, callback) -> None:
        """
        Creates new instance of TandemClient.
        """

        self.__authProvider = callback
        self.__base_url = 'https://developer.api.autodesk.com/tandem/v1'
        pass

    def __enter__(self) -> "TandemClient":
        return self
    
    def __exit__(self, *args: any)-> None:
        pass

    def create_documents(self, facility_id: str, doc_inputs: List[Any]) -> Any:
        """"
        Adds documents to the facility.
        """

        token = self.__authProvider()
        endpoint = f'twins/{facility_id}/documents'
        response = self.__post(token, endpoint, doc_inputs)
        return response

    def create_stream(self,
                      model_id: str,
                      name: str,
                      uniformat_class_id: str,
                      category_id: str,
                      classification: str | None = None,
                      parent_xref: str | None = None,
                      room_xref: str | None = None,
                      level_key: str | None = None) -> str:
        """
        Creates new stream using provided data.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/create'
        inputs = {
            'muts': [
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_NAME, name ],
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_ELEMENT_FLAGS, ELEMENT_FLAGS_STREAM ],
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_UNIFORMAT_CLASS, uniformat_class_id ],
                [ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_CATEGORY_ID, category_id ]
            ],
            'desc': 'Create stream'
        }

        if classification is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_STANDARD, COLUMN_NAMES_CLASSIFICATION, classification ])
        if parent_xref is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_XREFS, COLUMN_NAMES_PARENT, parent_xref ])
        if room_xref is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_XREFS, COLUMN_NAMES_ROOMS, room_xref ])
        if level_key is not None:
            inputs['muts'].append([ MUTATE_ACTIONS_INSERT, COLUMN_FAMILIES_REFS, COLUMN_NAMES_LEVEL, level_key ])
        response = self.__post(token, endpoint, inputs)
        return response.get('key')
    
    def delete_stream_data(self, model_id: str, keys: List[str], substreams: List[str] | None = None, from_date: str | None = None, to_date: str | None = None) -> None:
        """
        Deletes data from given streams. It can be used to delete specified substreams or all data from give streams.
        It's also possible to delete data for given time range (from, to).
        """

        token = self.__authProvider()
        endpoint = f'timeseries/models/{model_id}/deletestreamsdata'
        inputs = {
            'keys': keys
        }
        query_params = {
        }
        if substreams is not None:
            query_params['substreams'] = ','.join(substreams)
        if from_date is not None:
            query_params['from'] = from_date
        if to_date is not None:
            query_params['to'] = to_date
        # if there are no input parameters, then delete all stream data
        if len(query_params) == 0:
            query_params['allSubstreams'] = 1
        self.__post(token, endpoint, inputs, query_params)

    def get_element(self, model_id: str, key: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns element for given key.
        """

        data = self.get_elements(model_id, [ key ], column_families)
        return data[0]

    def get_elements(self, model_id: str, element_ids: List[str] | None = None, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ], include_history: bool = False) -> Any:
        """
        Returns list of elements for given model.
        """

        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': include_history,
            'skipArrays': True
        }
        if element_ids is not None and len(element_ids) > 0:
            inputs['keys'] = element_ids
        result = self.__post(token, endpoint, inputs)
        return result[1:]
    
    def get_facility(self, facility_id: str) -> Any:
        """
        Retuns facility for given facilty urn.
        """

        token = self.__authProvider()
        endpoint = f'twins/{facility_id}'
        return self.__get(token, endpoint)
    
    def get_facility_template(self, facility_id: str) -> Any:
        """
        Retuns facility teplate for given facilty urn.
        """

        token = self.__authProvider()
        endpoint = f'twins/{facility_id}/inlinetemplate'
        return self.__get(token, endpoint)
    
    def get_group(self, group_id: str) -> Any:
        """
        Returns group details.
        """
        
        token = self.__authProvider()
        endpoint = f'groups/{group_id}'
        result = self.__get(token, endpoint)
        return result
    
    def get_groups(self) -> Any:
        """
        Returns list of groups.
        """
        
        token = self.__authProvider()
        endpoint = f'groups'
        result = self.__get(token, endpoint)
        return result
    
    def get_levels(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns level elements from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': False,
            'skipArrays': True
        }
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            flags = elem.get(QC_ELEMENT_FLAGS)
            if flags == ELEMENT_FLAGS_LEVEL:
                results.append(elem)
        return results
    
    def get_model_history(self, model_id: str, timestamps: List[int], include_changes: bool = False, use_full_keys: bool = False):
        """
        Returns model changes.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/history'
        inputs = {
            'timestamps': timestamps,
            'includeChanges': include_changes,
            'useFullKeys': use_full_keys
        }
        response = self.__post(token, endpoint, inputs)
        return response
    
    def get_model_history_between_dates(self, model_id: str, from_date: int, to_date: int, include_changes: bool = True, use_full_keys: bool = True):
        """
        Returns model changes between two dates.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/history'
        inputs = {
            'min': from_date,
            'max': to_date,
            'includeChanges': include_changes,
            'useFullKeys': use_full_keys
        }
        response = self.__post(token, endpoint, inputs)
        return response

    def get_model_schema(self, model_id: str) -> Any:
        """
        Returns schema for given model URN.
        """

        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/schema'
        return self.__get(token, endpoint)
    
    def get_rooms(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns room elements from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': False,
            'skipArrays': True
        }
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            flags = elem.get(QC_ELEMENT_FLAGS)
            if flags == ELEMENT_FLAGS_ROOM:
                results.append(elem)
        return results
    
    def get_stream_data(self, model_id: str, key: str, from_date: int | None = None, to_date: int | None = None) -> Any:
        """
        Returns data for given stream. It can be used to get data for given time range (from, to).
        """
    
        token = self.__authProvider()
        endpoint = f'timeseries/models/{model_id}/streams/{key}'
        search_params = {}
        if from_date is not None:
            search_params['from'] = from_date
        if to_date is not None:
            search_params['to'] = to_date
        result = self.__get(token, endpoint, search_params)
        return result

    def get_stream_secrets(self, model_id: str, keys: List[str]) -> Any:
        """
        Returns secrets for streams.
        """

        token = self.__authProvider()
        endpoint = f'models/{model_id}/getstreamssecrets'
        inputs = {
            'keys': keys
        }
        result = self.__post(token, endpoint, inputs)
        return result
    
    def get_streams(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns stream elements from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': False,
            'skipArrays': True
        }
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            flags = elem.get(QC_ELEMENT_FLAGS)
            if flags == ELEMENT_FLAGS_STREAM:
                results.append(elem)
        return results
    
    def get_systems(self, model_id: str, column_families: List[str] = [ COLUMN_FAMILIES_STANDARD ]) -> Any:
        """
        Returns system elements from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': False,
            'skipArrays': True
        };
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            flags = elem.get(QC_ELEMENT_FLAGS)
            if flags == ELEMENT_FLAGS_SYSTEM:
                results.append(elem)
        return results
    
    def get_tagged_assets(self, model_id: str,
                          column_families: List[str] = [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES, COLUMN_FAMILIES_REFS ],
                          include_history: bool = False) -> Any:
        """
        Returns list of tagged assets from given model.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/scan'
        inputs = {
            'families': column_families,
            'includeHistory': include_history,
            'skipArrays': True
        }
        data = self.__post(token, endpoint, inputs)
        results = []

        for elem in data:
            if elem == 'v1':
                continue
            keys = elem.keys()
            custom_props = []

            for k in keys:
                if k.startswith('z:'):
                    custom_props.append(k)
            if len(custom_props) > 0:
                results.append(elem)
        return results
    
    def get_views(self, facility_id: str) -> Any:
        """
        Returns list of views for given facility.
        """
        
        token = self.__authProvider()
        endpoint = f'twins/{facility_id}/views'
        result = self.__get(token, endpoint)
        return result
    
    def mutate_elements(self, model_id: str, keys: List[str], mutations, description: str) -> Any:
        """
        Modifies given elements.
        """
        
        token = self.__authProvider()
        endpoint = f'modeldata/{model_id}/mutate'
        inputs = {
            'keys': keys,
            'muts': mutations,
            'desc': description
        }
        result = self.__post(token, endpoint, inputs)
        return result
    
    def reset_stream_secrets(self, model_id, stream_ids: List[str], hard_reset: bool = False) -> None:
        """
        Resets secrets for given streams.
        """
        
        token = self.__authProvider()
        endpoint = f'models/{model_id}/resetstreamssecrets'
        inputs = {
            'keys': stream_ids,
            'hardReset': hard_reset
        }
        self.__post(token, endpoint, inputs)
        return
    
    def save_document_content(self, url: str, file_path: str) -> None:
        """"
        Downloads document to local file.
        """

        token = self.__authProvider()
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return
    
    def __get(self, token: str, endpoint: str, params: Dict[str, Any] | None = None) -> Any:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        url = f'{self.__base_url}/{endpoint}'
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    def __post(self, token: str, endpoint: str, data: Any, params: Dict[str, Any] | None = None) -> Any:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.__base_url}/{endpoint}'
        response = requests.post(url, headers=headers, json=data, params=params)
        if response.status_code == 204:
            return
        return response.json()
from typing import List
import requests



def create_token(client_id: str, client_secret: str, scope: List[str]) -> str:
    """ Creates 2-legged authorization token. """

    options = {
        'grant_type': 'client_credentials',
        'scope': ' '.join(scope)
    }

    response = requests.post('https://developer.api.autodesk.com/authentication/v2/token', params=options, auth=(client_id, client_secret))
    data = response.json()   
    return data.get('access_token')

# update values below according to your environment
APS_CLIENT_ID = "ooitRwpKk1hUODYgPiMWzVD3NA0CNGf6z3UcqUcEe8qFIBae"
APS_CLIENT_SECRET = "GAYBeDFHubOww0Lugun0FPOdWZcOdsyG3SiEcxytz8j26wlQ7yRjU5DyNLNuBu6t"
FACILITY_URN = "urn:adsk.dtt:LudKiyWAQcCPqK2gQWxNfw"

def is_default_model(facility_id: str, model_id: str) -> bool:
    """
    Checks if model is default model for the facility.
    """

    default_model_id = facility_id.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')

    return default_model_id == model_id

def get_levels(data) -> list:
    result = []
    for level_key in data['levels']:
        result.append((level_key, data['levels'][level_key]))
    return result

def get_rooms_by_level(data, level_key) -> list:
    result = []
    for room_key in data['rooms']:
        if data['room_level_map'].get(room_key) == level_key:
            room = data['rooms'][room_key]
            result.append((room_key, room))
    return result

def get_assets_by_room(data, room_key) -> list:
    asset_keys = data['room_assets_map'][room_key]
    result = []

    for asset_key in asset_keys:
        asset = data['assets'].get(asset_key)

        result.append((asset_key, asset))
    return result

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility
        facility = client.get_facility(FACILITY_URN)
        # this structure is used to keep structure data. it uses element keys as keys for maps.
        data = {
            'levels': {},
            'rooms': {},
            'assets': {},
            'room_assets_map': {},
            'room_level_map': {}
        }
        model_rooms = []

        # STEP 3 - collect assets and related room references
        for l in facility.get('links'):
            model_id = l.get('modelId')
            # skip default model
            if is_default_model(FACILITY_URN, model_id):
                continue
            assets = client.get_tagged_assets(model_id, [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_DTPROPERTIES, COLUMN_FAMILIES_REFS, COLUMN_FAMILIES_XREFS ])
            for asset in assets:
                # unique asset key
                asset_key = asset.get(QC_KEY)
                data['assets'][asset_key] = asset
                room_ref = asset.get(QC_ROOMS)
                asset_rooms = []
                # STEP 4 - find room references. Note that reference can be within same model or across models
                if room_ref is not None:
                    room_keys = from_short_key_array(room_ref)

                    for room_key in room_keys:
                        asset_rooms.append((model_id, room_key))
                else:
                    room_ref = asset.get(QC_XROOMS)
                    room_keys = from_xref_key_array(room_ref)
                    for (model_id, room_id) in room_keys:
                        # in case of xref key we need to decode from long key to short key
                        asset_rooms.append((f'urn:adsk.dtm:{model_id}', to_short_key(room_id)))
                # STEP 5 - build map between asset and rooms - note that asset can be linked to more than one room
                for (model_id, room_key) in asset_rooms:
                    asset_ids = data['room_assets_map'].get(room_key)

                    if asset_ids is None:
                        asset_ids = []
                        data['room_assets_map'][room_key] = asset_ids
                    asset_ids.append(asset_key)
                model_rooms.extend(asset_rooms)
        # STEP 6 - process rooms and create map between room and level
        model_ids = set(map(lambda item: item[0], model_rooms))
        for model_id in model_ids:
            room_ids = set(map(lambda item: item[1], filter(lambda item: item[0] == model_id, model_rooms)))
            rooms = client.get_elements(model_id, list(room_ids), [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_REFS ])
            level_ids = set()

            for room in rooms:
                room_key = room.get(QC_KEY)

                data['rooms'][room_key] = room
                level_ref = room.get(QC_LEVEL)
                if level_ref is not None:
                    level_ids.add(level_ref)
                    data['room_level_map'][room_key] = level_ref
            # process levels
            if len(level_ids) > 0:
                levels = client.get_elements(model_id, list(level_ids))
                for level in levels:
                    level_key = level.get(QC_KEY)
                    data['levels'][level_key] = level
        # STEP 7 - iterate through structure
        print('facility data list')
        for (level_key, level) in get_levels(data):
            print(f'{level.get(QC_NAME)}')
            for (room_key, room) in get_rooms_by_level(data, level_key):
                print(f'  {room.get(QC_NAME)}')
                for (asset_key, asset) in get_assets_by_room(data, room_key):
                    print(f'    {asset.get(QC_NAME)}')
        # STEP 8 - save structure to file
        with open('facility_data.json', 'w') as f:
            f.write(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
