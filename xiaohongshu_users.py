# import json 
# from mitmproxy import ctx 

# def response(flow):
#     url = 'https://www.xiaohongshu.com/api/sns/v2/search/user'
#     print(flow.request.url)
#     if url in str(flow.request.url):
#         users = json.loads(flow.response.text).get('data')
#         for user in users:
#             print(user)



# {
#     "data": [
#         {
#             "desc": "粉丝·5",
#             "followed": false,
#             "id": "5b40c960e8ac2b0f872caaca",
#             "image": "https://img.xiaohongshu.com/avatar/5b40cba714de4109a669d174.jpg@120w_120h_92q_1e_1c_1x.jpg",
#             "link": "xhsdiscover://1/user/user.5b40c960e8ac2b0f872caaca",
#             "name": "李冰冰",
#             "red_id": "424280265",
#             "red_official_verified": false,
#             "red_official_verify_type": 0
#         },
#         {
#             "desc": "粉丝·2",
#             "followed": false,
#             "id": "5b21fc9811be1031e4d7187d",
#             "image": "https://img.xiaohongshu.com/avatar/5b21fc9811be1031e4d7187d.jpg@120w_120h_92q_1e_1c_1x.jpg",
#             "link": "xhsdiscover://1/user/user.5b21fc9811be1031e4d7187d",
#             "name": "李冰冰",
#             "red_id": "182248516",
#             "red_official_verified": false,
#             "red_official_verify_type": 0
#         },

#         {


