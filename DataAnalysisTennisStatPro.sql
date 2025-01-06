-- List all competitions along with their category name
-- Count the number of competitions in each category
-- Find all competitions of type 'doubles'
-- Get competitions that belong to a specific category (e.g., ITF Men)
-- Identify parent competitions and their sub-competitions
-- Analyze the distribution of competition types by category
-- List all competitions with no parent (top-level competitions)

-- Categories Table
-- Competitions Table
-- 1st query
select comp.competition_id, comp.competition_name,comp.parent_id,comp.type,comp.gender,comp.category_id,cat.category_name
from Competitions comp Left join Categories cat on comp.category_id=cat.category_id;
-- 2nd query

select cat.category_name,count( comp.competition_id) as CompetitionCount
from Competitions comp Left join Categories cat on comp.category_id=cat.category_id
group by cat.category_name;

-- 3rd Query
select * from Competitions where type='doubles';

-- 4th query 

select comp.competition_id, comp.competition_name,comp.parent_id,comp.type,comp.gender,comp.category_id,cat.category_name
from Competitions comp Left join Categories cat on comp.category_id=cat.category_id
where cat.category_name='ITF Men';
-- 5th query
SELECT 
    parent.competition_id AS ParentCompetitionID,
    parent.competition_name AS ParentCompetitionName,
    child.competition_id AS SubCompetitionID,
    child.competition_name AS SubCompetitionName
FROM 
    competitions parent
LEFT JOIN 
    competitions child
ON 
    parent.competition_id = child.parent_id;

-- 6th query 

SELECT cat.category_name  as CategoryName, comp.type as Type, COUNT(*) AS CompetitionCount
FROM Competitions comp
LEFT JOIN Categories cat 
    ON comp.category_id = cat.category_id
GROUP BY cat.category_name, comp.type;

-- 7th query
select * from Competitions where parent_id is null;

#-------------------------------------------------------------------------------------------------


-- Execute the following SQL queries:
-- List all venues along with their associated complex name
-- Count the number of venues in each complex
-- Get details of venues in a specific country (e.g., Chile)
-- Identify all venues and their timezones
-- Find complexes that have more than one venue
-- List venues grouped by country
-- Find all venues for a specific complex (e.g., Nacional)
#1)
	select v.venue_id, v.venue_name, v.city_name, v.country_name, v.country_code, v.timezone, c.complex_id, c.complex_name 
	from Venues v LEFT JOIN  Complexes c 
	ON v.complex_id=c.complex_id;

#2)
 select complex_name, count(*) as VenuesCount 
 from Venues v left join  Complexes c 
 ON v.complex_id=c.complex_id group by complex_name;
 
 #3)
select * from Venues where country_name='Chile';

#4)
select venue_name,timezone from  Venues;


#5)
select complex_name, count(*) as VenuesCount 
 from Venues v left join  Complexes c 
 ON v.complex_id=c.complex_id group by complex_name having count(*)>=2 ;
 
 #6)
 
SELECT country_code, country_name, venue_name,timezone,city_name
FROM Venues
ORDER BY country_code, country_name, venue_name; 

#7)
select *
from Venues v LEFT JOIN  Complexes c 
ON v.complex_id=c.complex_id
where c.complex_name='Nacional';


#----------------------------------------------------------------------------------
-- Execute the following SQL queries:
-- Get all competitors with their rank and points.
-- Find competitors ranked in the top 5
-- List competitors with no rank movement (stable rank)
-- Get the total points of competitors from a specific country (e.g., Croatia)
-- Count the number of competitors per country
-- Find competitors with the highest points in the current week

 #1)
 select  c.competitor_id, c.name, c.country, c.country_code, c.abbreviation,  cr.rank, cr.points 
 from Competitors c left join Competitor_Rankings cr 
 on c.competitor_id=cr.competitor_id;

#2)
 select  distinct c.competitor_id, c.name, c.country, c.country_code, c.abbreviation,  cr.rank, cr.points 
 from Competitors c left join Competitor_Rankings cr 
 on c.competitor_id=cr.competitor_id order by cr.rank asc limit 5; 
	
 #3)
 
 select  c.competitor_id, c.name, c.country, c.country_code, c.abbreviation,  cr.rank, cr.points,cr.movement
 from Competitors c left join  Competitor_Rankings cr 
 on c.competitor_id=cr.competitor_id
 where cr.movement=0;
 
 #4) 
 select c.competitor_id, c.name, c.country,sum(cr.points) as TotalPoints
from Competitors c left join  Competitor_Rankings cr 
 on c.competitor_id=cr.competitor_id
 group by c.competitor_id, c.name, c.country having c.country='Croatia';
 
 #5)
 select country,count(*) from Competitors group by country;
 
 #6)
 select c.competitor_id, c.name, c.country, c.country_code, c.abbreviation, cr.rank, cr.points 
from Competitors c left join Competitor_Rankings cr 
on c.competitor_id=cr.competitor_id
order by cr.points desc limit 1;


 
 
