abilities_average_round = """
    SELECT
        AVG(mt."round") AS Average,
        count(mt."round") as Count,
        UNNEST("abilities") as Name
    FROM "MatchPlayer" AS mp
    INNER JOIN
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
        AND mt."team_id" = mp."team_id"
    INNER JOIN
        "Match" AS m ON mp."match_id" = m."match_id"
    WHERE
        m."map_name" = $map_name AND m."ended_at" > $from_date
    GROUP BY Name
    ORDER BY Average DESC
""".lstrip()

most_picked_abilities = """
    SELECT
        AVG(mt."round") AS Average,
        count(mt."round") as Count,
        UNNEST("abilities") as Name
    FROM "MatchPlayer" AS mp
    INNER JOIN
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
        AND mt."team_id" = mp."team_id"
    INNER JOIN
        "Match" AS m ON mp."match_id" = m."match_id"
    WHERE
        m."map_name" = $map_name AND m."ended_at" > $from_date
    GROUP BY Name
    ORDER BY Count DESC
""".lstrip()

items_average_round = """
    SELECT *
    FROM (
        SELECT
            AVG(mt."round") AS Average,
            count(mt."round") as Count,
            UNNEST("items") as Name
        FROM "MatchPlayer" AS mp
        INNER JOIN
            "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
            AND mt."team_id" = mp."team_id"
        INNER JOIN
            "Match" AS m ON mp."match_id" = m."match_id"
        WHERE
            m."map_name" = $map_name
            AND m."ended_at" > $from_date
        GROUP BY Name
        ORDER BY Average DESC
    ) t
    WHERE
        t.Name is not NULL AND t.Name != 'None'
""".lstrip()

most_purchased_items = """
    SELECT *
    FROM (
        SELECT
            AVG(mt."round") AS Average,
            count(mt."round") as Count,
            UNNEST("items") as Name
        FROM "MatchPlayer" AS mp
        INNER JOIN
            "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
            AND mt."team_id" = mp."team_id"
        INNER JOIN
            "Match" AS m ON mp."match_id" = m."match_id"
        WHERE
            m."map_name" = $map_name AND m."ended_at" > $from_date
        GROUP BY Name
        ORDER BY Count DESC
    ) t
    WHERE t.Name is not NULL AND t.Name != 'None'
""".lstrip()

innates_average_round = """
    SELECT
        avg(mt."round") as Average,
        count(mt."round") as Count,
        mp."innate" as Name
    FROM "MatchPlayer" as mp
    INNER JOIN
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
        AND mt."team_id" = mp."team_id"
    INNER JOIN "Match" m on mp."match_id" = m."match_id"
    WHERE
        m."map_name" = $map_name
        AND m."ended_at" > $from_date
        AND mp."innate" != ''
        AND mp."innate" is not null
    GROUP BY Name
    ORDER BY Average desc
""".lstrip()

most_picked_innates = """
    SELECT
        avg(mt."round") as Average,
        count(mt."round") as Count,
        mp."innate" as Name
    FROM "MatchPlayer" as mp
    INNER JOIN
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
        AND mt."team_id" = mp."team_id"
    INNER JOIN "Match" m on mp."match_id" = m."match_id"
    WHERE
        m."map_name" = $map_name
        AND m."ended_at" > $from_date
        AND mp."innate" != ''
        AND mp."innate" is not null
    GROUP BY Name
    ORDER BY Count desc
""".lstrip()

hardest_round_death_element = """
    SELECT *
    FROM (
        SELECT
            COUNT(*),
            jsonb_array_elements("round_deaths")->>$rd_field as Name
        FROM "MatchPlayer" as mp
        INNER JOIN "Match" AS m ON mp."match_id" = m."match_id"
        WHERE
            m."map_name" = $map_name
            AND m."ended_at" > $from_date
            AND mp."round_deaths" != '"{}"'
        GROUP BY Name
        ORDER BY Count DESC
    ) t
    WHERE t.Name is not NULL
""".lstrip()

quests_progress = """
    SELECT
        Q.name,
        avg(progress),
        count(progress)
    FROM "PlayerQuests"
    INNER JOIN "Quests" Q on "PlayerQuests".quest_id = Q.id
    GROUP BY Q.id
    ORDER BY Avg desc
""".lstrip()

achievements_progress = """
    SELECT
        A.name,
        avg(progress) from "PlayerAchievements"
    INNER JOIN
        "Achievements" A on "PlayerAchievements".achievement_id = A.id
    GROUP BY A.id
    ORDER BY Avg desc
""".lstrip()

dated_leaderboard = """
    SELECT
        mp."steam_id",
        max("rating_change_new") "max"
    FROM "MatchPlayer" mp
    INNER JOIN "Match" M on mp."match_id" = M."match_id"
    WHERE "ended_at"::date = $from_date and "map_name"=$map_name
    GROUP by mp."steam_id"
    ORDER BY "max" desc
    LIMIT 200
    OFFSET 200 * $page;
""".lstrip()

masteries_average_round = """
    SELECT
        avg(mt."round") as Average,
        count(mt."round") as Count,
        mp."mastery" as Name
    FROM "MatchPlayer" as mp
    INNER JOIN
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id"
        AND mt."team_id" = mp."team_id"
    INNER JOIN "Match" M on mp."match_id" = M."match_id"
    WHERE
        M."map_name" = $map_name
        AND M."ended_at" > $from_date
        AND mp."mastery" != ''
        AND mp."mastery" is not null
    GROUP BY Name
    ORDER BY Average desc
""".lstrip()
