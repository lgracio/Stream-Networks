SECONDS_IN_DAY = 60 * 60 * 24


# Parameters: compute?, directed, preprocess type,  sliding-window size, sample fraction,  network file
data = {
    # UNDIRECTED NETWORKS
    # Email. Source: https://snap.stanford.edu/data/email-Eu-core-temporal.html
    "email": (True, False, 0, 7 * SECONDS_IN_DAY, 0.65, "Source Networks/email-Eu-core-temporal.txt"),

    # Mooc. Souce: https://snap.stanford.edu/data/act-mooc.html
    "mooc": (True, False, 1, 1*SECONDS_IN_DAY, 0.1, "Source Networks/mooc_actions.tsv"),

    # 9/11. Source: http://vlado.fmf.uni-lj.si/pub/networks/data/CRA/terror.htm
    "911": (True, False, 4, 1*SECONDS_IN_DAY,1,"Source Networks/Days.net"),

    # DIRECTED NETWORKS
    # Violence. Source: http://vladowiki.fmf.uni-lj.si/doku.php?id=pajek:data:temp:fran
    "violence": (True, True, 3, 365*SECONDS_IN_DAY, 1, "Source Networks/violence.ten"),

    # Mathoverlow. Source: https://snap.stanford.edu/data/sx-mathoverflow.html
    "mathoverflow": (True, True, 0, 14*SECONDS_IN_DAY, 0.4, "Source Networks/sx-mathoverflow-a2q.txt"),

    # Retweets. Source: https://github.com/manlius/SocialBursts/tree/master/Network_Data
    #           Paper:  https://www.nature.com/articles/s41598-020-61523-z.pdf
    "retweets": (True, True, 2, SECONDS_IN_DAY, 1, "Source Networks/GRAVITATIONAL_WAVES_2016-activity.txt")
}