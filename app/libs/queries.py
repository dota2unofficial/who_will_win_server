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

ability_per_day_pickrate = """
    select
        "ended_at"::date,
        count("abilities"),
        avg(mt."round")
    from
        "MatchPlayer" mp
    inner join
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id" and
        mt."team_id" = mp."team_id"
    inner join
        "Match" M on mp."match_id" = M."match_id"
    where
        $ability_name = any("abilities")
    group by "ended_at"::date;
""".lstrip()

item_per_day_pickrate = """
    select
        "ended_at"::date,
        count("items"),
        avg(mt."round")
    from "MatchPlayer" mp
    inner join
        "MatchTeam" AS mt ON mt."match_id" = mp."match_id" and
        mt."team_id" = mp."team_id"
    inner join
        "Match" M on mp."match_id" = M."match_id"
    where
        $item_name = any("items")
    group by "ended_at"::date;
""".lstrip()

replace_player_quests = """
    CREATE OR REPLACE FUNCTION replace_player_quests() RETURNS BOOLEAN AS $$
    DECLARE
        rec RECORD;
        quests integer[] := (select array_agg(id::integer) from "Quests");
        player_quest_ids integer[];
        available_quest_ids integer[];
        steam_ids bigint[] := (
            select array_agg(distinct steam_id::bigint) from "PlayerQuests"
        );
        m_steam_id bigint;
        iter int := 1;
    BEGIN
        LOCK TABLE "Quests" IN SHARE MODE;
        --raise notice 'quest ids list: % %', quests, array_length(quests, 1);
        foreach m_steam_id in array steam_ids loop
            player_quest_ids = (
                select array_agg(plq.quest_id::integer)
                from "PlayerQuests" plq where plq.steam_id = m_steam_id
            );
            --raise notice
                'player quests ids % %',
                player_quest_ids,
                array_length(player_quest_ids, 1);
            available_quest_ids = (
                select array_agg(unnest(arr) order by random()) from (
                    select unnest(quests) except select unnest(
                        player_quest_ids
                    )
                ) arr
            );

            --raise notice
                'available quest ids of % are %, len: %',
                m_steam_id,
                available_quest_ids,
                array_length(available_quest_ids, 1);
            iter := 1;
            FOR rec IN (
                SELECT id, steam_id, quest_id, added_at
                FROM "PlayerQuests" plq where plq.steam_id=m_steam_id
            ) LOOP
                --raise notice
                    'available array value: [%] %', iter,
                    available_quest_ids[iter];
                update "PlayerQuests" set
                    quest_id = available_quest_ids[iter],
                    added_at=current_timestamp,
                    progress=0,
                    completed=null
                where id = rec.id;
                iter := iter + 1;
            end loop;
        end loop;
        RETURN TRUE;
    END;
    $$ LANGUAGE PLPGSQL;
""".lstrip()
