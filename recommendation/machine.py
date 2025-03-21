import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from utils.query import querys


# 假设的用户评分数据
# user_ratings = {
#     "admin": {"赛博朋克": 1},
#     "userA": {"赛博朋克": 1, "艾尔登法环": 2}
# }

def get_user_ratings():
    user_ratings = {}
    userList = list(querys('select * from user', [], 'select'))
    historyList = list(querys('select * from history', [], 'select'))

    for user in userList:
        user_id = user[0]
        user_name = user[1]

        for history in historyList:
            game_id = history[1]
            try:
                existHistory = \
                    querys('select id from history where game_id = %s and user_id = %s', [game_id, user_id], "select")[
                        0][0]
                gameName = querys('select title from games where id = %s', [game_id], "select")[0][0]
                historyCount = history[3]

                if user_ratings.get(user_name, -1) == -1:
                    user_ratings[user_name] = {gameName: historyCount}
                else:
                    user_ratings[user_name][gameName] = historyCount
            except:
                continue

    print(user_ratings)
    return user_ratings


def user_based_collaborative_filtering(user_name, user_ratings, top_n=3):
    # 获取目标用户的数据
    target_user_ratings = user_ratings[user_name]
    # 保存相似度得分
    user_similarity_scores = {}
    # 目标用户转为numpy数组
    target_user_ratings_list = np.array([
        rating for _, rating in target_user_ratings.items()
    ])

    # 计算相似得分
    for user, rating in user_ratings.items():
        if user == user_name:
            continue
        # 将其他用户数据也转为numpy数组
        user_ratings_list = np.array([rating.get(item, 0) for item in target_user_ratings])
        # 计算余弦相似度
        similarity_score = cosine_similarity([user_ratings_list], [target_user_ratings_list])[0][0]
        user_similarity_scores[user] = similarity_score

    # 按相似度得分排序
    sorted_similar_users = sorted(user_similarity_scores.items(), key=lambda x: x[1], reverse=True)

    # 打印相似用户及其相似度得分
    print(sorted_similar_users)

    # 选择topn个相似用户作为推荐结果
    recommended_items = set()
    for similar_user in sorted_similar_users[:top_n]:
        # print(user_ratings[similar_user[0]])
        recommended_items.update(user_ratings[similar_user[0]].keys())

    # 过滤：移除目标用户已经评分的项目
    filtered_recommended_items = []
    for item in recommended_items:
        if item not in target_user_ratings:
            filtered_recommended_items.append(item)

    # 对结果进行排序，保证每次顺序相同
    filtered_recommended_items = sorted(filtered_recommended_items)

    # 打印推荐结果
    print("推荐结果:", filtered_recommended_items)

    # 返回推荐结果
    return filtered_recommended_items


if __name__ == '__main__':
    user_name = '1'
    user_ratings = get_user_ratings()
    user_based_collaborative_filtering(user_name, user_ratings)
