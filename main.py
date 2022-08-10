import requests
import time

cookie = 'SET YOUR COOKIE HERE'


def refresh_xcsrf(cookie):
    response = requests.post('https://auth.roblox.com/v1/login',
                             cookies={'.ROBLOSECURITY': cookie})
    if "X-CSRF-TOKEN" in response.headers:
        return response.headers["X-CSRF-TOKEN"]


def send_message(subject, message, user_id, cookie):
    data = {
        'body': message,
        'cacheBuster': 1660090304980,
        'recipientid': str(user_id),
        'subject': subject
    }
    request = requests.post('https://privatemessages.roblox.com/v1/messages/send',
                            data=data,
                            cookies={'.ROBLOSECURITY': cookie},
                            headers={'x-csrf-token': refresh_xcsrf(cookie)})
    return request.json()


def get_resellers(id, cookie):
    resellers = []
    request = requests.get(f'https://economy.roblox.com/v1/assets/{id}/resellers?cursor=&limit=100',
                           headers={'x-csrf-token': refresh_xcsrf(cookie)},
                           cookies={'.ROBLOSECURITY': cookie}).json()
    next_page = request['nextPageCursor']
    for item in request['data']:
        resellers.append({'seller': item['seller']['id'], 'price': item['price']})

    while next_page is not None:
        request = requests.get(f'https://economy.roblox.com/v1/assets/{id}/resellers?cursor={next_page}&limit=100',
                               headers={'x-csrf-token': refresh_xcsrf(cookie)},
                               cookies={'.ROBLOSECURITY': cookie}).json()
        next_page = request['nextPageCursor']
        for item in request['data']:
            resellers.append({'seller': item['seller']['id'], 'price': item['price']})
    return resellers


message = '''
🔔 NOTIFICATION 🔔

This is an idiot alert !

You get an idiot alert when you re-sell something for lower than you bought it for !

Please use your brain and get some help !

👍👍👍            
'''

original_price = 400
loss_threshold = round(original_price / 7 * 10)  # calculates how much they need to sell it for before it turns into a loss
sent = []

resellers = get_resellers(10159606132, cookie)
for reseller in resellers:
    if reseller['price'] < loss_threshold and not reseller['seller'] in sent:
        # check if reseller can be messaged (to save on rate-limits)
        request = requests.get(f'https://privatemessages.roblox.com/v1/messages/{reseller["seller"]}/can-message',
                               headers={'x-csrf-token': refresh_xcsrf(cookie)},
                               cookies={'.ROBLOSECURITY': cookie})
        try:
            #
            if request.json()['canMessage'] is True:
                m = send_message('IMPORTANT',
                                 message,
                                 reseller['seller'],
                                 cookie)
                print(m)
                try:
                    # check for rate limits
                    m['errors']
                    time.sleep(15)
                except KeyError:
                    sent.append(reseller['seller'])
        except KeyError:
            # rate limit on check
            print(f'Check: {request.json()}')
