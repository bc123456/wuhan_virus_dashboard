from geopy.geocoders import Nominatim
import time
import pickle

def get_infection_stats(path):
    with open(path, 'rb') as f:
        infection_stats = pickle.load(f)

    return (
        infection_stats['death'], 
        infection_stats['confirmed'], 
        infection_stats['investigating'], 
        infection_stats['reported']
    )


def pop_address(address):
    address_lst = address.split(',')
    return ','.join(address_lst[1:])
    
def get_coordinates(address):
    trial0 = 0
    trial1 = 0
    trial2 = 0
    location = None
    geolocator = Nominatim(user_agent='hk_explorer')
    while location is None and trial0 < 5:
        trial0 += 1
        try:
            location = geolocator.geocode(address)
        except:
            pass
        time.sleep(1)
    if location is None:
        simplified_address1 = pop_address(address)
        while location is None and trial1 < 5:
            trial1 += 1
            try:
                location = geolocator.geocode(simplified_address1)
            except:
                pass
            time.sleep(1)
    if location is None:
        simplified_address2 = pop_address(simplified_address1)
        while location is None and trial2 < 5:
            trial2 += 1
            try:
                location = geolocator.geocode(simplified_address2)
            except:
                pass
            time.sleep(1)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None, None