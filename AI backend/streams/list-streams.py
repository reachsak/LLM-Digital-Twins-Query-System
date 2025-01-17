"""
This example demonstrates how to get streams from given facility and get stream details (name, parent).

It uses 2-legged authentication - this requires athat application is added to facility as service.
"""
import base64
import struct
from typing import List, Tuple
from typing import Any

def get_default_model(facility_id: str, facility: Any) -> Any | None:
    """
    Returns default model for given facility.
    """
    
    default_model_id = facility_id.replace('urn:adsk.dtt:', 'urn:adsk.dtm:')
    for link in facility.get('links'):
        model_id = link.get('modelId')
        if model_id == default_model_id:
            return link
    return None


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
from typing import Any, Dict, List
import requests


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

def main():
    # Start
    # STEP 1 - obtain token. The sample uses 2-legged token but it would also work
    # with 3-legged token assuming that user has access to the facility
    token = create_token(APS_CLIENT_ID, APS_CLIENT_SECRET, ['data:read'])
    with TandemClient(lambda: token) as client:
        # STEP 2 - get facility and default model. The default model has same id as facility
        facility = client.get_facility(FACILITY_URN)
        default_model = get_default_model(FACILITY_URN, facility)
        # STEP 3 - get streams and their parents
        streams = client.get_streams(default_model.get('modelId'), [ COLUMN_FAMILIES_STANDARD, COLUMN_FAMILIES_XREFS ])
        model_stream_map = {}
        for i in range(len(streams)):
            stream = streams[i]
            # host is stored as parent
            parent_xref = stream.get(QC_XPARENT)
            if parent_xref is None:
                continue
            # decode xref key of the host
            model_id, key = decode_xref_key(parent_xref)
            items = model_stream_map.get(model_id)
            if items is None:
                items = []
                model_stream_map[model_id] = items
            items.append({
                'key': to_short_key(key),
                'stream_index': i
            })
        # STEP 4 - print name of stream + name of parent
        # note we use batch query to get properties of multiple elements
        # in one call rather than query server for each element
        for model_id in model_stream_map:
            items = model_stream_map[model_id]
            keys = list(map(lambda item: item.get('key'), items))
            element_data = client.get_elements(f'urn:adsk.dtm:{model_id}', keys)
            for item in items:
                stream = streams[item.get('stream_index')]
                parent_data = next((e for e in element_data if e.get(QC_KEY) == item.get('key')), None)
                if parent_data is None:
                    continue
                print(f'{stream[QC_NAME]}: {parent_data[QC_NAME]}')


if __name__ == '__main__':
    main()
