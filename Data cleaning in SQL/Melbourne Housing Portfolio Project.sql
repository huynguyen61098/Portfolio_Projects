	/*
	Melbourne Housing Data Cleaning and Exploration
	
	Skills used: Join, CTE's, Temp Table, Window Function, Aggregation Function, Creating Views, Converting Data Types
	
	The data source: https://www.kaggle.com/dansbecker/melbourne-housing-snapshot

	*/


	Select *
	from Portfolio_Project..melb_data



	-- Standardize Date format
	SELECT Date, CONVERT(Date, Date) 
	FROM Portfolio_Project..melb_data

	ALTER TABLE melb_data
	ADD SoldDate Date
	UPDATE melb_data 
	SET SoldDate = CONVERT(Date, Date)




	--Extract Address's names for later purpose
	SELECT PARSENAME(REPLACE(Address,' ','.'),LEN())
	FROM Portfolio_Project..melb_data

	SELECT SUBSTRING(Address,CHARINDEX(' ',Address)+1,LEN(Address))
	FROM Portfolio_Project..melb_data

	ALTER TABLE melb_data
	ADD Truncated_Address Nvarchar(255)
	
	UPDATE melb_data
	SET Truncated_Address = SUBSTRING(Address,CHARINDEX(' ',Address)+1,LEN(Address))




	-- Change Type and Method to a more human-readable form
	SELECT DISTINCT(Type), COUNNT(Type) 
	FROM (SELECT 
	CASE WHEN Type = 'h' THEN 'House'
	WHEN Type = 'u' THEN 'Unit'
	ELSE 'TownHouse'
	END as Type  
	FROM Portfolio_Project..melb_data) AS tempData 
	GROUP BY Type

	UPDATE melb_data
	SET Type = CASE WHEN Type = 'h' THEN 'House'
	WHEN Type = 'u' THEN 'Unit'
	ELSE 'TownHouse'
	END

	SELECT DISTINCT(Type),COUNT(Type) 
	FROM Portfolio_Project..melb_data
	GROUP BY Type
	SELECT * from Portfolio_Project..melb_data

	UPDATE melb_data
	SET Method = CASE WHEN Method ='S' THEN 'Property sold'
	WHEN Method = 'SP' THEN 'Property sold prior'
	WHEN Method = 'PI' THEN 'Property passed in'
	WHEN Method = 'VB' THEN 'vendor bid'
	ELSE 'Sold after auction'
	END

	SELECT DISTINCT(Method), COUNT(Method) 
	FROM Portfolio_Project..melb_data
	GROUP BY Method
	
	SELECT * 
	FROM Portfolio_Project..melb_data




	-- Remove duplicate
	WITH RowNumCTE AS(
	SELECT *, ROW_NUMBER() OVER(PARTITION BY Suburb, Address,Price,Date, Lattitude, Longtitude ORDER BY Suburb) row_num 
	FROM Portfolio_Project..melb_data)
	DELETE  FROM RowNumCTE
	WHERE row_num >1

	


	-- Populate some null Council's names
	SELECT COUNT(*) FROM Portfolio_Project..melb_data
	WHERE CouncilArea IS NULL

	SELECT a.Suburb, a.Truncated_Address,a.CouncilArea, b.Suburb, b.Truncated_Address, b.CouncilArea,ISNULL(a.CouncilArea, b.CouncilArea)
	FROM Portfolio_Project..melb_data a
	JOIN Portfolio_Project..melb_data b
	ON a.Suburb = b.Suburb
	AND a.Truncated_Address = b.Truncated_Address
	WHERE a.CouncilArea IS NULL

	UPDATE a 
	SET CouncilArea = ISNULL(a.CouncilArea, b.CouncilArea)
	FROM Portfolio_Project..melb_data a
	JOIN Portfolio_Project..melb_data b
	ON a.Suburb = b.Suburb
	AND a.Truncated_Address = b.Truncated_Address
	WHERE a.CouncilArea IS NULL




	-- Delete Unused Columns 
	ALTER TABLE Portfolio_Project..melb_data
	DROP COLUMN Date




	--Add new column for better usage of YearBuilt
	ALTER TABLE melb_data
	ADD BuildingAges int 
	UPDATE melb_data
	SET BuildingAges = 2021 - YearBuilt




	--Data Exploration
	SELECT * 
	FROM Portfolio_Project..melb_data




	-- Select Data that we are going to be start with
	SELECT Suburb,Truncated_Address, Rooms, Type, Price, Distance, Bedroom2, Bathroom, BuildingArea, Regionname, BuildingAges
	FROM Portfolio_Project..melb_data




	-- top 1000 Housing prices
	SELECT TOP 1000 Price 
	FROM Portfolio_Project..melb_data
	ORDER BY Price DESC
 



	-- Min price by number of rooms
	SELECT  DISTINCT(Rooms), MIN(Price)
	FROM Portfolio_Project..melb_data
	GROUP BY Rooms
	ORDER BY 1 DESC,2 DESC




	--Average number of rooms by their housing's type
	SELECT DISTINCT(Type), ROUND(AVG(Rooms),0) As AverageRoomsByType
	FROM Portfolio_Project..melb_data
	GROUP BY Type




	--Average Distance to the Metro's Central Business District by Suburb
	SELECT DISTINCT(Suburb), AVG(Distance) 
	FROM Portfolio_Project..melb_data
	GROUP BY Suburb
	ORDER BY 2 DESC




	-- Do old buildings cost less than new buildings?
	SELECT BuildingAges,Price
	FROM Portfolio_Project..melb_data
	WHERE BuildingAges is Not NULL
	ORDER BY Price DESC




	-- Which Region have the highest average housing'price?
	SELECT Regionname, AVG(price)
	FROM Portfolio_Project..melb_data
	GROUP BY Regionname

	


	--Compare Housing'prices with their area's average prices
	SELECT Regionname,Suburb, Truncated_Address, Price, AVG(Price) OVER(PARTITION BY Regionname, Suburb, Truncated_Address ORDER BY Regionname) as AreaAvgPrice
	FROM Portfolio_Project..melb_data
	ORDER BY 1, 2, 3, 4 DESC

	-- Here's another way. I using Temp Table here for example purpose only 
	DROP TABLE if EXISTS #PriceByArea
	CREATE TABLE #PriceByArea
	(RegionName nvarchar(255),
	SubUrb nvarchar(255),
	Truncated_Address nvarchar(255),
	Price float,
	AreaAvgPrice float)

	INSERT INTO #PriceByArea
	SELECT Regionname,Suburb, Truncated_Address, Price, AVG(Price) OVER(PARTITION BY Regionname, Suburb, Truncated_Address ORDER BY Regionname) as AreaAvgPrice
	FROM Portfolio_Project..melb_data

	SELECT * 
	FROM #PriceByArea
	ORDER BY 1, 2, 3, 4 DESC




	--Create a view of top 10 Suburbs with the highest number of Properties for later visualizations
	CREATE VIEW TOP10PropertyCountBySuburb AS 
	SELECT  TOP(10) Suburb,Regionname, Max(Propertycount) as MaxPropertyCount
	FROM Portfolio_Project..melb_data
	GROUP BY Regionname, Suburb
	ORDER BY 3 DESC
	



	--Housing's Type, area and their minimum number of bedrooms, bathrooms
	SELECT Type, BuildingArea, MIN(Bedroom2) as MinBedroom, MIN(Bathroom) as MinBathroom
	FROM Portfolio_Project..melb_data
	WHERE BuildingArea is NOT NULL
	GROUP BY Type, BuildingArea
	ORDER BY 1,2 DESC, 3 DESC, 4 DESC

	
